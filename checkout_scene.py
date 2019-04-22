"""
old check out scene tools are used by publish scene and update timeline
"""
from . import *
from pym.core import workspace, openFile, saveAs, warning
from pymel.util import path


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
            "Cameras": "_Cam",
            "Layouts": "sg_maya_layout",
            "Animation": "_Anim",
            "Lighting": "sg_maya_light"
        }
        entity_type = "Shot"
        if key in ["Rigs", "Assets"]:
            entity_type = "Asset"
        entity_code = path(scene_directory).basename()

        published_file = None
        if key == "Cameras" or key == "Animation":
            version_additional_filter_presets = [
                {
                    "preset_name": "LATEST",
                    "latest_by": "ENTITIES_CREATED_AT"
                }
            ]
            published_file = sg.find_one(
                "Version",
                [["project", "is", project], ["code", "contains", entity_code+data[key]]],
                fields=["sg_maya_file"],
                additional_filter_presets=version_additional_filter_presets
            )["sg_maya_file"]["local_path_windows"]
        else:
            entity_filters = [
                ["project", "is", project],
                ["code", "is", entity_code]
            ]

            if key == "Rigs":
                entity_filters += [["sg_asset_type", "is", "CG Rig"]]
            elif key == "Assets":
                entity_filters += [["sg_asset_type", "is", "CG Model"]]

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
        print ">> Checked out file: ..{}\n".format(checkout_file.split("scenes")[1]),
        return checkout_file
