import sgtk
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
        self.init_ui()

    def import_ui(self):
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    def load_vayner(self):
        self.ui.close()
        return

    def load_tracked(self):
        self.ui.close()
        return

    def init_ui(self):
        self.ui.vayner_btn.clicked.connect(self.load_vayner)
        self.ui.tracked_btn.clicked.connect(self.load_tracked)
        return

"""
import pymel.util.common as common
root = r"A:\Animation\Shotgun\System\Tools\shotgun\render_cam_RIG"
vayner_camera = sorted(common.path(root).files("render_cam.*.ma"))[::-1][0]
"""