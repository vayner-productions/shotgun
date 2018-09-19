"""
checks the latest file in a scene process
option to check latest published file on sg and latest file in directory

from shotgun import build_scene as sg
reload(sg)
sg.get_window()
"""
from PySide2 import QtCore, QtWidgets, QtUiTools, QtGui
import pymel.core as pm
import sgtk
import os

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

    def get_arrow_type(self, toolbox):
        open = 0
        if toolbox.arrowType() == QtCore.Qt.ArrowType.RightArrow:
            open = 1
        return open

    def set_arrow_type(self, toolbox, open):
        if open:
            toolbox.setArrowType(QtCore.Qt.DownArrow)
        else:
            toolbox.setArrowType(QtCore.Qt.RightArrow)
        return

    def layout_row(self, index, name, start, items, combo):
        layout_name = "{}_{}_lyt".format(name, start)
        hbox = self.ui.scrollAreaLayout.findChild(QtWidgets.QHBoxLayout, layout_name)
        if hbox:
            for i in range(3):
                hbox.itemAt(i).widget().show()
            hbox.setContentsMargins(3, 3, 3, 3)
        else:
            font = QtGui.QFont("Arial", 14)

            label_name = name.replace("_", " ")
            label = QtWidgets.QLabel(label_name)
            label.setFont(font)
            label_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                                      QtWidgets.QSizePolicy.Preferred)
            label.setSizePolicy(label_size_policy)

            combox = QtWidgets.QComboBox()
            combox.addItems(items)
            combox.setCurrentIndex(combo)
            combox.setFont(font)
            combox_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                                       QtWidgets.QSizePolicy.Preferred)
            combox.setSizePolicy(combox_size_policy)
            combox.setFixedWidth(80)

            update_btn = QtWidgets.QPushButton("Update Available")
            update_btn.setFont(font)
            update_btn.setSizePolicy(combox_size_policy)

            layout = QtWidgets.QHBoxLayout()
            layout.setContentsMargins(3, 3, 3, 3)
            # layout_name = "{}_{}_lyt".format(name, start)
            layout.setObjectName(layout_name)
            layout.addWidget(label)
            layout.addWidget(combox)
            layout.addWidget(update_btn)

            self.ui.scrollAreaLayout.insertLayout(index, layout)
        return

    def modeling(self):
        # proccess data from shotgun
        # get asset name and its file, file directory
        assets_processed = {}

        assets = sg.find("Asset",
                         [["project", "is", project],
                          ["sg_asset_type", "is", "CG Model"]],
                         ["code", "sg_file"])

        for a in assets:
            combo, versions = None, []

            combo_current = a["sg_file"]["local_path"]
            asset_dir = os.path.dirname(combo_current).replace("published", "scenes")
            for f in os.listdir(asset_dir):
                if (len(f.split(".")) == 3) and ("{}_processed.".format(a["code"][4:]) in f):
                    versions += [f.split(".")[1]]

                    combo_key = os.path.basename(combo_current).replace("original", "processed")
                    if combo_key == f:
                        combo = os.listdir(asset_dir).index(combo_key)

            assets_processed[a["code"]] = {
                "combo": combo,
                "versions": versions
            }

        # then build out the ui
        # adding/removing layouts as needed
        toolbox_index = 1  # refers to commands variable
        toolbox = self.ui.scrollAreaWidgetContents.children()[toolbox_index]
        for l in self.ui.scrollAreaWidgetContents.children():
            if l.objectName() == "modeling_tbx":
                toolbox_index = self.ui.scrollAreaLayout.indexOf(l)
                toolbox = l
        closed = self.get_arrow_type(toolbox)
        self.set_arrow_type(toolbox, closed)

        if closed:
            index = self.ui.scrollAreaLayout.indexOf(toolbox)
            delete_tbx = True

            for a in assets_processed:
                name = a[4:]
                start = 1
                items = assets_processed[a]["versions"]
                combo = assets_processed[a]["combo"]
                if items:
                    index += 1
                    self.layout_row(index, name, start, items, combo)
                    delete_tbx = False

            if delete_tbx:
                layout_name = "modeling_tbx"
                tbx = self.ui.scrollAreaWidgetContents.findChild(QtWidgets.QToolButton,
                                                                 layout_name)
                tbx.deleteLater()
        else:
            layouts_to_hide = []
            toolbox_key = "_{}_".format(1)

            for l in self.ui.scrollAreaLayout.children():
                if toolbox_key in l.objectName():
                    layouts_to_hide += [l]
                    for i in range(3):
                        l.itemAt(i).widget().hide()
                    l.setContentsMargins(0, 0, 0, 0)
        return

    def rigs(self):
        # proccess data from shotgun
        # get asset name and its file, file directory
        assets_processed = {}

        assets = sg.find("Asset",
                         [["project", "is", project],
                          ["sg_asset_type", "is", "CG Rig"]],
                         ["code", "sg_file"])

        for a in assets:
            combo, versions = None, []

            combo_current = a["sg_file"]["local_path"]
            asset_dir = os.path.dirname(combo_current).replace("published", "scenes")
            for f in os.listdir(asset_dir):
                if (len(f.split(".")) == 3) and ("{}_processed.".format(a["code"][4:]) in f):
                    versions += [f.split(".")[1]]

                    combo_key = os.path.basename(combo_current).replace("original", "processed")
                    if combo_key == f:
                        combo = os.listdir(asset_dir).index(combo_key)

            assets_processed[a["code"]] = {
                "combo": combo,
                "versions": versions
            }

        # then build out the ui
        # adding/removing layouts as needed
        toolbox_index = 2  # refers to commands variable
        toolbox = self.ui.scrollAreaWidgetContents.children()[toolbox_index]
        for l in self.ui.scrollAreaWidgetContents.children():
            if l.objectName() == "rigs_tbx":
                toolbox_index = self.ui.scrollAreaLayout.indexOf(l)
                toolbox = l
        closed = self.get_arrow_type(toolbox)
        self.set_arrow_type(toolbox, closed)

        if closed:
            index = self.ui.scrollAreaLayout.indexOf(toolbox)
            delete_tbx = True

            for a in assets_processed:
                name = a[4:]
                start = 2
                items = assets_processed[a]["versions"]
                combo = assets_processed[a]["combo"]
                if items:
                    index += 1  # in case items are empty, avoids appearing in another tab
                    self.layout_row(index, name, start, items, combo)
                    delete_tbx = False

            if delete_tbx:
                layout_name = "rigs_tbx"
                tbx = self.ui.scrollAreaWidgetContents.findChild(QtWidgets.QToolButton,
                                                                 layout_name)
                tbx.deleteLater()
        else:
            layouts_to_hide = []
            toolbox_key = "_{}_".format(2)

            for l in self.ui.scrollAreaLayout.children():
                if toolbox_key in l.objectName():
                    layouts_to_hide += [l]
                    for i in range(3):
                        l.itemAt(i).widget().hide()
                    l.setContentsMargins(0, 0, 0, 0)
        return

    def cameras(self):
        # proccess data from shotgun
        # get asset name and its file, file directory
        assets = sg.find_one("Shot",
                             [["project", "is", project],
                              ["code", "is", pm.workspace.fileRules["scene"].split("/")[-1]]],
                             ["sg_tracked_camera"])

        combo_current = assets["sg_tracked_camera"]["local_path"]
        asset_dir = os.path.dirname(combo_current).replace("published", "scenes")
        versions, combo = [], None
        shot_name = asset_dir.rsplit("\\", 1)[1]
        file_name = "{}_processed.".format(shot_name)
        for f in os.listdir(asset_dir):
            if (len(f.split(".")) == 3) and (file_name in f):
                versions += [f.split(".")[1]]

                combo_key = os.path.basename(combo_current).replace("original", "processed")
                if combo_key == f:
                    combo = os.listdir(asset_dir).index(combo_key)

        # then build out the ui
        # adding/removing layouts as needed
        toolbox_index = 3  # refers to commands variable
        toolbox = self.ui.scrollAreaWidgetContents.children()[toolbox_index]
        for l in self.ui.scrollAreaWidgetContents.children():
            if l.objectName() == "cameras_tbx":
                toolbox_index = self.ui.scrollAreaLayout.indexOf(l)
                toolbox = l
        closed = self.get_arrow_type(toolbox)
        self.set_arrow_type(toolbox, closed)

        if closed:
            index = self.ui.scrollAreaLayout.indexOf(toolbox)
            for a in [shot_name]:
                index += 1
                name = a
                start = 3
                items = versions
                if items:
                    self.layout_row(index, name, start, items, combo)
                else:
                    layout_name = "cameras_tbx"
                    tbx = self.ui.scrollAreaWidgetContents.findChild(QtWidgets.QToolButton,
                                                                     layout_name)
                    tbx.deleteLater()
        else:
            layouts_to_hide = []
            toolbox_key = "_{}_".format(3)

            for l in self.ui.scrollAreaLayout.children():
                if toolbox_key in l.objectName():
                    layouts_to_hide += [l]
                    for i in range(3):
                        l.itemAt(i).widget().hide()
                    l.setContentsMargins(0, 0, 0, 0)
        return

    def layouts(self):
        scene_dir = pm.workspace.expandName(pm.workspace.fileRules["scene"]).rsplit("/", 2)
        scene_dir[1] = "04_Layouts"
        scene_dir = "/".join(scene_dir)
        versions = []
        shot_name = scene_dir.rsplit("/", 1)[1]
        file_name = "{}_processed.".format(shot_name)
        for f in os.listdir(scene_dir):
            if (len(f.split(".")) == 3) and (file_name in f):
                versions += [f.split(".")[1]]
        versions = sorted(versions)

        # then build out the ui
        # adding/removing layouts as needed
        toolbox_index = 4  # refers to commands variable
        toolbox = self.ui.scrollAreaWidgetContents.children()[toolbox_index]
        for l in self.ui.scrollAreaWidgetContents.children():
            if l.objectName() == "layouts_tbx":
                toolbox_index = self.ui.scrollAreaLayout.indexOf(l)
                toolbox = l
        closed = self.get_arrow_type(toolbox)
        self.set_arrow_type(toolbox, closed)

        if closed:
            index = self.ui.scrollAreaLayout.indexOf(toolbox)
            for a in [shot_name]:
                index += 1
                name = a
                start = 4
                items = versions
                combo = len(versions) - 1  # not on sg
                if items:
                    self.layout_row(index, name, start, items, combo)
                else:
                    layout_name = "layouts_tbx"
                    tbx = self.ui.scrollAreaWidgetContents.findChild(QtWidgets.QToolButton,
                                                                     layout_name)
                    tbx.deleteLater()
        else:
            layouts_to_hide = []
            toolbox_key = "_{}_".format(4)

            for l in self.ui.scrollAreaLayout.children():
                if toolbox_key in l.objectName():
                    layouts_to_hide += [l]
                    for i in range(3):
                        l.itemAt(i).widget().hide()
                    l.setContentsMargins(0, 0, 0, 0)
        return

    def dynamics(self):
        scene_dir = pm.workspace.expandName(pm.workspace.fileRules["scene"]).rsplit("/", 2)
        scene_dir[1] = "05_Dynamics"
        scene_dir = "/".join(scene_dir)
        versions = []
        shot_name = scene_dir.rsplit("/", 1)[1]
        file_name = "{}_processed.".format(shot_name)
        for f in os.listdir(scene_dir):
            if (len(f.split(".")) == 3) and (file_name in f):
                versions += [f.split(".")[1]]
        versions = sorted(versions)

        # then build out the ui
        # adding/removing layouts as needed
        toolbox_index = 5  # refers to commands variable
        toolbox = self.ui.scrollAreaWidgetContents.children()[toolbox_index]
        for l in self.ui.scrollAreaWidgetContents.children():
            if l.objectName() == "dynamics_tbx":
                toolbox_index = self.ui.scrollAreaLayout.indexOf(l)
                toolbox = l
        closed = self.get_arrow_type(toolbox)
        self.set_arrow_type(toolbox, closed)

        if closed:
            index = self.ui.scrollAreaLayout.indexOf(toolbox)
            for a in [shot_name]:
                index += 1
                name = a
                start = 5
                items = versions
                combo = len(versions) - 1
                if items:
                    self.layout_row(index, name, start, items, combo)
                else:
                    layout_name = "dynamics_tbx"
                    tbx = self.ui.scrollAreaWidgetContents.findChild(QtWidgets.QToolButton,
                                                                     layout_name)
                    tbx.deleteLater()
        else:
            layouts_to_hide = []
            toolbox_key = "_{}_".format(5)

            for l in self.ui.scrollAreaLayout.children():
                if toolbox_key in l.objectName():
                    layouts_to_hide += [l]
                    for i in range(3):
                        l.itemAt(i).widget().hide()
                    l.setContentsMargins(0, 0, 0, 0)
        return

    def animation(self):
        # proccess data from shotgun
        # get asset name and its file, file directory
        assets = sg.find_one("Shot",
                             [["project", "is", project],
                              ["code", "is", pm.workspace.fileRules["scene"].split("/")[-1]]],
                             ["sg_maya_scene"])

        combo_current = assets["sg_maya_scene"]["local_path"]
        asset_dir = os.path.dirname(combo_current).replace("published", "scenes")
        versions, combo = [], None
        shot_name = asset_dir.rsplit("\\", 1)[1]
        file_name = "{}_processed.".format(shot_name)
        for f in os.listdir(asset_dir):
            if (len(f.split(".")) == 3) and (file_name in f):
                versions += [f.split(".")[1]]

                combo_key = os.path.basename(combo_current).replace("original", "processed")
                if combo_key == f:
                    combo = os.listdir(asset_dir).index(combo_key)

        # then build out the ui
        # adding/removing layouts as needed
        toolbox_index = 6  # refers to commands variable
        toolbox = self.ui.scrollAreaWidgetContents.children()[toolbox_index]
        for l in self.ui.scrollAreaWidgetContents.children():
            if l.objectName() == "animation_tbx":
                toolbox_index = self.ui.scrollAreaLayout.indexOf(l)
                toolbox = l
        closed = self.get_arrow_type(toolbox)
        self.set_arrow_type(toolbox, closed)

        if closed:
            index = self.ui.scrollAreaLayout.indexOf(toolbox)
            for a in [shot_name]:
                index += 1
                name = a
                start = 6
                items = versions
                if items:
                    self.layout_row(index, name, start, items, combo)
                else:
                    layout_name = "animation_tbx"
                    tbx = self.ui.scrollAreaWidgetContents.findChild(QtWidgets.QToolButton,
                                                                     layout_name)
                    tbx.deleteLater()
        else:
            layouts_to_hide = []
            toolbox_key = "_{}_".format(6)

            for l in self.ui.scrollAreaLayout.children():
                if toolbox_key in l.objectName():
                    layouts_to_hide += [l]
                    for i in range(3):
                        l.itemAt(i).widget().hide()
                    l.setContentsMargins(0, 0, 0, 0)
        return

    def init_ui(self):
        #TODO: add radio button to the side to know which are loading
        # make only the toolboxes relevant to the scene process visible
        current_process = pm.workspace.fileRules["scene"].split("/")[1][3:]
        create_accordian = ["Assets", "Rigs", "Cameras", "Layouts", "Dynamics", "Animation"]
        commands = [self.modeling, self.rigs, self.cameras, self.layouts, self.dynamics, self.animation]

        for p, c in zip(create_accordian, commands):
            if current_process == p:
                break

            # create accordian tabs
            if "Assets" == p:
                p = "Modeling"

            toolbox = QtWidgets.QToolButton()
            toolbox.setObjectName("{}_tbx".format(p.lower()))
            tbx_font = QtGui.QFont("Arial", 16)
            tbx_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                                    QtWidgets.QSizePolicy.Fixed)
            toolbox.setSizePolicy(tbx_size_policy)
            toolbox.setFont(tbx_font)
            toolbox.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
            toolbox.setArrowType(QtCore.Qt.RightArrow)
            toolbox.setStyleSheet("background:rgb(93, 93, 93)")
            toolbox.setText(p)
            toolbox.setAutoRaise(1)

            self.ui.scrollAreaLayout.addWidget(toolbox)

            toolbox.clicked.connect(c)

        spacer = QtWidgets.QSpacerItem(20, 2000, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.ui.scrollAreaLayout.addItem(spacer)

        self.modeling()
        self.rigs()
        self.cameras()
        self.layouts()
        self.dynamics()
        self.animation()
        return

    def setup_ui(self):
        return

    def run(self):
        # self.ui.close()
        pass
