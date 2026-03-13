from isaaclab.utils import configclass


@configclass
class Go2VelocityRewardsCfg:
    """
    奖励配置

    当前先留空。
    后续可逐步加入：
    - 速度跟踪奖励
    - 姿态稳定奖励
    - 足端接触奖励
    - 动作平滑惩罚
    - 能耗惩罚
    """
    pass