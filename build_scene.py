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

    def arrow_type(self, toolbox):
        open = 0
        if toolbox.arrowType() == QtCore.Qt.ArrowType.RightArrow:
            toolbox.setArrowType(QtCore.Qt.DownArrow)
            open = 1
        else:
            toolbox.setArrowType(QtCore.Qt.RightArrow)
        return open

    def layout_row(self, index, name):
        font = QtGui.QFont("Arial", 14)
        cbx_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                                QtWidgets.QSizePolicy.Fixed)

        label_name = name.replace("_", " ")
        label = QtWidgets.QLabel(label_name)
        label.setFont(font)
        label_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                                  QtWidgets.QSizePolicy.Preferred)
        label.setSizePolicy(label_size_policy)

        publish_checkbox = QtWidgets.QCheckBox("Latest publish")
        publish_checkbox.setFont(font)
        publish_checkbox.setSizePolicy(cbx_size_policy)

        latest_checkbox = QtWidgets.QCheckBox("Latest file")
        latest_checkbox.setFont(font)
        latest_checkbox.setSizePolicy(cbx_size_policy)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(3, 3, 3, 3)
        layout_name = "{}_lyt".format(name)
        layout.setObjectName(layout_name)
        layout.addWidget(label)
        layout.addWidget(publish_checkbox)
        layout.addWidget(latest_checkbox)

        self.ui.verticalLayout_2.insertLayout(index, layout)
        return

    def expand(self, toolbox):
        is_open = self.arrow_type(toolbox)
        index = self.ui.verticalLayout_2.indexOf(toolbox)

        if is_open:
            assets = sg.find("Asset",
                             [["project", "is", project],
                              ["sg_asset_type", "is", "CG Model"]],
                             ["code"])

            for a in assets:
                name = a["code"][4:]
                index += 1
                self.layout_row(index, name)
        else:
            # index += 1
            # widget = self.ui.verticalLayout_2.itemAt(index)
            # while "_lyt" in widget.objectName():
            #     widget.deleteLater()
            #     index += 1
            #     widget = self.ui.verticalLayout_2.itemAt(index)
            #     print "> deleted:", widget.objectName()

        return

    def modeling(self):
        self.expand(self.ui.modeling_tbx)
        # publish_file = sg.find_one("Asset",
        #                            [["project", "is", project]],
        #                            ["sg_file"])["sg_file"]["local_path"]
        # dir = pm.workspace.expandName(pm.workspace.fileRules["scene"])
        # base_name = os.path.basename(dir)[4:] + "_processed."
        # files = []
        # for f in os.listdir(dir):
        #     if base_name in f:
        #         files += [dir + "/" + f]
        # latest_file = max(files, key=os.path.getctime)
        return
    
    def rigs(self):
        self.arrow_type(self.ui.rigs_tbx)
        return
    
    def cameras(self):
        self.arrow_type(self.ui.cameras_tbx)
        return

    def layouts(self):
        self.arrow_type(self.ui.layouts_tbx)
        return   
    
    def dynamics(self):
        self.arrow_type(self.ui.dynamics_tbx)
        return   
    
    def animation(self):
        self.arrow_type(self.ui.animation_tbx)
        return   

    def init_ui(self):
        # make only the toolboxes relevant to the scene process visible
        asset_processes = ["Assets", "Rigs"]
        shot_processes = ["Cameras", "Layouts", "Dynamics", "Animation", "Lighting"]
        current_process = pm.workspace.fileRules["scene"].split("/")[1][3:]

        # dynamics should appear in animation scene process as animation should in dynamics
        hide_processes = []
        if "Shot" in pm.workspace.fileRules["scene"]:
            for p in shot_processes[::-1]:
                hide_processes += [p]
                if current_process == p:
                    if "Dynamics" == current_process:
                        hide_processes.remove("Animation")
                    break
        else:
            hide_processes = shot_processes
            for p in asset_processes[::-1]:
                hide_processes += [p]
                if current_process in p:
                    break

        # hide widgets that match
        for i, p in enumerate(hide_processes):
            hide_processes[i] = "{}_tbx".format(p.lower())

        for child in self.ui.scrollAreaWidgetContents.children():
            for p in hide_processes:
                if p in child.objectName():
                    child.hide()

        self.ui.modeling_tbx.clicked.connect(self.modeling)
        self.ui.rigs_tbx.clicked.connect(self.rigs)
        self.ui.cameras_tbx.clicked.connect(self.cameras)
        self.ui.layouts_tbx.clicked.connect(self.layouts)
        self.ui.dynamics_tbx.clicked.connect(self.dynamics)
        self.ui.animation_tbx.clicked.connect(self.animation)
        return

    def setup_ui(self):
        return

    def run(self):
        # self.ui.close()
        pass
