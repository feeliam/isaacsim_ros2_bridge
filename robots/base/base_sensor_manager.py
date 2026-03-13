from abc import ABC, abstractmethod


class BaseSensorManager(ABC):
    """
    通用传感器管理器抽象基类

    约定：
    - 子类负责实现具体相机/雷达创建逻辑
    - create_all() 提供统一聚合接口
    """

    @abstractmethod
    def create_camera(self):
        """
        创建相机
        """
        raise NotImplementedError

    @abstractmethod
    def create_lidar(self):
        """
        创建激光雷达
        """
        raise NotImplementedError

    def create_all(self):
        """
        一次性创建所有传感器
        """
        return {
            "cameras": self.create_camera(),
            "lidars": self.create_lidar(),
        }