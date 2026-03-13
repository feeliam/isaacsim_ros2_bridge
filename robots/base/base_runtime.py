from abc import ABC, abstractmethod


class BaseRuntime(ABC):
    """
    运行时抽象基类

    目标：
    - 为不同机器人/不同运行模式提供统一的 runtime 接口
    - 约束 runtime 至少具备 build() 方法
    - 可按需要扩展为更细粒度的阶段接口

    一个典型 runtime 可能负责：
    - 构建环境
    - 加载策略
    - 导出策略
    - 返回 env 和 policy
    """

    @abstractmethod
    def build_env(self):
        """
        构建运行时环境
        例如：
        - gym env
        - vec env wrapper
        """
        raise NotImplementedError

    @abstractmethod
    def build_policy(self):
        """
        构建/加载策略
        例如：
        - 创建 runner
        - 加载 checkpoint
        - 获取 inference policy
        """
        raise NotImplementedError

    @abstractmethod
    def build(self):
        """
        构建完整 runtime

        推荐返回：
            env, policy
        """
        raise NotImplementedError