import omni.graph.core as og
import omni.replicator.core as rep
import omni.kit.commands
import rclpy

class SensorDataManager:
    def __init__(self, env, cfg, entity:str):
        self.env = env
        self.num_envs = cfg.num_envs
        self.robot_data = self.env.unwrapped.scene[entity].data
        self.node_name : str = f"{entity}_sensor_data_manager"
        if not rclpy.ok():
            rclpy.init()
        self.node = rclpy.create_node(self.node_name)

    def pub_camera_ros2_msg(self, cameras_list, frame_id_list, topic_template):
        """
        发布 camera 图像topic
        """
        if cameras_list or frame_id_list is None:
            print(f"[Error] no camera or no frame id")
        for i in range(self.num_envs):
            render_product_path = cameras_list.render_product_paths[i]
            graph_path = f"/World/Camera_ROS_Graph_env_{i}"
            topic_name = f"env_{i}" + topic_template
            frame_id = frame_id_list[i]
            try:
                og.Controller.edit(
                    {"graph_path": graph_path, "evaluator_name": "push"},
                    {
                        og.Controller.Keys.CREATE_NODES: [
                            ("OnTick", "omni.graph.action.OnTick"),
                            ("cameraHelperRgb", "isaacsim.ros2.bridge.ROS2CameraHelper"),
                        ],
                        og.Controller.Keys.CONNECT: [
                            ("OnTick.outputs:tick", "cameraHelperRgb.inputs:execIn"),
                        ],
                        og.Controller.Keys.SET_VALUES: [
                            ("cameraHelperRgb.inputs:renderProductPath", render_product_path),
                            ("cameraHelperRgb.inputs:frameId", frame_id),
                            ("cameraHelperRgb.inputs:topicName", topic_name),
                            ("cameraHelperRgb.inputs:type", "rgb"),
                            ("cameraHelperRgb.inputs:frameSkipCount", 0),
                        ],
                    },
                )
            except Exception as e:
                print (f"[Error]  Failed to create Camera Helper for Env {i}: {e}")

    def pub_lidar_ros2_msg(self, lidar_list, fram_id_list, topic_template:str):
        """
        发布 lidar 点云topic
        """
        if lidar_list is None:
            print(f"[Error] no lidar")
            for i, annotator in enumerate(lidar_list):
                render_product_obj = rep.create.render_product(annotator.GetPath(), resolution=[1024, 64], name="Isaac")
                render_product_path = render_product_obj.path

                graph_path = f"/World/Lidar_ROS_Graph_env_{i}"
                topic_name = f"env_{i}" + topic_template
                fram_id = fram_id_list[i]
                try:
                    og.Controller.edit(
                        {"graph_path": graph_path, "evaluator_name": "push"},
                        {
                            og.Controller.Keys.CREATE_NODES: [
                                ("OnTick", "omni.graph.action.OnTick"),
                                ("LidarHelper", "isaacsim.ros2.bridge.ROS2RtxLidarHelper"),
                            ],
                            og.Controller.Keys.CONNECT: [
                                ("OnTick.outputs:tick", "LidarHelper.inputs:execIn"),
                            ],
                            og.Controller.Keys.SET_VALUES: [
                                ("LidarHelper.inputs:renderProductPath", render_product_path),
                                ("LidarHelper.inputs:topicName", topic_name),
                                ("LidarHelper.inputs:frameId", fram_id),
                                ("LidarHelper.inputs:type", "point_cloud"), 
                                ("LidarHelper.inputs:fullScan", True), 
                                ("LidarHelper.inputs:frameSkipCount", 0),
                                ("LidarHelper.inputs:resetSimulationTimeOnStop", True),
                            ],
                        },
                    )
                except Exception as e:
                    print (f"[Error]  Failed to create Lidar Helper for Env {i}: {e}")

    def create_odom_ros2_node(self, frame_id_list, topic_template):
        """
        创建 ros2 的里程计odom信息节点 

        """
        if frame_id_list is None :
            print(f"[Error] no frame_id_list")
        for i in range(self.num_envs):


            graph_path = f"/World/Odom_ROS_Graph_env_{i}"
            topic_name = f"env_{i}" + topic_template
            frame_id = frame_id_list[i]
            chassisFrameId = f"base_link_{i}"

            try:
                og.Controller.edit(
                    {"graph_path": graph_path, "evaluator_name": "push"},
                    {
                        og.Controller.Keys.CREATE_NODES: [
                            ("PublishOdom", "isaacsim.ros2.bridge.ROS2PublishOdometry"),
                        ],
                        og.Controller.Keys.SET_VALUES: [
                            ("PublishOdom.inputs:topicName", topic_name),
                            ("PublishOdom.inputs:odomFrameId", frame_id),
                            ("PublishOdom.inputs:chassisFrameId", chassisFrameId),
                        ],
                    },
                )
                print(f"[Bridge] Odometry Publisher Node created for Env {i}")
            except Exception as e:
                print(f"[Error] Failed to create Odometry Publisher for Env {i}: {e}")

    def pub_odom_ros2_msg(self):


        # 计算时间
        current_sim_time = self.env.unwrapped.sim.current_time
        for i in range(self.num_envs):
            odom_node_path = f"/World/Odom_ROS_Graph_env_{i}/PublishOdom"
            
            # (Root State: [pos_x, pos_y, pos_z, quat_w, quat_x, quat_y, quat_z])
            pos = self.robot_data.root_state_w[i, :3].tolist()
            # Isaac Lab(WXYZ) -> ROS 2(XYZW)
            quat_wxyz = self.robot_data.root_state_w[i, 3:7]
            quat_xyzw = [quat_wxyz[1].item(), quat_wxyz[2].item(), quat_wxyz[3].item(), quat_wxyz[0].item()]
            
            
            lin_vel = self.robot_data.root_lin_vel_b[i].tolist()
            ang_vel = self.robot_data.root_ang_vel_b[i].tolist()

            try:
                og.Controller.set(og.Controller.attribute(f"{odom_node_path}.inputs:position"), pos)
                og.Controller.set(og.Controller.attribute(f"{odom_node_path}.inputs:orientation"), quat_xyzw)
                og.Controller.set(og.Controller.attribute(f"{odom_node_path}.inputs:linearVelocity"), lin_vel)
                og.Controller.set(og.Controller.attribute(f"{odom_node_path}.inputs:angularVelocity"), ang_vel)
                og.Controller.set(og.Controller.attribute(f"{odom_node_path}.inputs:timeStamp"), current_sim_time)
                
            except Exception as e:
                pass

    def pub_clock_ros2_msg(self):
        """
        发布 clock 
        """
        graph_path = "/World/Push_ROS2_Clock"

        try:
            og.Controller.edit(
                {"graph_path": graph_path, "evaluator_name": "execpushution"},
                {
                    og.Controller.Keys.CREATE_NODES: [
                        ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                        ("ReadSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
                        ("PublishClock", "isaacsim.ros2.bridge.ROS2PublishClock"),
                    ],
                    og.Controller.Keys.CONNECT: [
                        ("OnPlaybackTick.outputs:tick", "PublishClock.inputs:execIn"),
                        ("ReadSimTime.outputs:simulationTime", "PublishClock.inputs:timeStamp"),
                    ],
                },
            )
        except Exception as e:
            print(f"[Error] Global OmniGraph setup error: {e}")
    
    def update(self):
        """
        更新 持续发布
        """
        rclpy.spin_once(self.node, timeout_sec=0)

        self.pub_odom_ros2_msg()


    def destroy_node(self):
        """
        销毁 节点
        """
        if hasattr(self, 'node'):
            self.node.destroy_node()


