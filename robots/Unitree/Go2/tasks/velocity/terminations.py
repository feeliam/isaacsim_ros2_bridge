from isaaclab.utils import configclass


@configclass
class Go2VelocityTerminationsCfg:
    """
    终止配置

    当前先留空。
    后续可逐步加入：
    - 跌倒终止
    - 姿态越界终止
    - 超时终止
    - 越界终止
    """
    pass