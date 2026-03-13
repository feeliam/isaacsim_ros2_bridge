from isaaclab_assets.robots.unitree import UNITREE_GO2_CFG

from robots.base.base_robot_cfg import RobotSpec
from robots.base.base_types import RobotMeta


# 这里的  {ENV_REGEX_NS} 会在多环境创建的时候 替换为 /World/envs/env_*.
GO2_META = RobotMeta(
    robot_name="Go2",
    asset_name="robot",
    prim_path="{ENV_REGEX_NS}/Go2",         
    base_link="{ENV_REGEX_NS}/Go2/base",
)


def build_go2_robot_spec() -> RobotSpec:
    """
    仿真中 Go2 的配置构建 
    """
    articulation_cfg = UNITREE_GO2_CFG.replace(prim_path=GO2_META.prim_path)
    return RobotSpec(
        meta=GO2_META,
        articulation_cfg=articulation_cfg,
    )