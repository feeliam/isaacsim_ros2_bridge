from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class RobotMeta:
    """
    机器人元信息
    """
    robot_name: str
    asset_name: str
    prim_path: str
    base_link: str

@dataclass
class CameraMountCfg:
    """相机挂载参数"""
    prim_name: str = "front_cam"
    width: int = 640
    height: int = 480
    data_types: Tuple[str, ...] = ("rgb", "depth")
    update_period: float = 0.0
    pos: Tuple[float, float, float] = (0.5, 0.0, 0.1)
    rot: Tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0)


@dataclass
class LidarMountCfg:
    """激光雷达挂载参数"""
    prim_name: str = "lidar"
    update_rate_hz: int = 20
    preset: str = "Example_Rotatory"
    pos: Tuple[float, float, float] = (0.0, 0.0, 0.2)
    rot: Tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0)