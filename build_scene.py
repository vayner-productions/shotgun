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
        self.dictionary = collections.OrderedDict()
        self.dictionary["Assets"] = {
            "id": "01",
            "toolbox": self.ui.assets_tbx,
            "command": self.models
        }
        self.dictionary["Rigs"] = {
            "id": "02",
            "toolbox": self.ui.rigs_tbx,
            "command": self.rigs
        }
        self.dictionary["Cameras"] = {
            "id": "03",
            "toolbox": self.ui.cameras_tbx,
            "command": self.camera
        }
        self.dictionary["Layouts"] = {
            "id": "04",
            "toolbox": self.ui.layouts_tbx,
            "command": self.layout
        }
        self.dictionary["Dynamics"] = {
            "id": "05",
            "toolbox": self.ui.dynamics_tbx,
            "command": self.dynamics
        }
        self.dictionary["Animation"] = {
            "id": "08",
            "toolbox": self.ui.animation_tbx,
            "command": self.animation
        }
        self.dictionary["Lighting"] = {
            "id": "07",
            "toolbox": None,
            "command": None
        }
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

    def set_arrow(self, toolbutton, open=0):
        """
        tabs are initially expanded (arrow down) and closed (arrow right) when clicked again
        :param toolbutton: QToolButton object
        :param open: default closed
        :return:
        """
        if toolbutton.arrowType() == QtCore.Qt.ArrowType.RightArrow:
            open = 1

        if open:
            toolbutton.setArrowType(QtCore.Qt.DownArrow)
        else:
            toolbutton.setArrowType(QtCore.Qt.RightArrow)
        return

    def set_layout(self, name, items, index):
        """
        creates a single layout once, to store combo box selection in the event tabs expand/collapse
        :param name: name and number identifier, i.e. Shot_001_05 (05 for dynamics)
        :param items: dictionary, key as current index, value as items
        :param index: where the layout is placed in scroll area layout
        :return:
        """
        # checks if layout exists
        lyt = name + "_lyt"
        lyt = self.ui.scrollAreaLayout.findChild(QtWidgets.QHBoxLayout, lyt)
        if lyt:
            if lyt.itemAt(0).widget().isVisible():
                for i in range(4):
                    lyt.itemAt(i).widget().hide()
                lyt.setContentsMargins(0, 0, 0, 0)
            else:
                for i in range(4):
                    lyt.itemAt(i).widget().show()
                lyt.setContentsMargins(1, 1, 1, 1)
            return

        # create layout template
        font = QtGui.QFont("Arial", 14)

        chx_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                                QtWidgets.QSizePolicy.Fixed)
        chx = QtWidgets.QCheckBox()
        chx.setObjectName(name + "_chx")
        chx.setSizePolicy(chx_size_policy)
        chx.setFont(font)
        chx.setFixedWidth(20)

        lbl_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                                QtWidgets.QSizePolicy.Preferred)
        lbl = QtWidgets.QLabel()
        lbl.setObjectName(name + "_lbl")
        lbl.setSizePolicy(lbl_size_policy)
        lbl.setFont(font)
        lbl.setText(name[:-3])  # to remove the identifiers in the object names

        cbx_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                                QtWidgets.QSizePolicy.Fixed)
        cbx = QtWidgets.QComboBox()
        cbx.setObjectName(name + "_cbx")
        cbx.setSizePolicy(cbx_size_policy)
        cbx.setFont(font)
        cbx.setFixedWidth(90)
        cbx.addItems(items[1])
        cbx.setCurrentIndex(int(items[0]))

        clr_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                                QtWidgets.QSizePolicy.MinimumExpanding)
        clr = QtWidgets.QPushButton()
        clr.setObjectName(name + "_clr")
        clr.setSizePolicy(clr_size_policy)
        clr.setFont(font)
        clr.setFixedSize(27, 27)
        # clr.setStyleSheet("background: blue")

        lyt = QtWidgets.QHBoxLayout()
        lyt.setObjectName(name + "_lyt")
        lyt.setContentsMargins(3, 3, 3, 3)
        lyt.addWidget(chx)
        lyt.addWidget(lbl)
        lyt.addWidget(cbx)
        lyt.addWidget(clr)

        self.ui.scrollAreaLayout.insertLayout(index, lyt)
        return

    def get_tab_index(self, name, index=None):
        for tbx in self.ui.scrollAreaWidgetContents.children():
            if tbx.objectName() == name:
                index = self.ui.scrollAreaLayout.indexOf(tbx)
        return index

    def get_items(self, scene_process, name, items=[]):
        """
        get version items for combobox from /published and /scenes to get all versions
        :param scene_process:
        :param name: shot or asset subfolder name
        :return: returns items
        """
        versions = []
        path = "/".join([pm.workspace.path, "published", scene_process, name])
        if os.path.exists(path):
            for f in os.listdir(path):
                if f.lower().endswith(".ma"):
                    versions += [f.split(".")[1]]

        published = versions

        # in case there are no published files
        latest_publish = None
        if versions:
            latest_publish = versions[-1]

        path = "/".join([pm.workspace.path, "scenes", scene_process, name])
        if os.path.exists(path):
            file_name = name + "_processed."
            for f in os.listdir(path):
                if (f.lower().endswith(".ma")) and (f.count(".") == 3) and (file_name in f):
                    versions += [f.split(".")[1]]

        index, items = "0", sorted(list(set(versions)))
        if latest_publish is not None:
            index = str(versions.index(latest_publish))

        items = [index, items]
        return items

    def cycle_status(self, toolbox, cycle=[]):
        if cycle:
            # for referenced tab, all clrs are green
            toolbox.setStyleSheet("background-color:" + cycle)
            cbx_name = toolbox.objectName().replace("_clr", "_cbx")
            cbx = self.ui.scrollAreaWidgetContents.findChild(QtWidgets.QComboBox, cbx_name)

            #TODO: find out what the reference is cbx.setCurrentIndex()
            if cycle == "blue":
                pass
            elif cycle == "yellow":
                pass
            elif cycle == "green":
                pass
            return

        color = toolbox.palette().button().color()
        if color.blue() == 255:
            # cycle = [255, 255, 0]
            cycle = "yellow"
            print ">> yellow, latest scene"
        elif color.red() == 255:
            # cycle = [0, 255, 0]
            cycle = "green"
            print ">> green, current reference"
        else:
            # cycle = [0, 0, 255]
            cycle = "blue"
            print ">> blue, latest publish"
        toolbox.setStyleSheet("background-color:" + cycle)
        return

    def models(self):
        name = "Assets"
        num = self.dictionary[name]["id"]
        toolbox = self.ui.assets_tbx
        filter = [["project", "is", project], ["sg_asset_type", "is", "CG Model"]]
        field = ["code"]

        self.set_arrow(toolbox)
        scene_process = "_".join([num, name])
        index = self.get_tab_index(name.lower() + "_tbx") + 1
        assets = sg.find("Asset", filter, field)
        delete_tab = True  # delete tab if all layouts don't have items
        for a in assets[::-1]:  # first item in sg is first item in ui
            asset_name = a["code"]
            items = self.get_items(scene_process, asset_name)
            if items[1]:
                asset_name += "_{}".format(num)
                self.set_layout(asset_name, items, index)
                delete_tab = False

        if delete_tab:
            toolbox.deleteLater()
        return

    def rigs(self):
        name = "Rigs"
        num = self.dictionary[name]["id"]
        toolbox = self.ui.rigs_tbx
        filter = [["project", "is", project], ["sg_asset_type", "is", "CG Rig"]]
        field = ["code"]

        self.set_arrow(toolbox)
        scene_process = "_".join([num, name])
        index = self.get_tab_index(name.lower() + "_tbx") + 1
        assets = sg.find("Asset", filter, field)
        delete_tab = True  # delete tab if all layouts don't have items
        for a in assets[::-1]:  # first item in sg is first item in ui
            asset_name = a["code"]
            items = self.get_items(scene_process, asset_name)
            if items[1]:
                asset_name += "_{}".format(num)
                self.set_layout(asset_name, items, index)
                delete_tab = False

        if delete_tab:
            toolbox.deleteLater()
        return

    def camera(self):
        name = "Cameras"
        num = self.dictionary[name]["id"]
        toolbox = self.ui.cameras_tbx

        self.set_arrow(toolbox)
        scene_process = "_".join([num, name])
        index = self.get_tab_index(name.lower() + "_tbx") + 1
        asset_name = pm.workspace.fileRules["scene"].rsplit("/")[-1]
        items = self.get_items(scene_process, asset_name)
        if items[1]:
            asset_name += "_{}".format(num)
            self.set_layout(asset_name, items, index)
        else:
            toolbox.deleteLater()
        return

    def layout(self):
        name = "Layouts"
        num = self.dictionary[name]["id"]
        toolbox = self.ui.layouts_tbx

        self.set_arrow(toolbox)
        scene_process = "_".join([num, name])
        index = self.get_tab_index(name.lower() + "_tbx") + 1
        asset_name = pm.workspace.fileRules["scene"].rsplit("/")[-1]
        items = self.get_items(scene_process, asset_name)
        if items[1]:
            asset_name += "_{}".format(num)
            self.set_layout(asset_name, items, index)
        else:
            toolbox.deleteLater()
        return

    def dynamics(self):
        name = "Dynamics"
        num = self.dictionary[name]["id"]
        toolbox = self.ui.dynamics_tbx

        self.set_arrow(toolbox)
        scene_process = "_".join([num, name])
        index = self.get_tab_index(name.lower() + "_tbx") + 1
        asset_name = pm.workspace.fileRules["scene"].rsplit("/")[-1]
        items = self.get_items(scene_process, asset_name)
        if items[1]:
            asset_name += "_{}".format(num)
            self.set_layout(asset_name, items, index)
        else:
            toolbox.deleteLater()
        return

    def animation(self):
        name = "Animation"
        num = self.dictionary[name]["id"]
        toolbox = self.ui.animation_tbx

        self.set_arrow(toolbox)
        scene_process = "_".join([num, name])
        index = self.get_tab_index(name.lower() + "_tbx") + 1
        asset_name = pm.workspace.fileRules["scene"].rsplit("/")[-1]
        items = self.get_items(scene_process, asset_name)
        if items[1]:
            asset_name += "_{}".format(num)
            self.set_layout(asset_name, items, index)
        else:
            toolbox.deleteLater()
        return

    def build(self):
        print ">> scroll area widgets:"
        for tbx in self.ui.scrollAreaWidgetContents.children():
            print tbx.objectName()
        return

    def refresh(self):
        """
        checks for updates in /publish and scenes
        :return:
        """
        return

    def cancel(self):
        print ">> scroll area layout:"
        for tbx in self.ui.scrollAreaLayout.children():
            print tbx.objectName()
        return

    def init_ui(self):
        # connect toolbox to function
        for k, v in self.dictionary.items():
            if k == "Lighting":
                continue
            self.dictionary[k]["toolbox"].clicked.connect(self.dictionary[k]["command"])

        self.ui.build_btn.clicked.connect(self.build)
        self.ui.refresh_btn.clicked.connect(self.refresh)
        self.ui.cancel_btn.clicked.connect(self.cancel)

        # load ui once so tabs with no items in any layouts get deleted
        for k, v in self.dictionary.items():
            if k == "Lighting":
                continue
            self.dictionary[k]["command"]()

        # remove tabs, layouts, and widgets irrelevant to scene process
        removed = {}
        current_process = pm.workspace.fileRules["scene"].split("/")[1][3:]
        for k, v in self.dictionary.items()[::-1]:
            if "Lighting" == k:
                break
            elif "Dynamics" == current_process:
                break

            toolbox = self.dictionary[k]["toolbox"]
            id = self.dictionary[k]["id"]
            removed[id] = toolbox

            if "Animation" == current_process:
                break
            elif current_process == k.capitalize():
                break

        for k, v in removed.items():
            id = "_{}_".format(k)

            # tab
            v.deleteLater()

            # layouts
            for a in self.ui.scrollAreaLayout.children():
                if id in a.objectName():
                    a.deleteLater()

            # widgets
            for e in self.ui.scrollAreaWidgetContents.children():
                if id in e.objectName():
                    e.deleteLater()

        # connect widgets to function
        clr = None
        for w in self.ui.scrollAreaWidgetContents.children():
            if "_clr" in w.objectName():
                w.clicked.connect(lambda x=w: self.cycle_status(x))
                clr = w
        return

    def setup_ui(self):
        return

    def run(self):
        # self.ui.close()
        pass
