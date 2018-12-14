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
root = r"/Users/kathyhnali/Documents/Clients/Vayner Production/04_Maya"


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
        frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        frame.setMaximumWidth(100)
        frame.setFrameShape(QtWidgets.QFrame.Box)
        frame.setFrameShadow(QtWidgets.QFrame.Plain)
        frame.setLineWidth(3)
        if current is None:
            frame.setStyleSheet("color:rgb(255,255,102)")  # first publish available, add to scene
        elif items.index(current) != 0:
            frame.setStyleSheet("color:rgb(255,165,0)")  # new publish available

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

#TODO: SET LATEST
#TODO: LOAD TO EMPTY SCENE
#TODO: LOAD TO HALF FILLED SCENE
#TODO: LOAD TO FILLED HALF UPDATED SCENE
#TODO: ROLLBACK
    def init_ui(self):
        references = []
        type = "Shot"
        scene_process, entity = pm.workspace.fileRules["scene"].split("/")[1:]
        if "01" in scene_process or "02" in scene_process:
            type = "Asset"

        # add render camera for any shot scene process
        if type == "Shot":
            number = 1
            asset_name = "Render Camera"
            publish = sg.find_one(type, [["project", "is", project]], ["sg_tracked_camera"])[
                "sg_tracked_camera"]

            if publish is not None:
                publish = publish["local_path_windows"]
                current = publish.split(".")[1]

                # root switching
                if root:
                    publish = publish.replace("\\", "/").split("04_Maya")
                    publish = "".join([root, publish[1]])

                files = pm.util.common.path(publish).dirname().files("*.ma")
                items = sorted([f.split(".")[1] for f in files])[::-1]
                references += [[number, asset_name, current, items]]

        # add cache to lighting scene process
        if "Lighting" in scene_process:
            number = 1
            asset_name = "Alembic Cache"
            publish = sg.find_one(type, [["project", "is", project]], ["sg_alembic_cache"])[
                "sg_alembic_cache"]

            if publish is not None:
                publish = publish["local_path_windows"]
                current = publish.split(".")[1]

                # root switching
                if root:
                    publish = publish.replace("\\", "/").split("04_Maya")
                    publish = "".join([root, publish[1]])

                files = pm.util.common.path(publish).dirname().files("*.ma")
                items = sorted([f.split(".")[1] for f in files])[::-1]
                references += [[number, asset_name, current, items]]

            # CREATE ROWS WITH QUERIED DATA
            index = 0  # first row is the header
            for ast in references:
                index += 1  # which row
                ast.append(index)
                row = self.create_row(*ast)
                self.ui.central_vlayout.insertWidget(index, row)
            return

        # add assets to every scene process except lighting
        assets = sg.find_one(type,
                             [["project", "is", project],
                              ["code", "is", entity]],
                             ["assets"])["assets"]

        for asset in assets:
            # create row only if published file exists
            publish = None
            try:
                publish = sg.find_one("Asset",  # every scene process references assets
                                      [["id", "is", asset["id"]]],
                                      ["sg_file"])["sg_file"]["local_path_windows"]
            except:
                continue

            # root switching
            if root:
                publish = publish.replace("\\", "/").split("04_Maya")
                publish = "".join([root, publish[1]])

            # QUERY DATA FOR ROWS
            number = len([ref[1] for ref in references]) + 1  # times same asset is used
            asset_name = asset["name"]

            # combo items
            files = pm.util.common.path(publish).dirname().files("*.ma")
            items = sorted([f.split(".")[1] for f in files])[::-1]

            # combo current text
            match = 0
            current = None
            for ref in pm.listReferences():
                if asset_name == ref.path.dirname().basename():
                    match += 1
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
            self.ui.central_vlayout.insertWidget(index, row)
        return

    def setup_ui(self):
        return
