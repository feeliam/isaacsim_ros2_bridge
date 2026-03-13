import isaaclab.envs.mdp as mdp
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.utils import configclass

from robots.Unitree.Go2.control.control_api import base_vel_cmd


@configclass
class Go2VelocityPolicyObsCfg(ObsGroup):
    """
    policy 看到的观测空间
    """

    # 机体线速度
    base_lin_vel = ObsTerm(
        func=mdp.base_lin_vel,
        params={"asset_cfg": SceneEntityCfg("robot")},
    )

    # 机体角速度
    base_ang_vel = ObsTerm(
        func=mdp.base_ang_vel,
        params={"asset_cfg": SceneEntityCfg("robot")},
    )

    # 投影重力
    projected_gravity = ObsTerm(
        func=mdp.projected_gravity,
        params={"asset_cfg": SceneEntityCfg("robot")},
    )

    # 外部命令输入（键盘 / ROS2 / 其他控制源）
    velocity_commands = ObsTerm(func=base_vel_cmd)

    # 关节相对位置
    joint_pos = ObsTerm(
        func=mdp.joint_pos_rel,
        params={"asset_cfg": SceneEntityCfg("robot")},
    )

    # 关节相对速度
    joint_vel = ObsTerm(
        func=mdp.joint_vel_rel,
        params={"asset_cfg": SceneEntityCfg("robot")},
    )

    # 上一步动作
    actions = ObsTerm(func=mdp.last_action)

    # 高度扫描
    height_scan = ObsTerm(
        func=mdp.height_scan,
        params={"sensor_cfg": SceneEntityCfg("height_scanner")},
        clip=(-1.0, 1.0),
    )

    def __post_init__(self):
        # 是否启用观测噪声/扰动
        self.enable_corruption = False
        # 是否将所有观测项拼接成一个大向量
        self.concatenate_terms = True


@configclass
class Go2VelocityObservationsCfg:
    """
    观测配置入口
    """
    policy: Go2VelocityPolicyObsCfg = Go2VelocityPolicyObsCfg()