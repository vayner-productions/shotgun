import sgtk
from pymel.core.system import workspace
from pymel.util.common import path
import maya.mel as mel
from PySide2 import QtCore, QtWidgets, QtUiTools

eng = sgtk.platform.current_engine()
project_name = eng.context.project["name"]
sg = eng.shotgun
root = None


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
        self.project_path = None
        self.get_project_path()
        self.scene_dict = {}
        self.init_ui()

    def import_ui(self):
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    def get_project_path(self):
        # used for remote-work, change the root variable
        if root:
            self.project_path = root
            return

        # used for in-office development
        client_brand, sub_brand = [
            sg.find_one("Project", [["name", "is", project_name]], [i, "name"])[i]["name"] for i in
            ["sg_client", "sg_brand"]]
        client_brand = client_brand
        self.project_path = r"A:/Animation/Projects/Client/{}/{}/{}/Project Directory/02_Production/04_Maya".format(
            client_brand, sub_brand, project_name)
        return

    def add_scene_items(self):
        scene_dir = self.project_path + "/scenes"
        scene_subfolders = {r"{}".format(sub.basename()) for sub in path(scene_dir).dirs()}
        exclude = {"edits",
                   "03_Cameras",
                   # "04_Layouts",
                   "06_Cache",
                   "None"}

        self.scene_dict = {sub[3:]: sub for sub in sorted(list(scene_subfolders.difference(exclude)))}
        self.ui.scene_cbx.addItems(self.scene_dict.keys())
        return

    def change_entity_items(self):
        scene_process = self.ui.scene_cbx.currentText()
        scene_process_folder = self.scene_dict[scene_process]

        scene_process_dir = path(r"{}{}{}".format(
            self.project_path,
            "/scenes/",
            scene_process_folder))

        self.ui.asset_cbx.clear()
        for dir in scene_process_dir.dirs():
            folder = dir.basename()
            if "Archive" not in folder:
                self.ui.asset_cbx.addItem(folder)
        return

    def set_project(self):
        workspace.open(self.project_path)

        workspace.fileRules["scene"] = "/".join([
            "scenes",
            self.scene_dict[self.ui.scene_cbx.currentText()],
            self.ui.asset_cbx.currentText()])

        if "Shot" in self.ui.asset_cbx.currentText():
            workspace.fileRules["Alembic"] = "scenes/06_Cache/08_Animation/{}".format(self.ui.asset_cbx.currentText())

            workspace.fileRules["shaders"] = "data/001_Shaders"

        mel.eval('setProject \"' + self.project_path + '\"')
        self.ui.close()
        print ">> project set",
        return

    def init_ui(self):
        self.ui.scene_cbx.currentTextChanged.connect(self.change_entity_items)
        self.add_scene_items()
        self.ui.set_project_btn.clicked.connect(self.set_project)
        return
