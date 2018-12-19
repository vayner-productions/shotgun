import pymel.core as pm
import sgtk.platform
import os
import fnmatch

engine = sgtk.platform.current_engine()
sg = engine.shotgun
project = sg.find_one("Project", [["name", "is", engine.context.project["name"]]])


def get_entity(file_path):
    scene_process, entity_name = file_path.rsplit("/", 2)[1:]
    parent_entity = "Shot"
    if scene_process[3:] in ["Assets", "Rigs"]:
        parent_entity = "Asset"

    filters = [
        ["project", "is", project],
        ["code", "is", entity_name]
    ]
    entity = sg.find_one(parent_entity, filters)
    return entity


def get_version(file):
    version = int(file.split(".")[1])
    return version


def increment_and_save(current_file, entity_type="Asset", publish=0):
    scene_directory = pm.workspace.expandName(pm.workspace.fileRules["scene"])
    file_name = scene_directory.rsplit("/", 1)[1][4:]  # model_a
    if "Shot" == entity_type:
        file_name = scene_directory.rsplit("/", 1)[1]  # Shot_###
    processed_file = None

    if current_file and publish:
        processed_file = "{}/{}_processed.{}.ma".format(
            scene_directory,
            file_name,
            str(int(current_file.split(".")[1][1:]) + 1).zfill(4)
        )
    elif current_file and not publish:
        pm.openFile(current_file, f=1)
        processed_file = current_file.replace("original", "processed").replace("published", "scenes")
        # print ">> checked out"
    elif not current_file:
        directory = pm.util.common.path(scene_directory)
        files = directory.files(file_name + "_processed.*.ma")
        if files:
            latest_processed = max(files, key=get_version)
            old = max(files, key=get_version).split(".")[1]
            new = "{:04d}".format(int(old) + 1)
            version = ".{}.".format(new)
            processed_file = version.join(latest_processed.split(".")[::2])
        else:
            processed_file = "{}/{}_processed.0001.ma".format(
                scene_directory,
                file_name)
        # print ">> new:", processed_file

    pm.saveAs(processed_file)
    return processed_file


def checkout_scene():
    scene_directory = pm.workspace.expandName(pm.workspace.fileRules["scene"])
    key = scene_directory.split("scenes/")[1].split("/")[0][3:]

    data = {
        "Rigs": "sg_file",
        "Assets": "sg_file",
        "Cameras": "sg_tracked_camera",
        "Layouts": "sg_maya_layout",
        "Animation": "sg_maya_anim",
        "Lighting": "sg_maya_light"
    }

    entity = get_entity(scene_directory)
    entity_filters = [
        ["project", "is", project],
        ["id", "is", entity["id"]]
    ]
    entity_fields = data[key]
    current_file = sg.find_one(entity["type"],
                               entity_filters,
                               [entity_fields])[entity_fields]

    if current_file:
        current_file = current_file["local_path"]
    new_file = pm.util.path(increment_and_save(current_file, entity_type=entity["type"]))
    print ">> opened: {}".format(pm.util.path.basename(new_file)),
    return current_file

