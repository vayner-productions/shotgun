"""
"""
from . import *
from pymel.core import workspace, openFile, saveAs, warning
from pymel.util import path
from PySide2 import QtCore, QtWidgets, QtUiTools
import maya.mel as mel


def get_window():
    global mw
    try:
        mw.ui.close()
    except:
        pass

    mw = MyWindow()
    mw.ui.show()


class Checkout(object):
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


class SetProject(object):
    def __init__(self):
        self.project_path = self.get_project_path()
        self.exclude = {
            "edits",
            "04_Layouts",
            "06_Cache",
            "None"
        }
        self.scene_dict = self.get_scene_items()

    def get_project_path(self):
        # used for remote-work, change the root variable
        if root:
            project_path = root
            return

        # used for in-office development
        data = sg.find_one(
            "Project",
            [
                ["id", "is", project["id"]]
            ],
            [
                "sg_client",
                "sg_brand",
                "name"
            ]
        )
        client_brand = data["sg_client"]["name"]
        sub_brand = data["sg_brand"]["name"]
        project_name = data["name"]
        project_path = r"{}/Animation/Projects/Client/{}/{}/{}/Project Directory/02_Production/04_Maya".format(
            mapped_letter, client_brand, sub_brand, project_name)
        return project_path

    def get_scene_items(self):
        scene_dir = self.project_path + "/scenes"
        scene_subfolders = {r"{}".format(sub.namebase) for sub in path(scene_dir).dirs()}.difference(self.exclude)

        scene_items = {sub[3:]: sub for sub in scene_subfolders}
        return scene_items

    def set_project(self, scene=None, alembic=None):
        workspace.open(self.project_path)

        workspace.fileRules["scene"] = scene

        workspace.fileRules["Alembic"] = alembic

        workspace.fileRules["shaders"] = "data/001_Shaders"

        mel.eval('setProject \"' + self.project_path + '\"')
        print ">> project set\n",
        return


class MyWindow(SetProject, Checkout, QtWidgets.QDialog):
    def __init__(self, **kwargs):
        super(MyWindow, self).__init__(**kwargs)
        self.ui = self.import_ui()
        self.init_ui()

    def import_ui(self):
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    def change_entity_items(self):
        scene_process = self.ui.scene_cbx.currentText()
        scene_process_folder = self.scene_dict[scene_process]

        scene_process_dir = path(r"{}{}{}".format(
            self.project_path,
            "/scenes/",
            scene_process_folder))

        folders = []
        self.ui.asset_cbx.clear()
        for dir in scene_process_dir.dirs():
            folder = dir.basename()
            if "Archive" not in folder:
                folders += [folder]
        folders = sorted(folders)

        self.ui.asset_cbx.addItems(folders)
        return

    def checkout(self):

        self.set_project(scene=scene, alembic=alembic)
        return

    def init_ui(self):
        self.ui.scene_cbx.currentTextChanged.connect(self.change_entity_items)

        items = [item[3:] for item in sorted(self.scene_dict.values())]
        self.ui.scene_cbx.addItems(items)

        self.ui.checkout_cbx.clicked.connect(self.checkout)
        return
