"""
run_sim.py

统一仿真启动入口：
- 启动 Isaac Sim App
- 启用 ROS2 Bridge 扩展
- 加载 Hydra 配置
- 选择并运行对应 SimulationRunner
"""

import os
import argparse

import hydra
from isaaclab.app import AppLauncher


# ============================================================
# 1. App 启动参数
# ============================================================

parser = argparse.ArgumentParser(description="Simulation Launcher")
AppLauncher.add_app_launcher_args(parser)

args_cli = parser.parse_args()
args_cli.enable_cameras = True
args_cli.kit_args = "--/renderer/multiGpu/enabled=true --/renderer/multiGpu/maxGpuCount=2"

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app


# ============================================================
# 2. 启用 Isaac Sim ROS2 Bridge 扩展
# ============================================================

import omni.kit.app

ext_manager = omni.kit.app.get_app().get_extension_manager()
ext_manager.set_extension_enabled_immediate("isaacsim.ros2.bridge", True)


# ============================================================
# 3. Runner 选择
# 当前先直接使用 Go2，后面可以扩展成配置驱动
# ============================================================

from simulators.go2.runner import Go2SimulationRunner


FILE_PATH = os.path.join(os.path.dirname(__file__), "config")


@hydra.main(config_path=FILE_PATH, config_name="sim", version_base=None)
def main(cfg):
    runner = Go2SimulationRunner(cfg=cfg, simulation_app=simulation_app)
    runner.run()


if __name__ == "__main__":
    main()