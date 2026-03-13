import math
import time
from typing import Optional

import torch
import omni
import carb

from simulators.base.base_simulation_runner import BaseSimulationRunner
from simulators.base.runtime_context import RuntimeContext

from simulators.go2.scene_builder import Go2WorkSceneBuilder

from robots.Unitree.Go2.factory.go2_factory import Go2Factory
from robots.Unitree.Go2.sensors.sensor_cfg import Go2SensorParam
from robots.Unitree.Go2.control.control_api import sub_keyboard_event
from robots.Unitree.Go2.control.ros2_twist_bridge import Go2MultiEnvRos2TwistBridgeRunner

import ros2.go2_ros2_bridge as go2_ros2_bridge


class Go2SimulationRunner(BaseSimulationRunner):
    """
    Go2 仿真运行器

    职责：
    - 构建 env_cfg
    - 初始化控制器
    - 创建 runtime（env + policy）
    - 创建传感器
    - 启动 ROS2 Twist Bridge（如果使用 twist 模式）
    - 执行主推理循环
    """

    def __init__(self, cfg, simulation_app):
        """
        cfg : hydra 读取的yaml
        simulation_app : isaaclab.app
        """
        self.cfg = cfg
        self.simulation_app = simulation_app
        self.ctx: Optional[RuntimeContext] = None


    # ========================================================
    #  构建工作场景
    # ========================================================
    def build_work_scene(self):
        Go2WorkSceneBuilder.build(self.cfg.scene_name)


    # ========================================================
    #  配置构建
    # ========================================================

    def build_env_cfg(self):
        """
        仿真环境配置
        """
        env_cfg = Go2Factory.build_env_cfg(num_envs=self.cfg.num_envs)

        control_period = 1.0 / self.cfg.freq
        env_cfg.decimation = math.ceil(control_period / env_cfg.sim.dt)
        env_cfg.sim.render_interval = env_cfg.decimation
        env_cfg.scene.num_envs = self.cfg.num_envs

        return env_cfg

    def build_sensor_param(self) -> Go2SensorParam:
        """
        仿真传感器参数配置
        """
        sensor_param = Go2SensorParam()

        if hasattr(self.cfg, "sensor") and hasattr(self.cfg.sensor, "camera"):
            sensor_param.camera.pos = tuple(self.cfg.sensor.camera.pos)
            sensor_param.camera.rot = tuple(self.cfg.sensor.camera.rot)

        if hasattr(self.cfg, "sensor") and hasattr(self.cfg.sensor, "lidar"):
            sensor_param.lidar.pos = tuple(self.cfg.sensor.lidar.pos)
            sensor_param.lidar.rot = tuple(self.cfg.sensor.lidar.rot)

        return sensor_param

    # ========================================================
    #  控制初始化
    # ========================================================

    def init_control(self):
        """
        控制
        """
        control_mode = self.cfg.control.mode
        Go2Factory.build_controller(num_envs=self.cfg.num_envs, mode=control_mode)

        if control_mode == "keyboard":
            if self.cfg.num_envs != 1:
                raise ValueError(
                    f"keyboard mode only supports num_envs == 1, but got num_envs={self.cfg.num_envs}"
                )

            system_input = carb.input.acquire_input_interface()
            keyboard = omni.appwindow.get_default_app_window().get_keyboard()
            system_input.subscribe_to_keyboard_events(keyboard, sub_keyboard_event)

    def init_twist_bridge(self) -> Optional[Go2MultiEnvRos2TwistBridgeRunner]:
        """
        Ros2 Twist 转化配置
        """
        control_mode = self.cfg.control.mode
        if control_mode != "twist":
            return None

        topic_template = self.cfg.control.topic_template
        runner = Go2MultiEnvRos2TwistBridgeRunner(
            num_envs=self.cfg.num_envs,
            topic_template=topic_template,
        )
        runner.start()
        return runner

    # ========================================================
    #  runtime / sensors / ros2 数据管理
    # ========================================================

    def init_runtime(self, env_cfg):
        """
        仿真本体运行配置 
        """
        env, policy = Go2Factory.build_runtime(env_cfg, self.cfg)
        return env, policy

    def init_sensors(self):
        """
        本体传感器构建
        """
        sensor_param = self.build_sensor_param()
        sensor_mgr = Go2Factory.build_sensors(
            num_envs=self.cfg.num_envs,
            sensor_param=sensor_param,
        )

        lidars = sensor_mgr.create_lidar()
        cameras = sensor_mgr.create_camera()
        return lidars, cameras

    def init_data_manager(self, env, lidars, cameras):
        return go2_ros2_bridge.RobotDataManager(env, lidars, cameras, self.cfg)

    # ========================================================
    #  init
    # ========================================================

    def init(self):
        """
        Go2 仿真初始化入口
         构建runtime 上下文
        """
        # 1. 搭建工作场景
        self.build_work_scene()

        # 2. 构建仿真环境配置
        env_cfg = self.build_env_cfg()

        # 3. 初始化控制
        self.init_control()

        # 4. 初始化运行环境 runtime 
        env, policy = self.init_runtime(env_cfg)

        # 5. 初始化传感器
        lidars, cameras = self.init_sensors()

        # 6. 初始化 twist bridge（如果启用）
        twist_bridge_runner = self.init_twist_bridge()

        # 7. 初始化 ROS2 数据管理器
        data_manager = self.init_data_manager(env, lidars, cameras)

        self.ctx = RuntimeContext(
            env_cfg=env_cfg,
            env=env,
            policy=policy,
            lidars=lidars,
            cameras=cameras,
            data_manager=data_manager,
            twist_bridge_runner=twist_bridge_runner,
        )

    # ========================================================
    #  主循环
    # ========================================================

    def run_loop(self):
        """
        Go2 仿真主循环程序
        """
        if self.ctx is None:
            raise RuntimeError("Runtime context is not initialized. Call init() first.")

        print("[INFO]: simulation started")

        obs, _ = self.ctx.env.reset()
        dt = float(self.ctx.env_cfg.sim.dt * self.ctx.env_cfg.decimation)

        while self.simulation_app.is_running():
            start_time = time.time()

            with torch.inference_mode():
                actions = self.ctx.policy(obs)
                obs, _, _, _ = self.ctx.env.step(actions)

            self.ctx.data_manager.update()

            elapsed_time = time.time() - start_time
            sleep_time = dt - elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)

            actual_loop_time = time.time() - start_time
            rtf = min(1.0, dt / max(elapsed_time, 1e-6))

            print(
                f"\rStep time: {actual_loop_time * 1000:.2f} ms, Real Time Factor: {rtf:.2f}",
                end="",
                flush=True,
            )

    # ========================================================
    #  资源回收
    # ========================================================

    def shutdown(self):
        if self.ctx is not None:
            if self.ctx.twist_bridge_runner is not None:
                self.ctx.twist_bridge_runner.stop()

            if self.ctx.data_manager is not None:
                self.ctx.data_manager.destroy_node()

        self.simulation_app.close()