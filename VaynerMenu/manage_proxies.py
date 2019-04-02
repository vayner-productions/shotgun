"""
# USED FROM UI
from shotgun.VaynerMenu import manage_proxies as sg
reload(sg)
sg.get_window()

# USED FROM CODE
from shotgun.VaynerMenu import manage_proxies as sg
reload(sg)
mp = sg.MyWindow()
mp.remove = ["Shot_006_PXY"]  # expects the exact name of the proxy, assumes it's an alembic
mp.remove_proxies()
"""

from PySide2 import QtCore, QtWidgets, QtUiTools
from pymel.core.system import Workspace, warning
workspace = Workspace()
from pymel.util import path


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
        self.alembic_directory = path(workspace.expandName(workspace.fileRules["Alembic"])).normpath()
        if "data" in self.alembic_directory:
            warning(">> Set project to Animation")
            self.ui.close()
            return
        self.proxies = [pxy.namebase for pxy in self.alembic_directory.files("*_PXY.abc")]
        self.remove = []

        self.ui = self.import_ui()
        self.ui.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.ui.list_wdj.addItems(self.proxies)
        self.ui.remove_btn.clicked.connect(self.remove_proxies)
        return

    def import_ui(self):
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    def remove_proxies(self):
        """
        expects the exact name of the proxy, assumes it's an alembic
        can remove proxies from selection
        can remove proxies as strings using self.remove = ["Shot_006_PXY"]
        :return:
        """
        proxies = self.remove

        if not proxies:
            proxies = [str(proxy) for proxy in self.ui.list_wdj.selectedItems()]

        for proxy in proxies:
            proxy_file = self.alembic_directory.joinpath(proxy + ".abc")
            proxy_file.remove_p()

        self.ui.close()
        return
