"""
scene_manager.py

作用：
1. 往 Isaac Sim / Isaac Lab 场景中挂载不同的 USD 场景(工作场景)
2. 为场景中的 Mesh 补充碰撞属性
3. 预留语义标签功能接口
"""

from isaacsim.core.utils.prims import define_prim, get_prim_at_path

try:
    import isaacsim.storage.native as nucleus_utils
except ModuleNotFoundError:
    import isaacsim.core.utils.nucleus as nucleus_utils

import omni.replicator.core as rep
import omni

from pxr import UsdGeom, Usd

from isaaclab.sim.schemas import CollisionPropertiesCfg, define_collision_properties


# ============================================================
# 语义标签
# ============================================================

def add_semantic_label() -> None:
    """
    添加语义标签。

    当前函数仅预留接口，暂未真正启用。
    后续可在这里为地面、墙体、货架等对象添加 semantic label。
    """
    # 示例：
    # ground_plane = rep.get.prims("/World/ground")
    # with ground_plane:
    #     rep.modify.semantics([("class", "floor")])
    pass


# ============================================================
# 碰撞属性
# ============================================================

def add_collision(
    prim_path: str,
    contact_offset: float = 0.02,
    rest_offset: float = 0.0,
) -> None:
    """
    为指定根节点下的所有 Mesh Prim 递归添加碰撞属性。

    Args:
        prim_path: 场景挂载根节点路径，例如 "/World/Warehouse"
        contact_offset: 接触偏移, 可以理解为：在物体几何表面外再包一层“提前接触缓冲区”
        rest_offset: 静止偏移, 表示物体在静止接触时允许的表面偏移量
    """
    collision_cfg = CollisionPropertiesCfg(
        collision_enabled=True,
        contact_offset=contact_offset,
        rest_offset=rest_offset,
        torsional_patch_radius=None,
        min_torsional_patch_radius=None,
    )

    stage = omni.usd.get_context().get_stage()
    root_prim = stage.GetPrimAtPath(prim_path)

    if not root_prim or not root_prim.IsValid():
        print(f"[WARN] add_collision: invalid prim path: {prim_path}")
        return

    for prim in Usd.PrimRange(root_prim):
        # 只对 Mesh 类型且非 Prototype 的 Prim 添加碰撞
        if prim.IsA(UsdGeom.Mesh) and not prim.IsPrototype():
            try:
                define_collision_properties(prim.GetPath().pathString, collision_cfg)
            except Exception as e:
                print(f"[WARN] Failed to add collision on {prim.GetPath()}: {e}")


# ============================================================
# 场景挂载公共工具
# ============================================================

def _mount_usd_scene(prim_path: str, asset_rel_path: str) -> None:
    """
    在指定 prim_path 下挂载一个 USD 场景。

    Args:
        prim_path: 挂载根节点路径，例如 "/World/Warehouse"
        asset_rel_path: 相对 Isaac 资产库根目录的 USD 路径
    """
    assets_root_path = nucleus_utils.get_assets_root_path()
    if assets_root_path is None:
        raise RuntimeError("Failed to get Isaac assets root path.")

    # 若路径不存在，则创建一个 Xform 根节点
    prim = get_prim_at_path(prim_path)
    if not prim or not prim.IsValid():
        prim = define_prim(prim_path, "Xform")

    asset_path = assets_root_path + asset_rel_path
    prim.GetReferences().AddReference(asset_path)


def _create_scene(
    prim_path: str,
    asset_rel_path: str,
    enable_collision: bool = False,
    contact_offset: float = 0.02,
    rest_offset: float = 0.0,
) -> None:
    """
    创建仿真场景的统一入口。

    Args:
        prim_path: 场景挂载根节点路径
        asset_rel_path: USD 资产相对路径
        enable_collision: 是否为该场景自动补充碰撞属性
        contact_offset: 碰撞 contact_offset
        rest_offset: 碰撞 rest_offset
    """
    add_semantic_label()
    _mount_usd_scene(prim_path, asset_rel_path)

    if enable_collision:
        add_collision(
            prim_path=prim_path,
            contact_offset=contact_offset,
            rest_offset=rest_offset,
        )


# ============================================================
# 各类场景创建接口
# ============================================================

def create_warehouse_scene() -> None:
    """
    创建普通仓库场景，并补充碰撞属性。
    """
    _create_scene(
        prim_path="/World/Warehouse",
        asset_rel_path="/Isaac/Environments/Simple_Warehouse/warehouse.usd",
        enable_collision=True,
        contact_offset=0.02,
        rest_offset=0.0,
    )


def create_warehouse_forklifts_scene() -> None:
    """
    创建带叉车的仓库场景，并补充碰撞属性。
    """
    _create_scene(
        prim_path="/World/Warehouse",
        asset_rel_path="/Isaac/Environments/Simple_Warehouse/warehouse_with_forklifts.usd",
        enable_collision=True,
        contact_offset=0.02,
        rest_offset=0.0,
    )


def create_warehouse_shelves_scene() -> None:
    """
    创建多货架仓库场景，并补充碰撞属性。
    """
    _create_scene(
        prim_path="/World/Warehouse",
        asset_rel_path="/Isaac/Environments/Simple_Warehouse/warehouse_multiple_shelves.usd",
        enable_collision=True,
        contact_offset=0.02,
        rest_offset=0.0,
    )


def create_full_warehouse_scene() -> None:
    """
    创建完整仓库场景，并补充碰撞属性。
    """
    _create_scene(
        prim_path="/World/Warehouse",
        asset_rel_path="/Isaac/Environments/Simple_Warehouse/full_warehouse.usd",
        enable_collision=True,
        contact_offset=0.02,
        rest_offset=0.0,
    )


def create_hospital_scene() -> None:
    """
    创建医院场景，并补充碰撞属性。
    """
    _create_scene(
        prim_path="/World/Hospital",
        asset_rel_path="/Isaac/Environments/Hospital/hospital.usd",
        enable_collision=True,
        contact_offset=0.02,
        rest_offset=0.0,
    )


def create_office_scene() -> None:
    """
    创建办公室场景，并补充碰撞属性。
    """
    _create_scene(
        prim_path="/World/Office",
        asset_rel_path="/Isaac/Environments/Office/office.usd",
        enable_collision=True,
        contact_offset=0.05,
        rest_offset=0.02,
    )