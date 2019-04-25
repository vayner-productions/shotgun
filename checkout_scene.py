"""
"""
from . import *
from pymel.core import workspace, openFile, saveAs, displayInfo, newFile
from pymel.util import path
from PySide2 import QtCore, QtWidgets, QtUiTools
import maya.mel as mel
from . import update_timeline
reload(update_timeline)


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
        self.checkout_file = None
        return

    def processed_file(self, open_file=1):
        scene_path = workspace.path.joinpath(workspace.fileRules["scene"])
        search_pattern = str(scene_path.namebase + "_processed.*.ma")
        if search_pattern[:3].isdigit():
            search_pattern = search_pattern[4:]

        processed_files = sorted(scene_path.files(search_pattern))[::-1]
        if processed_files:
            self.checkout_file = processed_files[0].normpath()
        else:
            checkout_filename = path(workspace.fileRules["scene"]).namebase + "_processed.0001.ma"
            if checkout_filename[:3].isdigit():
                checkout_filename = checkout_filename[4:]

            self.checkout_file = workspace.path.joinpath(
                workspace.fileRules["scene"],
                checkout_filename
            ).normpath()

        if open_file and self.checkout_file.exists():
            openFile(self.checkout_file, f=1)
        elif open_file and not self.checkout_file.exists():
            # saveAs(self.checkout_file, f=1)
            newFile(f=1)
            displayInfo("No file to checkout, opened new file.")

        try:
            update_timeline.update_timeline()
        except TypeError:
            pass  # not a shot
        except AttributeError:
            displayInfo("No frame range set on Shotgun site.")
        return self.checkout_file

    def increment_file(self, open_file=1):
        self.processed_file(open_file=0)

        if self.checkout_file.exists():
            self.checkout_file = self.checkout_file.split(".")
            self.checkout_file[1] = str(int(self.checkout_file[1]) + 1).zfill(4)
            self.checkout_file = ".".join(self.checkout_file)

        if open_file:
            saveAs(self.checkout_file, f=1)
        return self.checkout_file

    def published_file(self, open_file=1):
        scene_process, entity_name = workspace.fileRules["scene"].split("/")[1:]

        published_file = None
        if "Assets" in scene_process or "Rigs" in scene_process:
            try:
                published_file = path(sg.find_one(
                    "Asset",
                    [["project", "is", project], ["code", "is", entity_name]],
                    ["sg_file"]
                )["sg_file"]["local_path"])
            except:
                pass
        elif "Cameras" in scene_process:
            try:
                published_file = path(sg.find_one(
                    "Version",
                    [["project", "is", project], ["code", "contains", entity_name + "_CAM"]],
                    ["sg_maya_file"],
                    additional_filter_presets=[{"preset_name": "LATEST", "latest_by": "ENTITIES_CREATED_AT"}]
                )["sg_maya_file"]["local_path"])
            except:
                pass
        elif "Animation" in scene_process:
            try:
                published_file = path(sg.find_one(
                    "Version",
                    [["project", "is", project], ["code", "contains", entity_name + "_ANIM"]],
                    ["sg_maya_file"],
                    additional_filter_presets=[{"preset_name": "LATEST", "latest_by": "ENTITIES_CREATED_AT"}]
                )["sg_maya_file"]["local_path"])
            except:
                pass
        elif "Lighting" in scene_process:
            try:
                published_file = path(sg.find_one(
                    "Shot",
                    [["project", "is", project], ["code", "is", entity_name]],
                    ["sg_maya_light"]
                )["sg_maya_light"]["local_path"])
            except:
                pass

        if published_file and open_file:
            self.increment_file(open_file=0)
            openFile(published_file, f=1)
            saveAs(self.checkout_file, f=1)
            return self.checkout_file
        elif not published_file and open_file:
            self.processed_file()
            displayInfo("No published file to checkout, opened latest working file: ../{}".format(
                self.checkout_file.basename()
            ))
            return published_file


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
        # print ">> Project set: {}\n".format(self.project_path),
        return


class MyWindow(SetProject, Checkout, QtWidgets.QDialog):
    def __init__(self, **kwargs):
        super(MyWindow, self).__init__(**kwargs)
        self.ui = self.import_ui()
        self.init_ui()
        return

    def import_ui(self):
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    def change_entity_items(self):
        scene_process = self.ui.process_cbx.currentText()
        scene_process_folder = self.scene_dict[scene_process]

        scene_process_dir = path(r"{}{}{}".format(
            self.project_path,
            "/scenes/",
            scene_process_folder
        ))

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
        scene = "/".join([
            "scenes",
            self.scene_dict[self.ui.process_cbx.currentText()],
            self.ui.asset_cbx.currentText()
        ])
        alembic = "scenes/06_Cache/08_Animation/{}".format(self.ui.asset_cbx.currentText())
        self.set_project(scene=scene, alembic=alembic)

        if self.ui.checkout_cbx.currentText() == "Published File":
            self.published_file()
        elif self.ui.checkout_cbx.currentText() == "Working File":
            self.processed_file()

        self.ui.close()
        return

    def init_ui(self):
        self.ui.process_cbx.currentTextChanged.connect(self.change_entity_items)

        items = [item[3:] for item in sorted(self.scene_dict.values())]
        self.ui.process_cbx.addItems(items)

        self.ui.checkout_btn.clicked.connect(self.checkout)
        return
