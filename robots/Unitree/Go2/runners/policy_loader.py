import os
import yaml

from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg
from rsl_rl.runners import OnPolicyRunner
from isaaclab_tasks.utils import get_checkpoint_path


class Go2PolicyLoader:
    """
    Go2 策略加载器

    职责：
    - 读取 agent yaml 配置
    - 创建 OnPolicyRunner
    - 加载 checkpoint
    - 获取推理 policy
    - 获取 policy 网络本体
    """

    def __init__(self, agent_cfg_path: str, models_root: str = "models"):
        self.agent_cfg_path = agent_cfg_path
        self.models_root = models_root

        self.agent_cfg = None
        self.runner = None
        self.model_path = None

    def load_agent_cfg(self) -> RslRlOnPolicyRunnerCfg:
        with open(self.agent_cfg_path, "r", encoding="utf-8") as f:
            raw_cfg = yaml.safe_load(f)

        self.agent_cfg = RslRlOnPolicyRunnerCfg(**raw_cfg)
        return self.agent_cfg

    def build_runner(self, env) -> OnPolicyRunner:
        if self.agent_cfg is None:
            self.load_agent_cfg()

        self.runner = OnPolicyRunner(
            env,
            self.agent_cfg.to_dict(),
            log_dir=None,
            device=self.agent_cfg.device,
        )
        return self.runner

    def load_checkpoint(self) -> str:
        if self.runner is None:
            raise RuntimeError("Runner is not built. Call build_runner(env) first.")

        self.model_path = get_checkpoint_path(
            log_path=os.path.abspath(self.models_root),
            run_dir=self.agent_cfg.load_run,
            checkpoint=self.agent_cfg.load_checkpoint,
        )
        self.runner.load(self.model_path)
        return self.model_path

    def get_inference_policy(self, env):
        if self.runner is None:
            raise RuntimeError("Runner is not built. Call build_runner(env) first.")
        return self.runner.get_inference_policy(device=env.unwrapped.device)

    def get_policy_nn(self):
        if self.runner is None:
            raise RuntimeError("Runner is not built. Call build_runner(env) first.")

        try:
            # rsl_rl / isaaclab 新版本
            return self.runner.alg.policy
        except AttributeError:
            # 旧版本兼容
            return self.runner.alg.actor_critic

    def get_obs_normalizer(self):
        if self.runner is None:
            raise RuntimeError("Runner is not built. Call build_runner(env) first.")
        return self.runner.obs_normalizer