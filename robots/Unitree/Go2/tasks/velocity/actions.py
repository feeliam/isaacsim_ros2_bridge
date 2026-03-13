import isaaclab.envs.mdp as mdp
from isaaclab.utils import configclass


@configclass
class Go2VelocityActionsCfg:
    """
    动作配置
    使用关节位置控制：
    - joint_names=[".*"] 表示匹配所有关节
    - scale 控制策略输出动作的缩放幅度
    - use_default_offset=True 表示在默认关节位置上叠加动作偏移
    """

    joint_pos = mdp.JointPositionActionCfg(
        asset_name="robot",
        joint_names=[".*"],
        scale=0.25,
        use_default_offset=True,
    )