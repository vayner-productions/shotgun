"""
checks for latest published version

from shotgun import build_scene as sg
reload(sg)
sg.get_window()
"""
from PySide2 import QtCore, QtGui, QtWidgets, QtUiTools
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

    def create_row(self, number, asset_name, current, items, index):
        font = QtGui.QFont("Arial", 14)

        # widget - horizontal hlayout, (0,3,6,3), 3 spacing
        row = QtWidgets.QWidget()
        row.setObjectName("Row_{:02}".format(index))

        # label quant - max width 25, arial 14, align horizontal center, horizontal expanding
        num = QtWidgets.QLabel("{}".format(number))
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
        frame.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        frame.setFrameShape(QtWidgets.QFrame.Box)
        frame.setFrameShadow(QtWidgets.QFrame.Plain)
        frame.setLineWidth(3)
        if items.index(current) != 0:
            frame.setStyleSheet("color:orange")

        # combobox - horizontal expanding, arial 14, style color none,
        combo = QtWidgets.QComboBox()
        combo.setFont(font)
        combo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        combo.setStyleSheet("color:none")
        combo.setFrame(0)
        combo.addItems(items)
        combo.setCurrentText(current)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.setSpacing(0)
        vlayout.setContentsMargins(0, 0, 0, 0)

        vlayout.addWidget(combo)
        frame.setLayout(vlayout)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setSpacing(3)
        hlayout.setContentsMargins(0, 3, 6, 3)

        hlayout.addWidget(num)
        hlayout.addWidget(name)
        hlayout.addWidget(frame)

        row.setLayout(hlayout)
        row.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        if index % 2 == 0:
            row.setStyleSheet("background-color: rgb(128, 128, 128)")  # light
        else:
            row.setStyleSheet("background-color: rgb(115, 115, 115)")  # dark
        return row

    def init_ui(self):
        type = "Shot"
        scene_process, entity = pm.workspace.fileRules["scene"].split("/")[1:]
        if "01" in scene_process or "02" in scene_process:
            type = "Asset"

        assets = sg.find_one(type,
                             [["project", "is", project],
                              ["code", "is", entity]],
                             ["assets"])["assets"]

        references = []
        for asset in assets:
            # create row only if published file exists
            publish = sg.find_one(type,
                                  [["id", "is", asset["id"]]],
                                  ["sg_file"])["sg_file"]["local_path_windows"]
            if publish is None:
                break

            # QUERY DATA FOR ROWS
            number = len([ref[1] for ref in references]) + 1  # times same asset is used
            asset_name = asset["name"]

            # combo items
            files = []
            for ref in pm.listReferences():
                if asset_name == ref.path.dirname().basename():
                    files = ref.path.dirname().files("*.ma")
                    break

            items = []
            for f in files:
                items += [f.basename().split(".")[1]]
            items = sorted(items)[::-1]

            # combo current text
            match = 0
            current = None
            for ref in pm.listReferences():
                if asset_name == ref.path.dirname().basename():
                    match += 1
                    print match
                else:
                    continue

                if match == number:
                    current = ref.path.split(".")[1]
                    break
            references += [[number, asset_name, current, items]]

        # CREATE ROWS WITH QUERIED DATA
        index = 0  # first row is the header
        for ast in references:
            index += 1  # which row
            ast.append(index)
            row = self.create_row(*ast)
            self.ui.verticalLayout.insertWidget(index, row)
        #TODO: CHECK UI APPEARS CORRECT FOR ALL SCENE PROCESSES
        return

    def setup_ui(self):
        return
