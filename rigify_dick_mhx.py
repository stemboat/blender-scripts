"""
make the dicktator part
(https://www.renderotica.com/store/sku/65079_Cover-Up-For-G8M-Dicktator)
of a mhx rig(exported from daz studio to blender using diffeomorphic(
http://diffeomorphic.blogspot.com/)) be ik, by creating another ik rig then copy
transformation to the original corresponding bones.
enable rigify and install this feature set(https://smutba.se/project/31632/),
select the mhx rig in object mode and apply scale, then run the script.

tested with g8m / blender 3.3.1 / rigify dicks 1.0.6 / diffeomorphic 1.62
just amateur, use with caution.
"""
import bpy

SHAFT_LENGTH = 7
SHAFT_LAYER_IN_MHX = 16
SUCCESS_MESSAGE = "Succeed"
SET_BODY_RIG_NAME = "Rig:Body"
SET_DICK_RIG_NAME = "Rig:Dick"
SET_META_RIG_NAME = "MetaRig:Dick"


def notify(message="", title="Error", icon="ERROR"):
    """show message box"""

    def draw(self, _):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def extrude_shaft(to_location):
    """extrude shaft bone outward"""
    bpy.ops.armature.extrude_move(
        ARMATURE_OT_extrude={"forked": False},
        TRANSFORM_OT_translate={
            "value": to_location,
            "orient_axis_ortho": "X",
            "orient_type": "GLOBAL",
            "orient_matrix": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            "orient_matrix_type": "GLOBAL",
            "constraint_axis": (False, False, False),
            "mirror": False,
            "use_proportional_edit": False,
            "proportional_edit_falloff": "SMOOTH",
            "proportional_size": 1,
            "use_proportional_connected": False,
            "use_proportional_projected": False,
            "snap": False,
            "snap_elements": {"INCREMENT"},
            "use_snap_project": False,
            "snap_target": "CLOSEST",
            "use_snap_self": True,
            "use_snap_edit": True,
            "use_snap_nonedit": True,
            "snap_point": (0, 0, 0),
            "snap_align": False,
            "snap_normal": (0, 0, 0),
            "gpencil_strokes": False,
            "cursor_transform": False,
            "texture_space": False,
            "remove_on_cancel": False,
            "view2d_edge_pan": False,
            "release_confirm": False,
            "use_accurate": False,
            "use_automerge_and_split": False,
        },
    )


def get_shaft_locations(rig_obj):
    """return tail/head locations of shaft bones of the original rig"""
    chain_positions = []
    for i in range(1, SHAFT_LENGTH + 1):
        bpy.ops.object.empty_add()
        active_obj = bpy.context.object
        active_obj.name = f"Empty.Chain.shaft{i}.tail"
        bpy.ops.object.constraint_add(type="COPY_LOCATION")
        active_obj_location_constraint = active_obj.constraints["Copy Location"]
        active_obj_location_constraint.target = rig_obj
        active_obj_location_constraint.subtarget = f"shaft{i}"
        active_obj_location_constraint.head_tail = 0
        bpy.ops.constraint.apply(constraint="Copy Location", owner="OBJECT")
        chain_positions.append(active_obj.location)

        if i == SHAFT_LENGTH:
            bpy.ops.object.empty_add()
            active_obj = bpy.context.object
            active_obj.name = f"Empty.Chain.shaft{i}.head"
            bpy.ops.object.constraint_add(type="COPY_LOCATION")
            active_obj.constraints["Copy Location"].target = rig_obj
            active_obj.constraints["Copy Location"].subtarget = f"shaft{i}"
            active_obj.constraints["Copy Location"].head_tail = 1
            bpy.ops.constraint.apply(constraint="Copy Location", owner="OBJECT")
            chain_positions.append(active_obj.location)

    return chain_positions


def __init__():
    body_rig_obj = bpy.context.active_object
    body_rig_obj.name = SET_BODY_RIG_NAME
    body_rig_obj.data.layers[SHAFT_LAYER_IN_MHX] = True

    chain_positions = get_shaft_locations(body_rig_obj)

    for index, value in enumerate(chain_positions):
        if index == 0:
            bpy.ops.object.armature_add(
                enter_editmode=True,
                align="WORLD",
                location=(0, 0, 0),
                scale=(1, 1, 1),
            )
            bpy.context.object.show_in_front = True
            bpy.context.object.name = "Metarig:Gen"
            active_bone = bpy.context.active_bone
            active_bone.name = f"gen.shaft.{index+1}"
            active_bone.head = value
            active_bone.tail = chain_positions[index + 1]
            continue

        if index + 1 == len(chain_positions):
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.transform_apply(
                location=False, rotation=False, scale=True
            )
            bpy.ops.object.posemode_toggle()
            bpy.context.object.data.bones.active = (
                bpy.data.objects["Metarig:Gen"].pose.bones["gen.shaft.1"].bone
            )
            bpy.context.active_pose_bone.rigify_type = "RBPNY_CUSTOM.penetrator"
            continue

        extrude_shaft(chain_positions[index + 1] - value)
        active_bone = bpy.context.active_bone
        active_bone.name = f"gen.shaft.{index+1}"
        continue

    bpy.ops.pose.rigify_generate()
    gen_object = bpy.context.active_object
    gen_object.name = "Rig:Gen"
    bpy.ops.object.posemode_toggle()
    bpy.context.object.data.bones.active = gen_object.pose.bones["root"].bone
    bpy.ops.pose.constraint_add(type="COPY_TRANSFORMS")
    bpy.context.object.pose.bones["root"].constraints[
        "Copy Transforms"
    ].target = bpy.data.objects["Rig:Body"]

    bpy.context.object.data.bones.active = gen_object.pose.bones[
        "root.001"
    ].bone
    bpy.ops.object.editmode_toggle()
    bpy.context.active_bone.parent = None
    bpy.ops.object.posemode_toggle()
    bpy.ops.pose.constraint_add(type="CHILD_OF")
    bpy.context.object.pose.bones["root.001"].constraints[
        "Child Of"
    ].target = bpy.data.objects[SET_BODY_RIG_NAME]
    bpy.context.object.pose.bones["root.001"].constraints[
        "Child Of"
    ].subtarget = "shaftRoot"
    bpy.ops.constraint.childof_set_inverse(constraint="Child Of", owner="BONE")
    bpy.context.object.show_in_front = True
    bpy.ops.object.posemode_toggle()

    bpy.context.view_layer.objects.active = body_rig_obj
    bpy.ops.object.posemode_toggle()

    for i in range(1, 7):
        bpy.context.object.data.bones.active = bpy.context.object.pose.bones[
            f"shaft{i+1}"
        ].bone
        for constraint in bpy.context.object.pose.bones[
            f"shaft{i+1}"
        ].constraints:
            bpy.context.object.pose.bones[f"shaft{i+1}"].constraints.remove(
                constraint
            )
        bpy.ops.pose.constraint_add(type="COPY_TRANSFORMS")
        bpy.context.object.pose.bones[f"shaft{i+1}"].constraints[
            "Copy Transforms"
        ].target = bpy.data.objects["Rig:Gen"]
        bpy.context.object.pose.bones[f"shaft{i+1}"].constraints[
            "Copy Transforms"
        ].subtarget = f"DEF-gen.shaft.{i+1}"

    indicators = [
        c for c in bpy.data.objects if c.name.startswith("Empty.Chain.shaft")
    ]
    for indicator in indicators:
        bpy.data.objects.remove(indicator, do_unlink=True)

    body_rig_obj.data.layers[SHAFT_LAYER_IN_MHX] = False
    notify(SUCCESS_MESSAGE)


__init__()
