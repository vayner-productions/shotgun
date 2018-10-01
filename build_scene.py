"""
checks the latest file in a scene process
option to check latest published file on sg and latest file in directory

from shotgun import build_scene as sg
reload(sg)
sg.get_window()

*

how do you handle variations
is there an instance where model is brought in twice
what do you want to see --
what are the attributes it should address --
- variation
- rollback
- status
"""
from PySide2 import QtCore, QtWidgets, QtUiTools, QtGui
import pymel.core as pm
import sgtk
import os
import collections

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

    def dropdown_menu(self):
        dictionary = {
            "Models": "01_Assets",
            "Rigs": "02_Rigs"
        }
        scene_process = dictionary[self.ui.assets_cbx.currentText()]

        # get all the available assets on sg
        items = []
        dir = r"{}/published/{}".format(pm.workspace.path, scene_process)
        for dir in os.listdir(dir):
            items += [dir]

        # search without case sensitivity
        show = []
        text = self.ui.assets_lne.text().lower()
        for item in items:
            if text in item.lower():
                show += [item]

        # keep the list view fresh upon every new input
        self.ui.assets_lst.clear()
        self.ui.assets_lst.addItems(show)
        return

    def add_assets(self):
        font = QtGui.QFont("MS Shell Dlg 2")
        font.setPointSize(12)

        selection = self.ui.assets_lst.selectedItems()
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Preferred)

        num = self.ui.scrollAreaLayout.rowCount()
        if selection:
            for sel in selection:
                label = QtWidgets.QLabel("")
                label.setMinimumSize(20, 20)
                label.setStyleSheet("background-color: None")
                label.setObjectName("status_{}_wgt".format(num))

                field = QtWidgets.QLabel(sel.text())
                field.setFont(font)
                field.setSizePolicy(size_policy)
                field.setObjectName("status_{}_lbl".format(num))

                self.ui.scrollAreaLayout.insertRow(num, label, field)
                num += 1
        return

    def add_context_menu(self):
        # right click for context menu, reveals 'Add' action
        # adds to Reference element

        # selects item cursor is on, preserves previous selection
        position = self.ui.assets_lst.mapFromGlobal(QtGui.QCursor.pos())
        widget = self.ui.assets_lst.itemAt(position)
        self.ui.assets_lst.setItemSelected(widget, 1)

        # shows context menu
        menu = QtWidgets.QMenu()
        action = QtWidgets.QAction("Add", menu)
        menu.addAction(action)
        action.triggered.connect(self.add_assets)
        menu.exec_(QtGui.QCursor.pos())
        return

    def remove_elements(self):
        # remove elements from row based on object name correspondence
        position = QtGui.QCursor.pos()
        widget = QtWidgets.QApplication.widgetAt(position)
        label_field = {
            "_lbl": "_wgt",
            "_wgt": "_lbl"
        }
        if isinstance(widget, QtWidgets.QLabel):
            key = widget.objectName()[-4:]
            value = label_field[key]
            name = widget.objectName()[:-4] + value
            row = int(name.rsplit("_", 2)[1])
            other = self.ui.findChild(QtWidgets.QLabel, name)

            widget.deleteLater()
            other.deleteLater()
        return

    def remove_context_menu(self):
        # creates right-click "Add" feature
        menu = QtWidgets.QMenu()
        action = QtWidgets.QAction("Remove", menu)
        menu.addAction(action)
        action.triggered.connect(self.remove_elements)
        menu.exec_(QtGui.QCursor.pos())
        return

    def add_shot(self, scene_process):
        font = QtGui.QFont("MS Shell Dlg 2")
        font.setPointSize(12)

        selection = {
            "Camera": "03_Cameras",
            "Layout": "04_Layouts",
            "Dynamics": "05_Dynamics",
            "Animation": "08_Animation"
        }
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Preferred)
        num = self.ui.scrollAreaLayout.rowCount()

        label = QtWidgets.QLabel("")
        label.setMinimumSize(20, 20)
        label.setStyleSheet("background-color: None")
        label.setObjectName("status_{}_wgt".format(num))

        field = QtWidgets.QLabel(selection[scene_process])
        field.setFont(font)
        field.setSizePolicy(size_policy)
        field.setObjectName("status_{}_lbl".format(num))

        self.ui.scrollAreaLayout.insertRow(num, label, field)
        return

    def add_references(self):
        font = QtGui.QFont("MS Shell Dlg 2")
        font.setPointSize(12)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Preferred)
        num = self.ui.scrollAreaLayout.rowCount()
        # add references
        for ref in pm.listReferences():
            item, status = None, "blue"

            # get item using reference node
            # use name for rigs and assets
            # use scene process for everything else
            if ("01_Assets" in ref.path) or ("02_Rigs" in ref.path):
                item = ref.refNode.rsplit("_", 1)[0]
                if "original" in item or "processed" in item:
                    item = item.rsplit("_", 1)[0]
            else:
                item = ref.path.dirname().rsplit("/", 2)[1]

            # get status: yellow/update; blue/latest
            # filters through name.#.ext and name_#.ext
            latest = None
            name = current = ref.path.basename().stripext()
            if len(current.splitall()) == 2 and current.ext[1:].isdigit():
                # name.####
                name = current.split(".")[0]
                current = int(current.ext[1:])
            elif len(current.rsplit("_", 1)) == 2 and current.rsplit("_", 1)[1].isdigit():
                # name_####
                name = current.rsplit("_", 1)[0]
                current = int(current.rsplit("_", 1)[1])

            pattern = "*{}*{}".format(name, ref.path.ext)
            files = ref.path.dirname().files(pattern)

            if files:
                latest = max(files, key=os.path.getctime)

            if current < latest:
                status = "yellow"

            # create ui
            label = QtWidgets.QLabel("")
            label.setMinimumSize(20, 20)
            label.setStyleSheet("background-color:" + status)
            label.setObjectName("status_{}_wgt".format(num))

            field = QtWidgets.QLabel(item)
            field.setFont(font)
            field.setSizePolicy(size_policy)
            field.setObjectName("status_{}_lbl".format(num))

            self.ui.scrollAreaLayout.insertRow(num, label, field)
            num += 1
        return

    def build(self):
        elements, latest = {}, []

        # find corresponding ui objects _wgt and _lbl
        # skip those with the latest publish and/or those without a label
        rx = QtCore.QRegExp("*_wgt")
        rx.setPatternSyntax(QtCore.QRegExp.Wildcard)
        for child in self.ui.findChildren(QtWidgets.QLabel, rx):
            color = child.palette().color(QtGui.QPalette.Background)
            label = self.ui.findChild(QtWidgets.QLabel, child.objectName().replace("_wgt", "_lbl"))

            if color == QtGui.QColor(0, 0, 255, 255):
                continue
            if not label:
                continue
            # elements += [child.objectName()]
            # elements += [label.objectName()]
            elements[child] = label.text()

        for e in elements.values():
            # get scene process
            scene_process, asset = e, e
            sg_asset_type = None
            if len(e.split("_", 1)[0]) == 3:
                sg_asset_type = sg.find_one("Asset",
                                            [["project", "is", project],
                                             ["code", "is", e]],
                                            ["sg_asset_type"])["sg_asset_type"]
            elif e.count("_") == 0:
                # in case element's 3-numbered prefix is removed
                # ###_name --> name
                sg_asset_type = sg.find_one("Asset",
                                            [["project", "is", project],
                                             ["code", "ends_with", e]],
                                            ["sg_asset_type"])["sg_asset_type"]
            if sg_asset_type == "CG Model":
                scene_process = "01_Assets"
            elif sg_asset_type == "CG Rig":
                scene_process = "02_Rigs"

            # create path with exception for animation (referencing from 06_Cache)
            reference_path = pm.workspace.path
            shot = pm.workspace.fileRules["scene"].rsplit("/", 1)[1]
            if (scene_process == "01_Assets") or (scene_process == "02_Rigs"):
                reference_path += "/published/{}/{}".format(scene_process, asset)
            elif scene_process == "08_Animation":
                reference_path += "/scenes/06_Cache/08_Animation/{}".format(shot)
            else:
                reference_path += "/published/{}/{}".format(scene_process, shot)

            # find the latest file
            files = reference_path.files("*.ma")
            if not files:
                files = reference_path.files("*.abc")
            latest += [max(files, key=os.path.getctime)]

        print "Referencing the following:"
        for f, wgt in zip(latest, elements.keys()):
            print ">>", f
            wgt.setStyleSheet("background-color: None")
        # what about broken links? only with custom
        # to identify shot or asset, check the length of the first split on "_"
        return

    def init_ui(self):
        self.add_references()
        self.dropdown_menu()

        self.ui.assets_lne.textChanged.connect(self.dropdown_menu)
        self.ui.assets_cbx.currentIndexChanged.connect(self.dropdown_menu)

        self.ui.assets_lst.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.assets_lst.customContextMenuRequested.connect(self.add_context_menu)

        self.ui.scrollAreaWidgetContents.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.scrollAreaWidgetContents.customContextMenuRequested.connect(self.remove_context_menu)

        self.ui.camera_btn.clicked.connect(lambda x="Camera": self.add_shot(x))
        self.ui.layout_btn.clicked.connect(lambda x="Layout": self.add_shot(x))
        self.ui.dynamics_btn.clicked.connect(lambda x="Dynamics": self.add_shot(x))
        self.ui.animation_btn.clicked.connect(lambda x="Animation": self.add_shot(x))

        self.ui.build_btn.clicked.connect(self.build)
        return

    def setup_ui(self):
        return

    def run(self):
        # self.ui.close()
        pass
