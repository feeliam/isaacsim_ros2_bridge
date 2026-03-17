from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper


class Go2EnvAdapter:
    """
    Go2 环境适配器

    职责：
    - 将原始 env 适配为 RSL-RL 所需格式
    """

    @staticmethod
    def wrap_for_rsl_rl(env, clip_actions):
        return RslRlVecEnvWrapper(env, clip_actions=clip_actions)