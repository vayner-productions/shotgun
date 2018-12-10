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

    def create_row(self, row_object, number, asset_name):
        vlayout = QtWidgets.QVBoxLayout()

        font = QtGui.QFont("Arial", 14)

        # widget - horizontal hlayout, (0,3,6,3), 3 spacing
        row = QtWidgets.QWidget()
        row.setObjectName(row_object)
        row.setContentsMargins(0, 3, 6, 3)

        # label quant - max width 25, arial 14, align horizontal center, horizontal expanding
        num = QtWidgets.QLabel(number)
        num.setFont(font)
        num.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        num.setMaximumWidth(25)
        num.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        # label name - horizontal expanding, arial 14
        name = QtWidgets.QLabel(asset_name)
        name.setFont(font)
        name.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        # frame - horizontal fixed, style color blue, box plain 3, vertical hlayout
        frame = QtWidgets.QFrame()
        frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        frame.setFrameShape(QtWidgets.QFrame.Box)
        frame.setFrameShadow(QtWidgets.QFrame.Plain)
        frame.setLineWidth(3)
        frame.setLayout(vlayout)
        frame.setStyleSheet("color:blue")

        # combobox - horizontal expanding, arial 14, style color none,
        combo = QtWidgets.QComboBox()
        combo.setFont(font)
        combo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        combo.setStyleSheet("color:none")

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setSpacing(3)
        hlayout.addWidget(num)
        hlayout.addWidget(name)
        hlayout.addWidget(frame)
        hlayout.addWidget(combo)
        row.setLayout(hlayout)
        return row

    def init_ui(self):
        rx = QtCore.QRegExp("row_*")
        rx.setPatternSyntax(QtCore.QRegExp.Wildcard)
        index = len(self.ui.findChildren(QtWidgets.QWidget, rx)) + 1

        row = self.create_row()
        row.setObjectName("Row_01")
        self.ui.verticalLayout.insertWidget(index, row)
        # row = self.create_row()
        # self.ui.verticalLayout.insertWidget(row)
        return

    def setup_ui(self):
        return
