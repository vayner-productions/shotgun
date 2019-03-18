"""
old check out scene tools are used by publish scene and update timeline
"""

import pymel.core as pm

# from . import sg, project  # this line works when __init__.py works, content currently commented out
from sgtk import platform

root = None
engine = platform.current_engine()
sg = engine.shotgun
project = sg.find_one("Project", [["name", "is", engine.context.project["name"]]])

import pymel.util.path as path
from pymel.core.system import Workspace, openFile, saveAs, warning
workspace = Workspace()


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


class Checkout:
    def __init__(self):
        # self.processed_file()
        # self.published_file()
        return

    def processed_file(self):
        processed_path = path(workspace.expandName(workspace.fileRules["scene"]))
        search_pattern = "{}_processed.*.ma".format(processed_path.basename())
        if search_pattern[:3].isdigit():
            search_pattern = search_pattern[4:]
        processed_files = sorted(processed_path.files(search_pattern))[::-1]

        processed_file = None
        if processed_files:
            processed_file = sorted(processed_path.files(search_pattern))[::-1][0].normpath()
        return processed_file

    def published_file(self):
        scene_directory = workspace.fileRules["scene"]

        key = path(scene_directory).dirname().basename()[3:]
        data = {
            "Rigs": "sg_file",
            "Assets": "sg_file",
            "Cameras": "sg_maya_camera",
            "Layouts": "sg_maya_layout",
            "Animation": "sg_maya_anim",
            "Lighting": "sg_maya_light"
        }
        entity_type = "Shot"
        if key in ["Rigs", "Assets"]:
            entity_type = "Asset"

        entity_code = path(scene_directory).basename()

        published_file = None
        if key == "Cameras":
            version_additional_filter_presets = [
                {
                    "preset_name": "LATEST",
                    "latest_by": "ENTITIES_CREATED_AT"
                }
            ]
            published_file = sg.find_one(
                "Version",
                [["project", "is", project], ["code", "contains", entity_code+"_Cam"]],
                fields=[data[key]],
                additional_filter_presets=version_additional_filter_presets
            )[data[key]]["local_path_windows"]
        else:
            entity_filters = [
                ["project", "is", project],
                ["code", "is", entity_code]
            ]
            published_file = sg.find_one(
                entity_type,
                entity_filters,
                [data[key]]
            )[data[key]]["local_path_windows"]
        published_file = path(published_file).normpath()
        published_file = "{}".format(published_file)
        return published_file

    def run(self, checkout_type="processed", checkout_file=None):
        """
        saves any file into working directory and renames it to Vayner's naming convention

        "processed" - opens the latest working file
        "published" - opens the latest published file, saves and increments as processed file
        "other" - opens any file, saves and increments as processed file
        "increment" - versions up the active file to match the naming convention for the set project. This is useful for
        copy lighting setup from one shot to another. To do so,
        1. open file with lighting setup
        2. set project to the shot to copy to
        3. run(checkout_type="increment")
        * may need to remove referenced assets of old shot
        4. build scene to update assets for the new shot

        ** set project to use the correct working directory **
        ** build scene references/updates assets specific to active shot **
        :param checkout_type: [str] "processed", "published", "other"
        :param checkout_file:
        :return: [str] working file path
        """
        if checkout_type == "processed":
            checkout_file = self.processed_file()
            openFile(self.processed_file(), f=1)
        elif checkout_type == "published":
            checkout_file = self.processed_file().split(".")
            checkout_file[1] = str(int(checkout_file[1]) + 1).zfill(4)
            checkout_file = ".".join(checkout_file)
            openFile(self.published_file(), f=1)
            saveAs(checkout_file)
        elif checkout_type == "increment":
            checkout_file = self.processed_file()
            if not checkout_file:
                processed_path = path(workspace.expandName(workspace.fileRules["scene"]))
                search_pattern = "{}_processed.*.ma".format(processed_path.basename())
                checkout_file = path(processed_path + "/" + search_pattern.replace("*", "0001")).normpath()
                checkout_file = r"{}".format(checkout_file)  # converts from path object to string
            else:
                checkout_file = checkout_file.split(".")
                checkout_file[1] = str(int(checkout_file[1]) + 1).zfill(4)
                checkout_file = ".".join(checkout_file)
            saveAs(checkout_file)
        elif checkout_type == "other" and checkout_file:
            openFile(checkout_file, f=1)
            checkout_file = self.processed_file().split(".")
            checkout_file[1] = str(int(checkout_file[1]) + 1).zfill(4)
            checkout_file = ".".join(checkout_file)
            saveAs(checkout_file)
        else:
            return warning("Wrong checkout type and/or missing checkout file.")
        print ">>", checkout_file,
        return checkout_file
