"""
TODO: IN ANIMATION, UPDATE "alembicCache" FILE RULLE cache/alembic --> scenes/06_Cache/08_Animation/Shot_###
"""
from . import *
from PySide2 import QtCore, QtWidgets, QtUiTools


def get_window():
    global mw
    try:
        mw.ui.close()
    except:
        pass

    mw = MyWindow()
    mw.ui.show()


class SetProject:
    def __init__(self, scenes=None):
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
