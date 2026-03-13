from dataclasses import dataclass
from typing import Optional


@dataclass
class RuntimeContext:
    """
    运行期上下文对象
    用于集中保存运行过程中的关键资源
    """

    env_cfg: object
    env: object
    policy: object
    lidars: list
    cameras: list
    data_manager: object
    twist_bridge_runner: Optional[object] = None