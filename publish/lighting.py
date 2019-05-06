"""
"""
from . import *
from .. import checkout_scene
import pymel.core as pm
from pymel.core.system import workspace
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

    def update_shotgun(self):
        return


class MyWindow(Publish, QtWidgets.QDialog):
    def __init__(self, **kwargs):
        super(MyWindow, self).__init__(**kwargs)
        self.ui = self.import_ui()

        scene_process, shot_name = workspace.fileRules["scene"].split("/")[1:]  # Shot_###
        self.scene_process = scene_process.split("_", 1)[-1]  # Lighting
        self.shot_entity = sg.find_one(
            "Shot",
            [
                ["project", "is", project],
                ["code", "is", shot_name]
            ]
        )

        self.init_ui()
        return

    def import_ui(self):
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    def get_tasks(self):
        task_filters = [
            ["project", "is", project],  # tasks for this project
            ["entity", "is", self.shot_entity],  # this shot
            ["step.Step.code", "is", self.scene_process]  # only lighting tasks
        ]

        task_fields = [
            "content"#, "step"
        ]

        print ">>>", sg.find(
            "Task",
            filters=task_filters,
            fields=task_fields
        )
        return

    def init_ui(self):
        return

