"""
checks for latest published version

from shotgun import build_scene as sg
reload(sg)
sg.get_window()
"""
from PySide2 import QtCore, QtWidgets, QtUiTools, QtGui
import pymel.core as pm
import sgtk

eng = sgtk.platform.current_engine()
sg = eng.shotgun
project = sg.find_one("Project", [["name", "is", eng.context.project["name"]]])


def get_window():
    global mw
    try:
        mw.ui.close()
    except:
        pass

    mw = MyWindow()
    mw.ui.show()
    return mw


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

    def create_row(self):
        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(3)

        font = QtGui.QFont("Arial", 14)

        # widget - horizontal layout, (0,3,6,3), 3 spacing
        row = QtWidgets.QWidget()
        row.setObjectName("ROW1")
        row.setLayout(layout)
        row.setContentsMargins(0, 3, 6, 3)

        # label quant - max width 25, arial 14, align horizontal center, horizontal expanding
        num = QtWidgets.QLabel("HHHH")
        num.setObjectName("num")
        # num.setFont(font)
        num.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        num.setMaximumWidth(25)
        num.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        num.setParent(row)
        # row.addWidget(num)

        # label name - horizontal expanding, arial 14
        # frame - horizontal fixed, style color blue, box plain 3, vertical layout
        # combobox - horizontal expanding, arial 14, style color none,
        return row

    def init_ui(self):
        self.ui.verticalLayout.
        # row = self.create_row()
        # self.ui.verticalLayout.insertWidget(row)
        return

    def setup_ui(self):
        return
