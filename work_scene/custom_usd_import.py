"""
custom_usd_import.py

作用：
1. 导入自定义的 USD / USDA / USDC / USDZ 场景文件
2. 获取并操作指定路径下的 Prim
3. 为目标 Prim 设置平移、旋转、缩放
4. 可选：将物理场景设置为同步模式（Synchronous）

适用场景：
- 导入自定义环境场景
- 导入第三方 USD / USDZ 资源
- 导入高斯场景、建筑场景、室内场景、地图场景等
"""

from pxr import UsdPhysics, PhysxSchema, UsdGeom, Gf
import omni.usd
import os


# ============================================================
# 默认测试路径（你可以改成自己的）
# ============================================================

DEFAULT_USD_PATH = "/home/loe/workspace/github/isaacsim5.0_ros2_go2/models/konkuk_library.usdz"


# ============================================================
# 工具函数：打开 USD / USDZ 场景
# ============================================================

def open_usd_stage(usd_path):
    """
    打开指定的 USD / USDA / USDC / USDZ 文件，并返回当前 Stage

    参数：
        usd_path:
            文件完整路径，例如：
                /home/xxx/scene.usd
                /home/xxx/scene.usdz
    """

    # 1. 判断文件是否存在
    if not os.path.exists(usd_path):
        print("[ERROR] USD 文件不存在:", usd_path)
        return None

    # 2. 打开 Stage
    # 注意：
    # open_stage 会直接打开这个文件作为当前 Stage
    # 它不是 reference 挂载，而是“整个场景打开”
    omni.usd.get_context().open_stage(usd_path)

    # 3. 获取当前 Stage
    stage = omni.usd.get_context().get_stage()

    if stage is None:
        print("[ERROR] 打开 Stage 失败:", usd_path)
        return None

    print("[INFO] 已加载场景:", usd_path)
    return stage


# ============================================================
# 工具函数：获取 Prim
# ============================================================

def get_prim_by_path(stage, prim_path):
    """
    根据路径从 Stage 中获取 Prim

    参数：
        stage:
            当前 USD Stage

        prim_path:
            Prim 路径，例如：
                /World
                /World/gauss
                /Root/MyScene
    """

    if stage is None:
        print("[ERROR] get_prim_by_path: stage is None")
        return None

    prim = stage.GetPrimAtPath(prim_path)

    if not prim or not prim.IsValid():
        print("[ERROR] 未找到 Prim:", prim_path)
        return None

    return prim


# ============================================================
# 工具函数：设置 Prim 的平移 / 旋转 / 缩放
# ============================================================

def set_prim_transform(
    prim,
    translate=None,
    rotate_xyz=None,
    scale=None,
    instanceable=None,
):
    """
    设置指定 Prim 的 transform 属性

    参数：
        prim:
            目标 Prim

        translate:
            平移，例如：
                (0.0, 0.0, 1.0)

        rotate_xyz:
            欧拉角旋转（单位：度），例如：
                (0.0, 0.0, 90.0)

        scale:
            缩放，例如：
                (1.0, 1.0, 1.0)

        instanceable:
            是否设为实例化
            True / False / None
            为 None 时不修改
    """

    if not prim or not prim.IsValid():
        print("[ERROR] set_prim_transform: 无效的 Prim")
        return False

    # 将 Prim 视为可进行几何变换的对象
    xformable = UsdGeom.Xformable(prim)

    # -------------------------------------------------------
    # 设置平移
    # -------------------------------------------------------
    if translate is not None:
        if not prim.GetAttribute("xformOp:translate"):
            xformable.AddTranslateOp()

        prim.GetAttribute("xformOp:translate").Set(
            Gf.Vec3f(translate[0], translate[1], translate[2])
        )

    # -------------------------------------------------------
    # 设置旋转（欧拉角 XYZ）
    # -------------------------------------------------------
    if rotate_xyz is not None:
        if not prim.GetAttribute("xformOp:rotateXYZ"):
            xformable.AddRotateXYZOp()

        prim.GetAttribute("xformOp:rotateXYZ").Set(
            Gf.Vec3f(rotate_xyz[0], rotate_xyz[1], rotate_xyz[2])
        )

    # -------------------------------------------------------
    # 设置缩放
    # -------------------------------------------------------
    if scale is not None:
        if not prim.GetAttribute("xformOp:scale"):
            xformable.AddScaleOp()

        prim.GetAttribute("xformOp:scale").Set(
            Gf.Vec3f(scale[0], scale[1], scale[2])
        )

    # -------------------------------------------------------
    # 设置实例化属性
    # -------------------------------------------------------
    if instanceable is not None:
        prim.SetInstanceable(instanceable)

    print("[INFO] 已设置 Prim 变换:", prim.GetPath())

    if translate is not None:
        print("       translate   =", translate)

    if rotate_xyz is not None:
        print("       rotate_xyz  =", rotate_xyz)

    if scale is not None:
        print("       scale       =", scale)

    if instanceable is not None:
        print("       instanceable=", instanceable)

    return True


# ============================================================
# 工具函数：设置物理场景为同步模式
# ============================================================

