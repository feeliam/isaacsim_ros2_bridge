import threading
import torch

from robots.base.base_controller import BaseVelocityController


class Go2TwistController(BaseVelocityController):
    """
    Twist 风格速度控制器

    约定:
        command_buffer[:, 0] -> linear.x
        command_buffer[:, 1] -> linear.y
        command_buffer[:, 2] -> angular.z
    """

    def __init__(self, num_envs: int):
        super().__init__(num_envs=num_envs)
        self._lock = threading.Lock()

    def set_command(self, lin_x: float, lin_y: float, ang_z: float, env_idx: int = 0) -> None:
        if env_idx < 0 or env_idx >= self.num_envs:
            raise IndexError(f"env_idx={env_idx} out of range [0, {self.num_envs})")

        with self._lock:
            self.command_buffer[env_idx, 0] = lin_x
            self.command_buffer[env_idx, 1] = lin_y
            self.command_buffer[env_idx, 2] = ang_z

    def set_command_tensor(self, cmd: torch.Tensor) -> None:
        if cmd.shape != self.command_buffer.shape:
            raise ValueError(
                f"Expected shape {tuple(self.command_buffer.shape)}, got {tuple(cmd.shape)}"
            )

        with self._lock:
            self.command_buffer.copy_(
                cmd.to(dtype=self.command_buffer.dtype, device=self.command_buffer.device)
            )

    def reset(self) -> None:
        with self._lock:
            self.command_buffer.zero_()

    def update(self) -> None:
        return

    def get_command(self, device) -> torch.Tensor:
        with self._lock:
            return self.command_buffer.clone().to(device)