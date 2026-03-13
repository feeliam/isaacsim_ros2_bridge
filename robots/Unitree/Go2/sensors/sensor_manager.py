from robots.base.base_sensor_manager import BaseSensorManager
from robots.Unitree.Go2.sensors.camera_manager import Go2CameraManager
from robots.Unitree.Go2.sensors.lidar_manager import Go2LidarManager
from robots.Unitree.Go2.sensors.sensor_cfg import Go2SensorParam


class Go2SensorManager(BaseSensorManager):
    def __init__(self, num_envs: int, sensor_param: Go2SensorParam | None = None):
        self.num_envs = num_envs
        self.sensor_param = sensor_param or Go2SensorParam()

        self.camera_manager = Go2CameraManager(num_envs, self.sensor_param)
        self.lidar_manager = Go2LidarManager(num_envs, self.sensor_param)

    def create_camera(self):
        return self.camera_manager.create()

    def create_lidar(self):
        return self.lidar_manager.create()