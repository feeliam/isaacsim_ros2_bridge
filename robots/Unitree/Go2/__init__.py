from robots.registry.robot_registry import RobotRegistry
from robots.Unitree.Go2.robot_cfg import build_go2_robot_spec

RobotRegistry.register(build_go2_robot_spec())