"""
"""
from . import *
from .. import checkout_scene
import pymel.core as pm
from pymel.core.system import workspace
from PySide2 import QtCore, QtWidgets, QtUiTools
from sgtk.authentication import ShotgunAuthenticator


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
        self.tasks = self.get_tasks()
        self.init_ui()
        return

    @staticmethod
    def import_ui():
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    @staticmethod
    def get_tasks():
        scene_process, shot_name = workspace.fileRules["scene"].split("/")[1:]  # Shot_###
        scene_process = scene_process.split("_", 1)[-1]  # Lighting
        shot_entity = sg.find_one(
            "Shot",
            [
                ["project", "is", project],
                ["code", "is", shot_name]
            ]
        )

        auth = ShotgunAuthenticator()
        user = str(auth.get_user())

        tasks = sg.find(
            "Task",
            filters=[
                ["project", "is", project],  # tasks for this project
                ["entity", "is", shot_entity],  # this shot
                ["task_assignees.HumanUser.firstname", "is", user],  # this user
                ["step.Step.code", "is", scene_process],  # only lighting tasks
                ["sg_status_list", "is_not", "cmp"],
                ["sg_status_list", "is_not", "rev"],
                ["sg_status_list", "is_not", "omt"],
            ],
            fields=["content"]
        )
        return tasks

    def get_render_path(self):
        render_path = workspace.path.joinpath(
            workspace.fileRules["images"],
            "render_cam"
        )
        print ">>", render_path
        return

    def init_ui(self):
        return

