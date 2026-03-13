from robots.base.base_runtime import BaseRuntime
from robots.Unitree.Go2.runners.env_builder import Go2EnvBuilder
from robots.Unitree.Go2.runners.policy_loader import Go2PolicyLoader
from robots.Unitree.Go2.runners.exporter import Go2PolicyExporter


class Go2Runtime(BaseRuntime):
    """
    Go2 运行时组装器

    职责：
    - 统一组装 env / runner / policy / exporter
    - 对外提供 build() 接口，返回 env, policy

    配置依赖：
    cfg.task_name
    cfg.agent_cfg_path
    cfg.models_root
    cfg.export_policy
    """

    def __init__(self, env_cfg, cfg):
        self.env_cfg = env_cfg
        self.cfg = cfg

        self.env_builder = None
        self.policy_loader = None
        self.exporter = None

        self.env = None
        self.policy = None
        self.policy_nn = None
        self.obs_normalizer = None
        self.model_path = None

    def _get_task_name(self) -> str:
        task_name = getattr(self.cfg, "task_name", None)
        if not task_name:
            raise ValueError("cfg.task_name is required.")
        return task_name

    def _get_models_root(self) -> str:
        return getattr(self.cfg, "models_root", "models")

    def _get_export_flag(self) -> bool:
        return bool(getattr(self.cfg, "export_policy", True))

    def build_env(self):
        """
        构建环境
        """
        self.policy_loader = Go2PolicyLoader(
            agent_cfg_path=self.cfg.agent_cfg_path,
            models_root=self._get_models_root(),
        )
        agent_cfg = self.policy_loader.load_agent_cfg()

        self.env_builder = Go2EnvBuilder(
            task_name=self._get_task_name(),
            clip_actions=agent_cfg.clip_actions,
        )
        self.env = self.env_builder.build(self.env_cfg)
        return self.env

    def build_policy(self):
        """
        构建并加载策略
        """
        if self.env is None:
            self.build_env()

        self.policy_loader.build_runner(self.env)
        self.model_path = self.policy_loader.load_checkpoint()

        self.policy = self.policy_loader.get_inference_policy(self.env)
        self.policy_nn = self.policy_loader.get_policy_nn()
        self.obs_normalizer = self.policy_loader.get_obs_normalizer()

        return self.policy

    def export_policy_if_needed(self):
        """
        按配置决定是否导出策略
        """
        if not self._get_export_flag():
            return None

        if self.policy_nn is None or self.obs_normalizer is None or self.model_path is None:
            raise RuntimeError("Policy is not ready. Call build_policy() first.")

        self.exporter = Go2PolicyExporter(self.model_path)
        export_dir = self.exporter.export_all(
            policy_nn=self.policy_nn,
            obs_normalizer=self.obs_normalizer,
        )
        return export_dir

    def build(self):
        """
        构建完整 runtime
        返回：
            env, policy
        """
        self.build_env()
        self.build_policy()
        self.export_policy_if_needed()
        return self.env, self.policy