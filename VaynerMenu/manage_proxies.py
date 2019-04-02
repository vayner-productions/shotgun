from PySide2 import QtCore, QtWidgets, QtUiTools
from pymel.core import workspace, confirmDialog
from os import listdir, remove


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
        self.ui.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.proxy_files = self.get_proxy_names()
        self.connect_signals(self.proxy_files, self.ui)
        return

    def import_ui(self):
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    def get_proxy_names(self):
        proxy_files = []
        project_file = workspace(q=True, sn=True)
        project_shot = workspace.expandName(workspace.fileRules["scene"]).split("/")[-1]
        cache_dir = project_file + r'/scenes/06_Cache/08_Animation/'+ project_shot + "/"
        for p_file in listdir(cache_dir):
            if "_PXY.abc" in str(p_file):
                proxy_files.append(str(p_file))

        return proxy_files


    def connect_signals(self, proxy_files, ui):
        for p_file in proxy_files:
            self.ui.list_wdj.addItem(p_file)

        self.ui.remove_btn.clicked.connect(self.remove_btn)


    def remove_btn(self):
        project_file = workspace(q=True, sn=True)
        project_shot = workspace.expandName(workspace.fileRules["scene"]).split("/")[-1]
        cache_dir = project_file + r'/scenes/06_Cache/08_Animation/'+ project_shot + "/"

        selected_obj = []
        selected_obj = self.ui.list_wdj.selectedItems()

        for p_file in selected_obj:
            remove(cache_dir + p_file.text())

        mw.ui.close()
