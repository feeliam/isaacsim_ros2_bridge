import gymnasium as gym


class Go2EnvBuilder:
    """
    Go2 原始环境构建器

    职责：
    - 创建 Isaac Lab gym 环境
    不负责 RL 框架包装
    """

    def __init__(self, task_name: str, render_mode: str = "rgb_array"):
        self.task_name = task_name
        self.render_mode = render_mode

    def build(self, env_cfg):
        return gym.make(
            self.task_name,
            cfg=env_cfg,
            render_mode=self.render_mode,
        )