import os
import yaml

from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg
from rsl_rl.runners import OnPolicyRunner
from isaaclab_tasks.utils import get_checkpoint_path


class Go2PolicyLoader:
    """
    Go2 策略加载器

    职责：
    - 加载 agent 配置
    - 创建 runner
    - 加载 checkpoint
    - 获取 inference policy
    - 暴露 policy_nn / obs_normalizer
    """

    def __init__(self, agent_cfg_path: str, models_root: str = "models"):
        self.agent_cfg_path = agent_cfg_path
        self.models_root = models_root

        self.agent_cfg = None
        self.runner = None
        self.model_path = None

    def load_agent_cfg(self) -> RslRlOnPolicyRunnerCfg:
        if self.agent_cfg is not None:
            return self.agent_cfg

        with open(self.agent_cfg_path, "r", encoding="utf-8") as f:
            raw_cfg = yaml.safe_load(f)

        self.agent_cfg = RslRlOnPolicyRunnerCfg(**raw_cfg)
        return self.agent_cfg

    def build_runner(self, env) -> OnPolicyRunner:
        agent_cfg = self.load_agent_cfg()

        self.runner = OnPolicyRunner(
            env,
            agent_cfg.to_dict(),
            log_dir=None,
            device=agent_cfg.device,
        )
        return self.runner

    def resolve_checkpoint_path(self) -> str:
        agent_cfg = self.load_agent_cfg()

        self.model_path = get_checkpoint_path(
            log_path=os.path.abspath(self.models_root),
            run_dir=agent_cfg.load_run,
            checkpoint=agent_cfg.load_checkpoint,
        )
        return self.model_path

    def load_checkpoint(self) -> str:
        if self.runner is None:
            raise RuntimeError("Runner is not built. Call build_runner(env) first.")

        model_path = self.resolve_checkpoint_path()
        self.runner.load(model_path)
        return model_path

    def get_inference_policy(self, device):
        if self.runner is None:
            raise RuntimeError("Runner is not built. Call build_runner(env) first.")
        return self.runner.get_inference_policy(device=device)

    def get_policy_nn(self):
        if self.runner is None:
            raise RuntimeError("Runner is not built. Call build_runner(env) first.")

        try:
            return self.runner.alg.policy
        except AttributeError:
            return self.runner.alg.actor_critic

    def get_obs_normalizer(self):
        if self.runner is None:
            raise RuntimeError("Runner is not built. Call build_runner(env) first.")
        return self.runner.obs_normalizer