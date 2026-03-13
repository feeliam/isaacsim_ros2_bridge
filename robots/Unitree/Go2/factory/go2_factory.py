from robots.base.base_factory import BaseRobotFactory
from robots.Unitree.Go2.control.control_api import init_base_vel_cmd
from robots.Unitree.Go2.sensors.sensor_cfg import Go2SensorParam
from robots.Unitree.Go2.sensors.sensor_manager import Go2SensorManager
from robots.Unitree.Go2.tasks.velocity.env_cfg import Go2VelocityEnvCfg
from robots.Unitree.Go2.runners.runtime import Go2Runtime


class Go2Factory(BaseRobotFactory):
    """
    Go2 统一工厂

    职责：
    - 构建 env cfg
    - 构建 控制器
    - 构建 传感器管理器
    - 构建 runtime（env + policy）
    """

    @staticmethod
    def build_env_cfg(num_envs: int = 1):
        env_cfg = Go2VelocityEnvCfg()
        env_cfg.scene.num_envs = num_envs
        return env_cfg

    @staticmethod
    def build_controller(num_envs: int, mode: str = "keyboard"):
        init_base_vel_cmd(num_envs=num_envs, mode=mode)

    @staticmethod
    def build_sensors(num_envs: int, sensor_param: Go2SensorParam | None = None):
        return Go2SensorManager(num_envs=num_envs, sensor_param=sensor_param)

    @staticmethod
    def build_runtime(env_cfg, cfg):
        runtime = Go2Runtime(env_cfg=env_cfg, cfg=cfg)
        return runtime.build()