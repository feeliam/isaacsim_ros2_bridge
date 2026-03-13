import omni
from pxr import Gf

from robots.Unitree.Go2.robot_cfg import GO2_META


class Go2LidarManager:
    def __init__(self, num_envs: int, sensor_param):
        self.num_envs = num_envs
        self.sensor_param = sensor_param
        self.lidars = []

    def create(self):
        """
        为每个环境创建 RTX 激光雷达
        """
        self.lidars = []

        sensor_attributes = {
            "omni:sensor:Core:scanRateBaseHz": self.sensor_param.lidar.update_rate_hz
        }

        for env_idx in range(self.num_envs):
            parent_path = f"/World/envs/env_{env_idx}/{GO2_META.robot_name}/base"

            _, sensor = omni.kit.commands.execute(
                "IsaacSensorCreateRtxLidar",
                translation=Gf.Vec3d(*self.sensor_param.lidar.pos),
                orientation=Gf.Quatd(*self.sensor_param.lidar.rot),
                path=self.sensor_param.lidar.prim_name,
                parent=parent_path,
                config=self.sensor_param.lidar.preset,
                **sensor_attributes,
            )

            self.lidars.append(sensor)

        return self.lidars