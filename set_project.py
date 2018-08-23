import sgtk
from pymel.core.system import workspace
import maya.mel as mel
import os
from PySide2 import QtCore, QtWidgets, QtUiTools

eng = sgtk.platform.current_engine()
project_name = eng.context.project["name"]
sg = eng.shotgun


def get_project_path():
    client_brand, sub_brand = [
        sg.find_one("Project", [["name", "is", project_name]], [i, "name"])[i]["name"] for i in
        ["sg_client", "sg_brand"]]
    client_brand = client_brand[-8:]
    project_path = r"A:/Animation/Projects/Client/{}/{}/{}/Project Directory/02_Production/04_Maya".format(
        client_brand, sub_brand, project_name)
    return project_path


def get_subfolders(full_path=None, parent_folder=None):
    subfolders = [x for x in os.listdir(full_path)]
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


def set_project(project_path=None, scene_path=None, alembic_cache=None):
    # set workspace to project path and scene to scene path

    # scenes
    workspace.open(project_path)
    if scene_path:
        workspace.fileRules["scene"] = scene_path
    else:
        workspace.fileRules["scene"] = "scenes"

    # images
    scene_path_basename = os.path.basename(scene_path)
    if "Shot_" in scene_path_basename:
        workspace.fileRules["images"] = "images/" + scene_path_basename
    else:
        workspace.fileRules["images"] = "images"

    # alembic
    if alembic_cache:
        cache_folder = [fld for fld in os.listdir(workspace.path + "/scenes") if "Cache" in fld][
            0]
        alembic_directory = "{}/{}/{}".format(workspace.path, cache_folder, alembic_cache)
        workspace.fileRules["alembicCache"] = alembic_directory

    # project
    mel.eval('setProject \"' + project_path + '\"')
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
        self.scene_processes, self.asset_types, self.scene_path = None, None, None
        self.project_path = get_project_path() + "/scenes"
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

    def init_ui(self):
        self.scene_processes = get_subfolders(self.project_path, parent_folder="scenes")
        self.ui.scene_cbx.addItems(sorted(self.scene_processes))
        self.ui.scene_cbx.currentIndexChanged.connect(self.setup_ui)
        self.ui.set_project_btn.clicked.connect(self.run)
        return

    def setup_ui(self):
        self.scene_path = self.project_path + "/" + self.ui.scene_cbx.currentText()
        pfld = self.ui.scene_cbx.currentText().split("_", 1)[1]
        self.asset_types = get_subfolders(self.scene_path, parent_folder=pfld)
        self.ui.asset_cbx.clear()
        self.ui.asset_cbx.addItems(sorted(self.asset_types))
        return

    def run(self):
        s_path, ac_path = self.scene_path, None
        if self.ui.asset_cbx.currentText():
            s_path = self.scene_path + "/" + self.ui.asset_cbx.currentText()
            ac_path = self.ui.asset_cbx.currentText()
        set_project(project_path=get_project_path(),
                    scene_path=s_path,
                    alembic_cache=ac_path)
        self.ui.close()
        print ">> project set"
        # print ">> scene directory:", self.scene_path
