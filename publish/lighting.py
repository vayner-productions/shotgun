"""
"""
from . import *
from .. import checkout_scene
import pymel.core as pm
from PySide2 import QtCore, QtWidgets, QtUiTools


reload(checkout_scene)
checkout = checkout_scene.Checkout()


def get_window():
    global mw
    try:
        mw.ui.close()
    except:
        pass

    mw = MyWindow()
    mw.ui.show()


class Publish(object):
    """
    - check for tasks, their names
    - update tasks to "cmpt" for complete
    - save original file
    - increment processed
    - create version
    - update sg_maya_light with original file
    - update sg_maya_render with latest output path
    - no need to create thumbnail
    - no need to create playblast
    - include automated comment
    render setup and publish are separated in case output render versions get overwritten..
    unless there's a way to see the versioning process first in the UI
    """
    def __init__(self):
        return


class MyWindow(Publish, QtWidgets.QDialog):
    def __init__(self, **kwargs):
        super(MyWindow, self).__init__(**kwargs)
        self.ui = self.import_ui()
        # self.init_ui()

    def import_ui(self):
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

