import work_scene.scene_manager as scene_mng

class Go2WorkSceneBuilder:
    """
    Go2 工作仿真场景构建器
    """

    _SCENE_BUILDERS = {
        "warehouse": scene_mng.create_warehouse_scene,
        "warehouse-forklifts": scene_mng.create_warehouse_forklifts_scene,
        "warehouse-shelves": scene_mng.create_warehouse_shelves_scene,
        "full-warehouse": scene_mng.create_full_warehouse_scene,
        "office": scene_mng.create_office_scene,
    }

    @classmethod
    def build(self, scene_name: str) -> None:
        """
        根据场景名称创建场景
        """
        if scene_name not in self._SCENE_BUILDERS:
            raise ValueError(f"Unsupported scene_name: {scene_name}")
        self._SCENE_BUILDERS[scene_name]()