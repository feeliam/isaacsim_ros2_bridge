from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors.ray_caster import RayCasterCfg
from isaaclab.sensors.ray_caster import patterns
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.utils import configclass
import isaaclab.sim as sim_utils

from robots.Unitree.Go2.robot_cfg import GO2_META, build_go2_robot_spec
from robots.Unitree.Go2.tasks.velocity.actions import Go2VelocityActionsCfg
from robots.Unitree.Go2.tasks.velocity.commands import Go2VelocityCommandsCfg
from robots.Unitree.Go2.tasks.velocity.curriculum import Go2VelocityCurriculumCfg
from robots.Unitree.Go2.tasks.velocity.events import Go2VelocityEventsCfg
from robots.Unitree.Go2.tasks.velocity.observations import Go2VelocityObservationsCfg
from robots.Unitree.Go2.tasks.velocity.rewards import Go2VelocityRewardsCfg
from robots.Unitree.Go2.tasks.velocity.terminations import Go2VelocityTerminationsCfg


@configclass
class Go2FlatSceneCfg(InteractiveSceneCfg):
    """
    Go2 平地场景配置
    """

    # 地形
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane",
    )

    # 机器人资产
    robot: ArticulationCfg = build_go2_robot_spec().articulation_cfg

    # 高度扫描器（RayCaster）
    height_scanner = RayCasterCfg(
        prim_path=GO2_META.base_link_path,
        update_period=0.02,
        offset=RayCasterCfg.OffsetCfg(pos=(0.0, 0.0, 20.0)),
        ray_alignment="yaw",
        pattern_cfg=patterns.GridPatternCfg(
            resolution=0.1,
            size=(1.6, 1.0),
        ),
        debug_vis=True,
        mesh_prim_paths=["/World/ground"],
    )

    # 灯光
    light = AssetBaseCfg(
        prim_path="/World/light",
        spawn=sim_utils.DistantLightCfg(intensity=1000.0),
    )


@configclass
class Go2VelocityEnvCfg(ManagerBasedRLEnvCfg):
    """
    Go2 速度任务 RL 环境配置
     必须项：
        - 场景配置 Scene
        - MDP 配置
        - 训练相关配置
    """

    # 场景配置
    scene: Go2FlatSceneCfg = Go2FlatSceneCfg(
        num_envs=2,
        env_spacing=2.5,
    )

    # MDP 配置
    observations: Go2VelocityObservationsCfg = Go2VelocityObservationsCfg()
    actions: Go2VelocityActionsCfg = Go2VelocityActionsCfg()
    commands: Go2VelocityCommandsCfg = Go2VelocityCommandsCfg()

    # 训练相关配置
    events: Go2VelocityEventsCfg = Go2VelocityEventsCfg()
    rewards: Go2VelocityRewardsCfg = Go2VelocityRewardsCfg()
    terminations: Go2VelocityTerminationsCfg = Go2VelocityTerminationsCfg()
    curriculum: Go2VelocityCurriculumCfg = Go2VelocityCurriculumCfg()

    def __post_init__(self):
        """Post initialization."""

        # viewer 参数
        self.viewer.eye = [-4.0, 0.0, 2.0]
        self.viewer.lookat = [0.5, 0.5, 0.0]

        # 环境参数
        self.decimation = 8
        self.episode_length_s = 20.0
        self.is_finite_horizon = False

        # 动作缩放
        self.actions.joint_pos.scale = 0.25

        # 仿真参数
        self.sim.dt = 0.005
        self.sim.render_interval = self.decimation
        self.sim.render.antialiasing_mode = None

        # 同步高度扫描器更新频率
        if self.scene.height_scanner is not None:
            self.scene.height_scanner.update_period = self.decimation * self.sim.dt