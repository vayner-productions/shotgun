"""
TODO: IN ANIMATION, UPDATE "alembicCache" FILE RULLE cache/alembic --> scenes/06_Cache/08_Animation/Shot_###
"""
from . import *
from PySide2 import QtCore, QtWidgets, QtUiTools
from pymel.util import path
from pymel.core.system import Workspace, warning
workspace = Workspace()


def get_window():
    global mw
    try:
        mw.ui.close()
    except:
        pass

    mw = MyWindow()
    mw.ui.show()


class SetProject:
    def __init__(self, process=None, entity=None):
        # --- process / entity_type ---
        template = [
            "00_Tests",
            "01_Assets",
            "02_Rigs",
            "03_Cameras",
            "04_Layouts",
            "05_Dynamics",
            "06_Cache",
            "07_Lighting",
            "08_Animation"
        ]

        for dir in template:
            if process.lower() in dir.lower():
                self.process = dir
                break

        if self.process is "01_Assets" or self.process is "02_Rigs":
            self.entity_type = "Asset"
        elif self.process is "00_Tests":
            pass
        else:
            self.entity_type = "Shot"

        # --- entity ---
        self.entity = sg.find_one(
            self.entity_type,  # Asset / Shot
            [["project", "is", project], ["code", "ends_with", entity.lower()]],
            ["code"]
        )

        # --- project_path ---
        # used for remote-work, change the root variable
        if root:
            self.project_path = path(root).normpath()
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
            media_space, client_brand, sub_brand, project_name)

        self.project_path = path(project_path).normpath()
        return


class MyWindow(QtWidgets.QDialog):
    def __init__(self):
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

    def init_ui(self):
        self.ui.asset_cbx
        self.ui.scene_cbx
        self.ui.set_project_btn
        return
