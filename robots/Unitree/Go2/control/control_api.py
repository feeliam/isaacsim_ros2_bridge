import torch
from isaaclab.envs import ManagerBasedEnv

from robots.Unitree.Go2.control.command_manager import Go2CommandManager


_command_manager = None


def init_base_vel_cmd(num_envs: int, mode: str = "keyboard"):
    """
    初始化速度命令管理器

    Args:
        num_envs: 并行环境数
        mode: 控制模式
            - "keyboard"
            - "twist"
    """
    global _command_manager
    _command_manager = Go2CommandManager(num_envs=num_envs, mode=mode)


def get_command_manager() -> Go2CommandManager:
    global _command_manager
    if _command_manager is None:
        raise RuntimeError(
            "Command manager is not initialized. "
            "Please call init_base_vel_cmd(num_envs, mode=...) first."
        )
    return _command_manager


def base_vel_cmd(env: ManagerBasedEnv) -> torch.Tensor:
    """
    Isaac Lab observation 使用的统一速度命令入口
    """
    manager = get_command_manager()
    return manager.get_command(env.device)


def switch_command_mode(mode: str) -> None:
    manager = get_command_manager()
    manager.switch_mode(mode)


def set_twist_command(lin_x: float, lin_y: float, ang_z: float, env_idx: int = 0) -> None:
    manager = get_command_manager()
    manager.set_twist_command(lin_x, lin_y, ang_z, env_idx=env_idx)


def set_twist_command_tensor(cmd: torch.Tensor) -> None:
    manager = get_command_manager()
    manager.set_twist_command_tensor(cmd)


def reset_twist_command() -> None:
    manager = get_command_manager()
    manager.reset_twist_command()


def sub_keyboard_event(event) -> bool:
    """
    预留键盘事件扩展口
    """
    return True