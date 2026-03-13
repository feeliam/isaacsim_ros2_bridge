from abc import ABC, abstractmethod


class BaseSimulationRunner(ABC):
    """
    仿真运行器抽象基类

    统一生命周期：
    - init
    - run_loop
    - shutdown
    - run
    """

    @abstractmethod
    def init(self):
        """
        仿真初始化接口
        """
        raise NotImplementedError

    @abstractmethod
    def run_loop(self):
        """
        仿真主循环接口
        """
        raise NotImplementedError

    @abstractmethod
    def shutdown(self):
        """
        仿真结束接口
        """
        raise NotImplementedError

    def run(self):
        """
        启动仿真
         - 1. 仿真初始化
         - 2. 进入仿真循环
         - 3. 退出时资源回收
        """
        try:
            self.init()
            self.run_loop()
        finally:
            self.shutdown()