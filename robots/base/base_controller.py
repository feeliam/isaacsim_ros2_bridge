from abc import ABC, abstractmethod
import torch


class BaseVelocityController(ABC):
    """
    通用底盘速度控制器抽象基类

    约定输出格式：
        [num_envs, 3] -> [lin_x, lin_y, ang_z]

    设计思路：
    - command_buffer 由子类维护
    - update() 由子类决定如何刷新命令
    - get_command() 提供统一读接口
    """

    def __init__(self, num_envs: int):
        if num_envs <= 0:
            raise ValueError(f"num_envs must be positive, but got {num_envs}")

        self.num_envs = num_envs
        self.command_buffer = torch.zeros((num_envs, 3), dtype=torch.float32)

    @abstractmethod
    def update(self) -> None:
        """更新内部 command_buffer"""
        raise NotImplementedError

    def get_command(self, device) -> torch.Tensor:
        """返回发往 env.device 的命令张量"""
        self.update()
        return self.command_buffer.clone().to(device)