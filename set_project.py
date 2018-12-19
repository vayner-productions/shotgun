import sgtk
from pymel.core.system import workspace
from pymel.util.common import path
import maya.mel as mel
import os
from PySide2 import QtCore, QtWidgets, QtUiTools

eng = sgtk.platform.current_engine()
project_name = eng.context.project["name"]
sg = eng.shotgun
root = r"/Users/kathyhnali/Documents/Clients/Vayner Production/04_Maya"


def get_project_path(project_path=None):
    # used for remote-work, change the root variable
    if root:
        project_path = root
        return project_path

    # used for in-office development
    client_brand, sub_brand = [
        sg.find_one("Project", [["name", "is", project_name]], [i, "name"])[i]["name"] for i in
        ["sg_client", "sg_brand"]]
    client_brand = client_brand
    project_path = r"A:/Animation/Projects/Client/{}/{}/{}/Project Directory/02_Production/04_Maya".format(
        client_brand, sub_brand, project_name)
    return project_path


def get_subfolders(full_path=None, parent_folder=None):
    subfolders = os.listdir(full_path)
    if not parent_folder:
        return subfolders

    folders = []
    if parent_folder in ["scenes", "Tests", "Assets", "Rigs"]:
        for f in subfolders:
            if ("_" in f) and (os.path.isdir(full_path + "/" + f)):
                folders += [f]
    else:
        folders = [s for s in subfolders if s not in ["[Archive]"]]
    return folders


def set_project(project_path=None, scene_path=None, alembic_cache=""):
    # set workspace to project path and scene to scene path

    # scenes
    workspace.open(project_path)
    if scene_path:
        workspace.fileRules["scene"] = scene_path

    # alembic
    workspace.fileRules["Alembic"] = alembic_cache

    # shaders
    workspace.fileRules["shaders"] = "data/001_Shaders"

    # project
    mel.eval('setProject \"' + project_path + '\"')
    print ">> project set",
    return project_path, scene_path


def get_window():
    global mw
    try:
        mw.ui.close()
    except:
        pass

    mw = MyWindow()
    mw.ui.show()


class MyWindow(QtWidgets.QDialog):
    def __init__(self):
        self.ui = self.import_ui()
        self.init_ui()
        self.setup_ui()

    def import_ui(self):
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    def add_scene_items(self, project_path=root):
        # root allows for remote and in-office work
        # when set to None, you're working from office
        if root is None:
            project = sg.find_one("Project", [["name", "is", project_name]],
                                  ["sg_client", "sg_brand"])
            client_brand = project["sg_client"]["name"]
            sub_brand = project["sg_brand"]["name"]
            project_path = r"/".join(
                ["A:/Animation/Projects/Client",
                 client_brand,
                 sub_brand,
                 project_name,
                 "Project Directory/02_Production/04_Maya"]
            )

        scene_dir = project_path + "/scenes"
        scene_subfolders = sorted([dir.basename() for dir in path(scene_dir).dirs()])
        scene_items = [dir[3:] for dir in scene_subfolders]
        self.ui.scene_cbx.addItems(scene_items)
        self.ui.scene_cbx.setToolTip(scene_subfolders[0])

        # self.ui.scene_cbx.currentTextChanged.connect(self.ui.scene_cbx.setToolTip("s"))
        return

    def init_ui(self):
        self.add_scene_items()
        return

    def setup_ui(self):
        # self.ui.scene_cbx
        # self.ui.asset_cbx
        # self.ui.set_project_btn
        return
