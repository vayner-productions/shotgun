"""
checks for latest published version

from shotgun import build_scene as sg
reload(sg)
sg.get_window()
"""
from PySide2 import QtCore, QtWidgets, QtUiTools, QtGui
import pymel.core as pm
import sgtk
import os
from collections import OrderedDict

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


class FileEdit(QtWidgets.QLineEdit):
    """overriding PEP8, camel-case functions are special events functions"""
    def __init__(self):
        super(FileEdit, self).__init__()

        self.setDragEnabled(True)
        font = QtGui.QFont("MS Shell Dlg 2")
        font.setPointSize(12)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Preferred)
        self.setFont(font)
        self.setSizePolicy(size_policy)
        self.setObjectName("custom_lne")

    def dragEnterEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            # for some reason, this doubles up the intro slash
            filepath = str(urls[0].path())[1:]
            self.setText(filepath)
            

class MyWindow(QtWidgets.QDialog):
    def __init__(self):
        self.ui = self.import_ui()
        #TODO: QUERY DESIGNATED LIST FROM SHOTGUN SITE
        self.designated_list = [
            "001_rig_A",
            "002_Model_C",
            "002_Model_C",
            "04_Layouts",
            "08_Animation"
            ]
        self.designated_rows = OrderedDict()
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

    def dragdown_menu(self):
        """the combo box in the assets section contain options "Rigs" and "Models", these options
        enable the list view to show folders representing entities on shotgun"""
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

    def indicate_multiples(self, text):
        """adds an identifier {1} beside the fields in reference elements to indicate multiples"""
        rx = QtCore.QRegExp("status_*lbl")
        rx.setPatternSyntax(QtCore.QRegExp.Wildcard)
        elements = [child.text().split(" {", 1)[0]  # get the asset name without indications
                    for child in self.ui.findChildren(QtWidgets.QLabel, rx)]
        if elements.count(text) != 0:
            text = "{} {{{}}}".format(text, elements.count(text) + 1)
        return text

    def scrolldown(self):
        value = self.ui.scrollArea.verticalScrollBar().maximum()
        self.ui.scrollArea.verticalScrollBar().setValue(value)
        return

    def add_template_row(self, text):
        """creates a row template for reference elements"""
        font = QtGui.QFont("MS Shell Dlg 2")
        font.setPointSize(12)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Preferred)
        num = self.ui.scrollAreaLayout.rowCount()

        label = QtWidgets.QLabel("")
        label.setMinimumSize(20, 20)
        label.setStyleSheet("background-color: None")
        label.setObjectName("status_{}_wgt".format(num))

        text = self.indicate_multiples(text)
        field = QtWidgets.QLabel(text)
        field.setFont(font)
        field.setSizePolicy(size_policy)
        field.setObjectName("status_{}_lbl".format(num))

        self.ui.scrollAreaLayout.insertRow(num, label, field)
        self.ui.scrollArea.verticalScrollBar().rangeChanged.connect(self.scrolldown)
        return label, field

    def add_shot(self, scene_process):
        """adds a row from the shots section to reference elements"""
        selection = {
            "Camera": "03_Cameras",
            "Layout": "04_Layouts",
            "Dynamics": "05_Dynamics",
            "Animation": "08_Animation"
        }
        if selection[scene_process] in self.designated_list:
            rx = QtCore.QRegExp("status_*_d*")
            rx.setPatternSyntax(QtCore.QRegExp.Wildcard)
            designated_widgets = [child for child in self.ui.findChildren(QtWidgets.QLabel, rx)]
            widgets = designated_widgets[0:][::2]
            labels = designated_widgets[1:][::2]
            for w, l in zip(widgets, labels):
                if not selection[scene_process] in l.text():
                    continue

                color = w.palette().color(QtGui.QPalette.Background).getRgb()
                update_element = None
                if color != QtGui.QColor(0, 0, 255, 255):  # not blue
                    w.setStyleSheet("background-color: blue")
                    break
            return
        self.add_template_row(selection[scene_process])
        return

    def add_assets(self, selection=None):
        """adds an entity from the assets section to reference elements"""
        if not selection:
            selection = [sel.text() for sel in self.ui.assets_lst.selectedItems()]

        if selection:
            for sel in selection:
                self.add_template_row(sel)
        return

    def designated(self):
        for d in self.designated_list:
            label, field = self.add_template_row(d)
            object_name = label.objectName().replace("wgt", "dwgt")
            label.setObjectName(object_name)
            object_name = field.objectName().replace("lbl", "dlbl")
            field.setObjectName(object_name)

            label.setStyleSheet("border: 1px solid red")

            self.designated_rows[label] = field
        return

    def add_context_menu(self):
        """enable a context menu in the assets section"""
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
        """a context menu in reference elements, removes the row from ui and asset from scene"""
        # remove asset from scene
        assets = []

        # remove asset row in ui from cursor selection
        #TODO: POSITION NOT CAPTURED CORRECTLY, DOESN'T SELECT THE RIGHT WIDGET
        position = QtGui.QCursor.pos()
        widget = QtWidgets.QApplication.widgetAt(position)
        print ">> remove:", widget.objectName(), widget.text()
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
            #TODO: DELETE ENTITY FROM UI
            #TODO: DELETE CUSTOM FROM UI
            # assets += []

        # remove asset from scene
        for asset in assets:
            break
        return

    def select_elements(self):
        """context menu in reference elements, selects all the nodes from reference based on ui
        selection"""
        # TODO: GET THE REFERENCE PATH OF THE UI SELECTION
        f = r"A:/Animation/Projects/Client/VaynerX/Vayner Productions/0002_Test_Project/Project Directory/02_Production/04_Maya/published/03_Cameras/Shot_001/Shot_001_original.0001.ma"
        ref_node = pm.FileReference(pathOrRefNode=f).refNode
        assemblies = set([a.__unicode__() for a in pm.ls(assemblies=1)])
        all_nodes = set(pm.referenceQuery(ref_node, nodes=1))
        nodes = list(assemblies.intersection(all_nodes))
        pm.select(nodes)
        return

    def ref_context_menu(self):
        """creates context menu in reference elements"""
        # creates menu
        menu = QtWidgets.QMenu()

        # select
        select = QtWidgets.QAction("Select", menu)
        menu.addAction(select)
        select.triggered.connect(self.select_elements)

        # remove
        remove = QtWidgets.QAction("Remove", menu)
        menu.addAction(remove)
        remove.triggered.connect(self.remove_elements)

        # locates where menu is shown
        menu.exec_(QtGui.QCursor.pos())
        return

    def add_referenced(self):
        """display all the referenced elements in the scene and their status
        the status refers to the file's directory name, which could be outside /published
        for example, status looks at /scenes/06_Cache when referencing alembics
        another example, status looks at /published/rigs when referencing rigs
        another example, status looks at /custom when files referenced through custom button"""
        designated_list = self.designated_list
        designated_rows = self.designated_rows

        for ref in pm.listReferences():
            item, status = ref.path.dirname().rsplit("/", 2), "blue"

            # get item using reference node
            # use name for rigs and assets
            # use scene process for everything else
            if ("01_Assets" in ref.path) or ("02_Rigs" in ref.path):
                item = item[2]
            else:
                item = item[1]

            # get status: yellow/update; blue/latest
            # filters through name.#.ext and name_#.ext
            latest = 0
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
                latest = int(max(files, key=os.path.getctime).splitext()[0][-4:])

            if current < latest:
                status = "yellow"

            # create ui
            new_row = 1
            for d, label, field in zip(designated_list, designated_rows.keys(), designated_rows.values()):
                # print ">>", item, d, field.text()
                if item in d:
                    # print ">> updating designated list", item, status, field.text()
                    label.setStyleSheet("background-color:{}; border: 1px solid red".format(status))
                    designated_list.remove(d)
                    del designated_rows[label]
                    new_row = 0
                    break
            if new_row:
                # print ">> creating new row", item, status
                label, field = self.add_template_row(item)
                label.setStyleSheet("background-color:{}".format(status))
        return

    def add_custom(self, file_name=None):
        """add custom element into ui and custom folder, the file is overwritten if it exists"""
        # /custom
        if not file_name:
            file_name = self.ui.custom_lne.text()

        file_name = pm.util.common.path(file_name)
        if not file_name.isfile():
            return

        custom = pm.workspace.path + "/custom/" + file_name.basename()
        pm.util.common.path.copy2(file_name, custom)

        # ui
        font = QtGui.QFont("MS Shell Dlg 2")
        font.setPointSize(12)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Preferred)
        num = self.ui.scrollAreaLayout.rowCount()

        label = QtWidgets.QLabel("")
        label.setMinimumSize(20, 20)
        label.setStyleSheet("background-color: None")
        label.setObjectName("status_{}_wgt".format(num))

        text = self.indicate_multiples(custom.basename().stripext())
        field = QtWidgets.QLabel(text)
        field.setFont(font)
        field.setSizePolicy(size_policy)
        field.setObjectName("status_{}_lbl".format(num))

        self.ui.scrollAreaLayout.insertRow(num, label, field)
        self.ui.scrollArea.verticalScrollBar().rangeChanged.connect(self.scrolldown)
        return

    def custom(self):
        """add custom reference"""
        dialog = QtWidgets.QFileDialog()
        file_name = dialog.getOpenFileName(
            parent=self.ui.custom_btn,
            caption="Custom Reference",
            dir=pm.workspace.path,
            filter="""
            Maya Files (*.ma *.mb);;
            Maya ASCII (*.ma);;
            Maya Binary (*.mb);;
            Alembic Files (*.abc);;
            All Files (*.*)""",
            selectedFilter="Maya ASCII (*.ma)",
            options=QtWidgets.QFileDialog.DontUseNativeDialog
        )[0]
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        self.add_custom(file_name)
        return

    def build(self):
        """updates the entire scene given the list in reference elements"""
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

        # update all the files in the scene, create reference to those just added
        # change status of elements to blue (for latest publish)
        for f, wgt in zip(latest, elements.keys()):
            color = wgt.palette().color(QtGui.QPalette.Background)
            if color == QtGui.QColor(255, 255, 0, 255):
                for ref in pm.listReferences():
                    if not (f.basename() in ref.path) and (f.dirname() in ref.path):
                        pm.FileReference(refnode=ref.refNode).replaceWith(f)
            else:
                pm.createReference(f, namespace=":")
            wgt.setStyleSheet("background-color: blue")
        return

    def init_ui(self):
        self.designated()
        self.add_referenced()
        self.dragdown_menu()

        self.ui.assets_lne.textChanged.connect(self.dragdown_menu)
        self.ui.assets_cbx.currentIndexChanged.connect(self.dragdown_menu)

        self.ui.assets_lst.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.assets_lst.customContextMenuRequested.connect(self.add_context_menu)

        self.ui.scrollAreaWidgetContents.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.scrollAreaWidgetContents.customContextMenuRequested.connect(self.ref_context_menu)

        current_scene_process = pm.workspace.fileRules["scene"].split("/")[1]
        if (current_scene_process == "01_Assets") or (current_scene_process == "02_Rigs"):
            self.ui.shots_gbx.setVisible(0)
        else:
            self.ui.camera_btn.clicked.connect(lambda x="Camera": self.add_shot(x))
            self.ui.layout_btn.clicked.connect(lambda x="Layout": self.add_shot(x))
            self.ui.dynamics_btn.clicked.connect(lambda x="Dynamics": self.add_shot(x))
            self.ui.animation_btn.clicked.connect(lambda x="Animation": self.add_shot(x))

        self.ui.custom_btn.clicked.connect(self.custom)
        file_edit = FileEdit()
        self.ui.custom_lyt.addWidget(file_edit)

        self.ui.build_btn.clicked.connect(self.build)
        return

    def setup_ui(self):
        return

    def run(self):
        return
