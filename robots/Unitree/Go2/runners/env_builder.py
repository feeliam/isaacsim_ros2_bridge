import gymnasium as gym
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper


class Go2EnvBuilder:
    """
    Go2 环境构建器

    职责：
    - 创建 Isaac Lab gym 环境
    - 包装为 RSL-RL 兼容 vec env
    """

    def __init__(self, task_name: str, clip_actions: float):
        self.task_name = task_name
        self.clip_actions = clip_actions

    def build(self, env_cfg):
        """
        构建环境并包装
        """
        env = gym.make(
            self.task_name,
            cfg=env_cfg,
            render_mode="rgb_array",
        )
        env = RslRlVecEnvWrapper(env, clip_actions=self.clip_actions)
        return env