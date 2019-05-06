"""
"""
from . import *
from .. import checkout_scene, render_setup
from pymel.core import PyNode
from pymel.core.system import workspace
from pymel.util import path
from PySide2 import QtCore, QtWidgets, QtUiTools
from sgtk.authentication import ShotgunAuthenticator


reload(checkout_scene)
checkout = checkout_scene.Checkout()

reload(render_setup)
render_settings = render_setup.RenderSettings()


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
        self.render_path = self.get_render_path()
        self.version = render_settings.drg.renderVersion.get()
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

    @staticmethod
    def get_render_path():
        drg = PyNode("defaultRenderGlobals")
        img_prefix = drg.imageFilePrefix.get()

        render_path = path(workspace.path.joinpath(
            workspace.fileRules["images"],
            img_prefix
        ).split("<Version>")[0]).normpath()
        return render_path

    def set_render_path(self):
        option = self.ui.version_grp.checkedButton().text()
        if option == "Next":
            self.version = self.ui.next_lne.placeholderText()
        elif option == "Custom":
            self.version = self.ui.custom_lne.text()
        elif option == "Previous":
            self.version = self.ui.previous_cbx.currentText()
        render_path = self.render_path.joinpath(self.version).normpath()
        self.ui.render_lbl.setText(render_path)
        return

    def checked_custom(self):
        self.ui.custom_rbn.setChecked(1)
        self.set_render_path()
        return

    def checked_previous(self):
        self.ui.previous_rbn.setChecked(1)
        self.set_render_path()
        return

    def init_ui(self):
        for task in self.tasks:
            item = QtWidgets.QListWidgetItem(task["content"], self.ui.task_lsw)
            item.setToolTip(str(task["id"]))

        # get all the version folders that exist
        previous = sorted([version.namebase for version in self.get_render_path().dirs()])[::-1]

        # previous only contains folders with content
        # by default, version reflects the next folder which has not been created yet
        # sometimes the next folder is created and contains nothing
        # previous will not display the next folder in the ui-dropdown to avoid confusion
        try:
            previous.remove(self.version)
        except:
            pass

        # display previous ui elements if version folders exist
        if previous:
            self.ui.previous_cbx.addItems(previous)
        else:
            self.ui.previous_rbn.deleteLater()
            self.ui.previous_cbx.deleteLater()

        # load ui elements
        self.ui.next_lne.setPlaceholderText(self.version)
        self.ui.render_lbl.setText(self.render_path.joinpath(self.version).normpath())

        # connect signals to slots
        self.ui.version_grp.buttonClicked.connect(self.set_render_path)
        self.ui.custom_lne.textChanged.connect(self.checked_custom)
        self.ui.previous_cbx.currentIndexChanged.connect(self.checked_previous)
        self.ui.publish_btn.clicked.connect(self.clicked_publish)
        return

    def clicked_publish(self):

        # render_settings.drg.renderVersion.set(self.version)
        return
