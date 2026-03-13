import isaaclab.envs.mdp as mdp
from isaaclab.utils import configclass


@configclass
class Go2VelocityCommandsCfg:
    """
    MDP 命令配置
    当前配置为静止命令环境：
    - lin_vel_x = 0
    - lin_vel_y = 0
    - ang_vel_z = 0
    - heading   = 0
    后续可改成速度采样范围，用于速度跟踪训练。
    """

    velocity_commands = mdp.UniformVelocityCommandCfg(
        asset_name="robot",
        resampling_time_range=(0.0, 0.0),
        debug_vis=True,
        ranges=mdp.UniformVelocityCommandCfg.Ranges(
            lin_vel_x=(0.0, 0.0),
            lin_vel_y=(0.0, 0.0),
            ang_vel_z=(0.0, 0.0),
            heading=(0.0, 0.0),
        ),
    )