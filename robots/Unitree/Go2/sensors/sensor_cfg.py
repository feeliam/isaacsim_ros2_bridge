from dataclasses import dataclass, field

from robots.base.base_types import CameraMountCfg, LidarMountCfg


@dataclass
class Go2SensorParam:
    """
    Go2 传感器参数配置
    """
    camera: CameraMountCfg = field(default_factory=CameraMountCfg)
    lidar: LidarMountCfg = field(default_factory=LidarMountCfg)