from typing import Optional
import torch

from robots.Unitree.Go2.control.keyboard_controller import Go2KeyboardController
from robots.Unitree.Go2.control.twist_controller import Go2TwistController


class Go2CommandManager:
    """
    Go2 速度命令管理器

    负责统一管理不同命令源:
    - keyboard
    - twist
    后续还可扩展:
    - ros2_cmd_vel
    - joystick
    - scripted
    """

    SUPPORTED_MODES = ("keyboard", "twist")

    def __init__(self, num_envs: int, mode: str = "keyboard"):
        if mode not in self.SUPPORTED_MODES:
            raise ValueError(f"Unsupported mode '{mode}'")

        if mode == "keyboard" and num_envs != 1:
            raise ValueError(
                f"keyboard mode only supports num_envs == 1, but got num_envs={num_envs}"
            )

        self.num_envs = num_envs
        self.mode = mode

        self.keyboard_controller = Go2KeyboardController(num_envs=num_envs) if num_envs == 1 else None
        self.twist_controller = Go2TwistController(num_envs=num_envs)

    def switch_mode(self, mode: str) -> None:
        if mode not in self.SUPPORTED_MODES:
            raise ValueError(
                f"Unsupported mode '{mode}', expected one of {self.SUPPORTED_MODES}"
            )

        if mode == "keyboard" and self.num_envs != 1:
            raise ValueError(
                f"keyboard mode only supports num_envs == 1, but got num_envs={self.num_envs}"
            )
        # 如果模式没有变化，直接返回，避免不必要的 reset
        if mode == self.mode:
            return
        
        if mode == "twist":
            self.twist_controller.reset()

        self.mode = mode

    def get_active_controller(self):
        if self.mode == "keyboard":
            if self.keyboard_controller is None:
                raise RuntimeError("Keyboard controller is not available.")
            return self.keyboard_controller

        if self.mode == "twist":
            return self.twist_controller

        raise RuntimeError(f"Invalid mode: {self.mode}")

    def get_command(self, device) -> torch.Tensor:
        controller = self.get_active_controller()
        return controller.get_command(device)

    def set_twist_command(self, lin_x: float, lin_y: float, ang_z: float, env_idx: int = 0) -> None:
        self.twist_controller.set_command(lin_x, lin_y, ang_z, env_idx=env_idx)

    def set_twist_command_tensor(self, cmd: torch.Tensor) -> None:
        self.twist_controller.set_command_tensor(cmd)

    def reset_twist_command(self) -> None:
        self.twist_controller.reset()