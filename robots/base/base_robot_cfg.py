from dataclasses import dataclass
from typing import Optional, Type

from isaaclab.assets import ArticulationCfg
from robots.base.base_types import RobotMeta


@dataclass
class RobotSpec:
    """
    机器人规格描述：
    - meta: 基础元信息
    - articulation_cfg: 机器人资产配置
    """
    meta: RobotMeta
    articulation_cfg: ArticulationCfg

    # 可选：后续可以继续扩展，把任务/控制/传感器工厂类也挂进来
    controller_cls: Optional[Type] = None
    sensor_manager_cls: Optional[Type] = None