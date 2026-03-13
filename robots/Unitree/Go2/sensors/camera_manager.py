from isaaclab.sensors import Camera, CameraCfg
import isaaclab.sim as sim_utils

from robots.Unitree.Go2.robot_cfg import GO2_META


class Go2CameraManager:
    def __init__(self, num_envs: int, sensor_param):
        self.num_envs = num_envs
        self.sensor_param = sensor_param
        self.cameras = []

    def create(self):
        """
        为每个环境创建相机
        """
        self.cameras = []

        for env_idx in range(self.num_envs):
            prim_path = (
                f"/World/envs/env_{env_idx}/{GO2_META.robot_name}/base/"
                f"{self.sensor_param.camera.prim_name}"
            )

            camera_cfg = CameraCfg(
                prim_path=prim_path,
                update_period=self.sensor_param.camera.update_period,
                data_types=list(self.sensor_param.camera.data_types),
                spawn=sim_utils.PinholeCameraCfg(),
                width=self.sensor_param.camera.width,
                height=self.sensor_param.camera.height,
                offset=CameraCfg.OffsetCfg(
                    pos=tuple(self.sensor_param.camera.pos),
                    rot=tuple(self.sensor_param.camera.rot),
                    convention="world",
                ),
            )

            self.cameras.append(Camera(cfg=camera_cfg))

        return self.cameras