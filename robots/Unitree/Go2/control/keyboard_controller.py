from isaaclab.devices import Se2Keyboard, Se2KeyboardCfg

from robots.base.base_controller import BaseVelocityController


class Go2KeyboardController(BaseVelocityController):
    """
    Go2 键盘速度控制器
    - 仅支持单环境控制（num_envs == 1）
    - 输出格式:
        [num_envs, 3] -> [lin_x, lin_y, ang_z]
    """

    def __init__(self, num_envs: int):
        super().__init__(num_envs=num_envs)

        if num_envs != 1:
            raise ValueError(
                f"Go2KeyboardController only supports num_envs == 1, but got num_envs={num_envs}"
            )

        self.keyboard = Se2Keyboard(Se2KeyboardCfg())

    def update(self) -> None:
        """
        更新速度指令
        """
        if self.keyboard is None:
            return

        # advance() 返回 [lin_x, lin_y, ang_z]
        vels = self.keyboard.advance()
        self.command_buffer[0, 0] = float(vels[0])
        self.command_buffer[0, 1] = float(vels[1])
        self.command_buffer[0, 2] = float(vels[2])