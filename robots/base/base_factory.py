from abc import ABC, abstractmethod


class BaseRobotFactory(ABC):
    """
    机器人统一工厂抽象基类
    - 为不同机器人提供统一对外入口
    """

    @staticmethod
    @abstractmethod
    def build_env_cfg(num_envs: int = 1):
        """
        构建环境配置
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def build_controller(num_envs: int, mode: str = "keyboard"):
        """
        初始化控制器 / 控制管理器
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def build_sensors(num_envs: int, sensor_param=None):
        """
        构建传感器管理器
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def build_runtime(env_cfg, cfg):
        """
        构建 runtime（env + policy）
        """
        raise NotImplementedError