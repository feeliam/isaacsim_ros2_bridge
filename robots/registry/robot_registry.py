from typing import Dict
from robots.base.base_robot_cfg import RobotSpec


class RobotRegistry:
    _registry: Dict[str, RobotSpec] = {}

    @classmethod
    def register(cls, robot_spec: RobotSpec):
        cls._registry[robot_spec.meta.name] = robot_spec

    @classmethod
    def get(cls, name: str) -> RobotSpec:
        if name not in cls._registry:
            raise KeyError(f"Robot '{name}' is not registered.")
        return cls._registry[name]

    @classmethod
    def list_all(cls):
        return list(cls._registry.keys())