def set_physics_scene_synchronous(stage):
    """
    遍历当前 Stage，查找 Physics Scene，
    并将其 PhysX 更新模式设置为 Synchronous

    同步模式更适合：
    - 机器人控制
    - 导航仿真
    - 需要稳定、可重复的物理更新场景
    """

    if stage is None:
        print("[ERROR] set_physics_scene_synchronous: stage is None")
        return False

    for prim in stage.Traverse():

        # 查找物理场景 Prim
        if prim.IsA(UsdPhysics.Scene):
            try:
                # 给该 Prim 应用 PhysX Scene API
                physx_scene = PhysxSchema.PhysxSceneAPI.Apply(prim)

                # 设置更新模式为同步
                physx_scene.GetUpdateTypeAttr().Set("Synchronous")

                print("[INFO] Physics Scene 已设置为 Synchronous:", prim.GetPath())
                return True

            except Exception as e:
                print("[ERROR] 设置 Physics Scene 为 Synchronous 失败:", e)
                return False

    print("[WARN] 当前 Stage 中未找到 UsdPhysics.Scene")
    return False


# ============================================================
# 工具函数：打印 Stage 中的部分 Prim 路径（调试用）
# ============================================================

def print_stage_prim_paths(stage, max_count=50):
    """
    打印当前 Stage 中的 Prim 路径，便于调试查看场景结构

    参数：
        stage:
            当前 USD Stage

        max_count:
            最多打印多少个 Prim
    """

    if stage is None:
        print("[ERROR] print_stage_prim_paths: stage is None")
        return

    print("[INFO] 当前 Stage 中的 Prim 路径（最多显示 {} 个）:".format(max_count))

    count = 0
    for prim in stage.Traverse():
        print("   ", prim.GetPath())
        count += 1
        if count >= max_count:
            break


# ============================================================
# 工具函数：导入场景后自动寻找一个可操作的根 Prim（可选）
# ============================================================

def find_first_valid_root_child(stage):
    """
    查找当前 Stage 根节点下的第一个有效子 Prim

    用途：
        当你不知道自定义 USD / USDZ 内部结构时，
        可以先打印 Stage 或自动找一个根节点下的子 Prim 看看。

    返回：
        找到则返回 Prim
        否则返回 None
    """

    if stage is None:
        return None

    pseudo_root = stage.GetPseudoRoot()
    children = pseudo_root.GetChildren()

    for child in children:
        if child and child.IsValid():
            return child

    return None


# ============================================================
# 主函数：导入自定义 USD / USDZ 场景
# ============================================================

def import_usd_scene(
    usd_path=DEFAULT_USD_PATH,
    target_prim_path=None,
    translate=None,
    rotate_xyz=None,
    scale=None,
    instanceable=False,
    set_sync_physics=True,
    print_stage_paths=False,
    print_stage_paths_max_count=50,
):
    """
    导入自定义的 USD / USDZ 场景，并可选地对指定 Prim 做变换设置。

    参数：
        usd_path:
            自定义 USD / USDZ 文件路径

        target_prim_path:
            需要操作的目标 Prim 路径，例如：
                /World/gauss
                /World/MyScene
            如果为 None，则只导入场景，不设置 Prim 变换

        translate:
            目标 Prim 的平移参数，例如：
                (0.0, 0.0, 1.4)

        rotate_xyz:
            目标 Prim 的欧拉角旋转，例如：
                (17.3, 0.0, 0.0)

        scale:
            目标 Prim 的缩放参数，例如：
                (3.0, 3.0, 3.0)

        instanceable:
            是否将目标 Prim 设为实例化
            常见情况下，为了便于单独修改属性，通常设为 False

        set_sync_physics:
            是否将场景中的 Physics Scene 设置为同步模式

        print_stage_paths:
            是否打印当前 Stage 中的 Prim 路径
            当你不清楚内部 Prim 路径时非常有用

        print_stage_paths_max_count:
            最多打印多少个 Prim 路径
    """

    # -------------------------------------------------------
    # 1. 打开 USD / USDZ 场景
    # -------------------------------------------------------
    stage = open_usd_stage(usd_path)
    if stage is None:
        return False

    # -------------------------------------------------------
    # 2. 可选：打印 Stage 中的 Prim 路径
    # -------------------------------------------------------
    if print_stage_paths:
        print_stage_prim_paths(stage, max_count=print_stage_paths_max_count)

    # -------------------------------------------------------
    # 3. 如果指定了 target_prim_path，则对目标 Prim 做变换设置
    # -------------------------------------------------------
    if target_prim_path is not None:
        target_prim = get_prim_by_path(stage, target_prim_path)

        if target_prim is None:
            print("[ERROR] 目标 Prim 不存在，无法继续设置变换")
            return False

        ok = set_prim_transform(
            prim=target_prim,
            translate=translate,
            rotate_xyz=rotate_xyz,
            scale=scale,
            instanceable=instanceable,
        )

        if not ok:
            return False

    # -------------------------------------------------------
    # 4. 可选：将 Physics Scene 设为同步模式
    # -------------------------------------------------------
    if set_sync_physics:
        set_physics_scene_synchronous(stage)

    print("[INFO] import_usd_scene 执行完成")
    return True


# ============================================================
# 示例调用
# ============================================================

def example_import():
    """
    示例：
    导入自定义 usdz 文件，并对 /World/gauss 做平移、旋转、缩放
    """

    import_usd_scene(
        usd_path=DEFAULT_USD_PATH,
        target_prim_path="/World/gauss",
        translate=(0.0, 0.0, 1.4),
        rotate_xyz=(17.3, 0.0, 0.0),
        scale=(3.0, 3.0, 3.0),
        instanceable=False,
        set_sync_physics=True,
        print_stage_paths=False,
    )