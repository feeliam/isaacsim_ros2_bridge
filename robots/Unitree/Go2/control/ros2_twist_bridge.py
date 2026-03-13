import threading
from functools import partial
from typing import Optional

import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from robots.Unitree.Go2.control.control_api import get_command_manager, switch_command_mode


class Go2MultiEnvRos2TwistBridge(Node):
    """
    多环境 ROS2 Twist 桥接节点

    每个环境一个 topic，例如：
        /env_0/cmd_vel
        /env_1/cmd_vel
        /env_2/cmd_vel
    或者：
        /env_0/unitree_go2/cmd_vel
        /env_1/unitree_go2/cmd_vel
    """

    def __init__(
        self,
        num_envs: int,
        topic_template: str = "/env_{env_idx}/cmd_vel",
        node_name: str = "go2_multi_env_ros2_twist_bridge",
        force_twist_mode: bool = True,
        qos_depth: int = 10,
    ):
        super().__init__(node_name)

        if num_envs <= 0:
            raise ValueError(f"num_envs must be positive, but got {num_envs}")

        self.num_envs = num_envs
        self.topic_template = topic_template
        self.qos_depth = qos_depth
        self.subscriptions = []

        if force_twist_mode:
            switch_command_mode("twist")

        self._create_subscribers()

        self.get_logger().info(
            f"Go2MultiEnvRos2TwistBridge started with num_envs={self.num_envs}"
        )

    def _create_subscribers(self) -> None:
        for env_idx in range(self.num_envs):
            topic_name = self.topic_template.format(env_idx=env_idx)

            sub = self.create_subscription(
                Twist,
                topic_name,
                partial(self._twist_callback, env_idx=env_idx),
                self.qos_depth,
            )
            self.subscriptions.append(sub)

            self.get_logger().info(
                f"Subscribed topic for env_{env_idx}: {topic_name}"
            )

    def _twist_callback(self, msg: Twist, env_idx: int) -> None:
        try:
            manager = get_command_manager()
            manager.set_twist_command(
                lin_x=float(msg.linear.x),
                lin_y=float(msg.linear.y),
                ang_z=float(msg.angular.z),
                env_idx=env_idx,
            )
        except Exception as e:
            self.get_logger().error(
                f"Failed to handle Twist for env_{env_idx}: {e}"
            )


class Go2MultiEnvRos2TwistBridgeRunner:
    """
    后台运行多环境 ROS2 Twist bridge
    """

    def __init__(
        self,
        num_envs: int,
        topic_template: str = "/env_{env_idx}/cmd_vel",
        node_name: str = "go2_multi_env_ros2_twist_bridge",
        force_twist_mode: bool = True,
        qos_depth: int = 10,
        executor_num_threads: int = 2,
    ):
        self.num_envs = num_envs
        self.topic_template = topic_template
        self.node_name = node_name
        self.force_twist_mode = force_twist_mode
        self.qos_depth = qos_depth
        self.executor_num_threads = executor_num_threads

        self._thread: Optional[threading.Thread] = None
        self._node: Optional[Go2MultiEnvRos2TwistBridge] = None
        self._executor: Optional[MultiThreadedExecutor] = None
        self._running = False

    def start(self) -> None:
        if self._running:
            return

        if not rclpy.ok():
            rclpy.init()

        self._node = Go2MultiEnvRos2TwistBridge(
            num_envs=self.num_envs,
            topic_template=self.topic_template,
            node_name=self.node_name,
            force_twist_mode=self.force_twist_mode,
            qos_depth=self.qos_depth,
        )

        self._executor = MultiThreadedExecutor(num_threads=self.executor_num_threads)
        self._executor.add_node(self._node)

        self._thread = threading.Thread(target=self._spin_loop, daemon=True)
        self._thread.start()
        self._running = True

    def _spin_loop(self) -> None:
        if self._executor is None:
            return

        try:
            self._executor.spin()
        except Exception as e:
            if self._node is not None:
                self._node.get_logger().error(f"ROS2 executor spin error: {e}")

    def stop(self) -> None:
        if not self._running:
            return

        if self._executor is not None:
            try:
                self._executor.shutdown()
            except Exception:
                pass
            self._executor = None

        if self._node is not None:
            try:
                self._node.destroy_node()
            except Exception:
                pass
            self._node = None

        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=1.0)

        self._thread = None
        self._running = False

    @property
    def node(self) -> Optional[Go2MultiEnvRos2TwistBridge]:
        return self._node