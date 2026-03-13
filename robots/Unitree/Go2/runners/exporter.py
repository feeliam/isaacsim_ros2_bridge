import os
from isaaclab_rl.rsl_rl import export_policy_as_jit, export_policy_as_onnx


class Go2PolicyExporter:
    """
    Go2 策略导出器

    职责：
    - 导出 JIT
    - 导出 ONNX
    """

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.export_dir = os.path.join(os.path.dirname(self.model_path), "exported")

    def ensure_export_dir(self):
        os.makedirs(self.export_dir, exist_ok=True)

    def export_jit(self, policy_nn, obs_normalizer, filename: str = "policy.pt"):
        self.ensure_export_dir()
        export_policy_as_jit(
            policy_nn,
            obs_normalizer,
            path=self.export_dir,
            filename=filename,
        )

    def export_onnx(self, policy_nn, obs_normalizer, filename: str = "policy.onnx"):
        self.ensure_export_dir()
        export_policy_as_onnx(
            policy_nn,
            normalizer=obs_normalizer,
            path=self.export_dir,
            filename=filename,
        )

    def export_all(
        self,
        policy_nn,
        obs_normalizer,
        jit_filename: str = "policy.pt",
        onnx_filename: str = "policy.onnx",
    ):
        self.export_jit(policy_nn, obs_normalizer, filename=jit_filename)
        self.export_onnx(policy_nn, obs_normalizer, filename=onnx_filename)
        return self.export_dir