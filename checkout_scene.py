import pymel.core as pm
import sgtk.platform

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


def increment_and_save(current_file, entity_type="Asset", publish=0):
    scene_directory = pm.workspace.expandName(pm.workspace.fileRules["scene"])
    file_name = scene_directory.rsplit("/", 1)[1][4:]
    if "Shot" == entity_type:
        file_name = scene_directory.rsplit("/", 1)[1]
    processed_file = None

    if current_file and publish:
        processed_file = "{}/{}_processed.{}.ma".format(
            scene_directory,
            file_name,
            str(int(current_file.split(".")[1][1:]) + 1).zfill(4)
        )
    elif current_file and not publish:
        pm.openFile(current_file, f=1)
        processed_file = "{}/{}_processed.{}.ma".format(
            scene_directory,
            file_name,
            str(int(current_file.split(".")[1][1:]) + 1).zfill(4)
        )
        # print ">> checked out"

    elif not current_file:
        processed_file = "{}/{}_processed.0001.ma".format(
            scene_directory,
            file_name)
        # print ">> new:", processed_file

    pm.saveAs(processed_file)
    return processed_file


def checkout_scene():
    scene_directory = pm.workspace.expandName(pm.workspace.fileRules["scene"])
    data = {
        "Rigs": "sg_file",
        "Assets": "sg_file",
        "Cameras": "sg_tracked_camera",
        "Animation": "sg_maya_scene",
        "Lighting": "sg_maya_scene__light_"
    }

    entity = get_entity(scene_directory)
    entity_filters = [
        ["project", "is", project],
        ["id", "is", entity["id"]]
    ]
    entity_fields = data[scene_directory.split("scenes/")[1].split("/")[0][3:]]
    current_file = sg.find_one(entity["type"],
                               entity_filters,
                               [entity_fields])[entity_fields]

    if current_file:
        current_file = current_file["local_path"]
    new_file = increment_and_save(current_file, entity_type=entity["type"])
    print ">> opened: {}".format(pm.util.path.basename(pm.sceneName())),
    return current_file

