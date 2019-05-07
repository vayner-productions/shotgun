"""

# PUBLISH BY CODE
lighting = Publish()
lighting.comment = "Published from code"  # add personal comment first

# get tasks you've addressed
# update tasks, add automated message to comments
task_complete = lighting.tasks[0]
lighting.set_task(task_name=task_complete["content"], task_id=task_complete["id"])

lighting.lighting()  # work that's done in Maya
lighting.update_shotgun()  # get shotgun to record all relevant info (files, comments, and tasks)
"""
from . import *
from .. import checkout_scene, render_setup
from pymel.core import PyNode, sceneName, saveFile, openFile
from pymel.core.system import workspace
from pymel.util import path
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
    def __init__(self):
        self.tasks = self.get_tasks()
        self.lighting_file = self.get_publish_file()  # maya lighting scene file to be recorded on shotgun
        self.lighting_output = self.get_render_path()  # maya render output path to be recorded on shotgun
        self.comment = ""
        self.return_file = sceneName()  # file to return to in case of publish error
        self.working_file = None
        return

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
    def set_task(task_name=None, task_id=None):
        sg.find_one(
            "Task",
            filters=[["project", "is", project], ["content", "is", task_name], ["id", "is", task_id]]
        )

        sg.update("Task", task_id, {"sg_status_list": "cmp"})
        return

    @staticmethod
    def get_render_path():
        """
        A path object stopping at the version folder, example:
        M:\Animation\Projects\Client\VaynerX\Vayner Productions\0009_Test_Project\Project Directory\02_Production
        \04_Maya\images\Shots\Shot_001\v001

        :return:
        """
        drg = PyNode("defaultRenderGlobals")
        img_prefix = drg.imageFilePrefix.get()

        render_path = path(workspace.path.joinpath(
            workspace.fileRules["images"],
            img_prefix
        ).split("<Version>")[0]).joinpath(drg.renderVersion.get()).normpath()
        return render_path

    @staticmethod
    def get_publish_file():
        publish_folder = path(workspace.path.joinpath(workspace.fileRules["scene"]).replace("scenes", "published"))
        publish_folder.makedirs_p()

        publish_file, shot = None, publish_folder.namebase
        publish_files = sorted(publish_folder.files("{}_original.*.ma".format(shot)))[::-1]
        if publish_files:
            # incrementing based on the length of published files may overwrite any existing file because it is not
            # accounting for the version number on the latest file, this way ensures the next original file does
            latest_file = publish_files[0].split(".")
            latest_file[1] = str(int(latest_file[1]) + 1).zfill(4)
            publish_file = path(".".join(latest_file))
        else:
            publish_file = publish_folder.__div__("{}_original.0001.ma".format(shot))

        publish_file = path(publish_file).normpath()
        return publish_file

    def lighting(self, version_label=None):
        """
        creates working file, saved as the latest processed file, and copies it as the latest original file
        :return:
        """
        reload(render_setup)
        render_settings = render_setup.RenderSettings()
        if version_label:
            render_settings.drg.renderVersion.set(version_label)

        # ensures this is the point to return to if there's an error
        self.working_file = path(checkout.increment_file())

        # copies saved working file as original file
        self.working_file.copy2(self.lighting_file)
        return

    def update_shotgun(self):
        lighting_name = workspace.fileRules["scene"].split("/")[-1] + "_Lgt"

        lighting_entity = sg.find_one(
            "CustomEntity03",
            filters=[["project", "is", project], ["code", "is", lighting_name]],
        )

        latest_version = sg.find_one(
            "Version",
            filters=[["project", "is", project], ["entity", "is", lighting_entity]],
            fields=["code"],
            additional_filter_presets=[
                {
                    "preset_name": "LATEST",
                    "latest_by": "ENTITIES_CREATED_AT"
                }
            ]
        )

        version_name = lighting_name + "_v001"
        if latest_version:
            version_name = lighting_name + "_v" + str(int(latest_version["code"][-3:]) + 1).zfill(3)

        sg.create(
            "Version",
            {
                "project": project,
                "entity": lighting_entity,
                "code": version_name,
                "description": self.comment,
                "sg_lighting_file": {
                    "link_type": "local",
                    "local_path": str(self.lighting_file.normpath()),
                    "name": self.lighting_file.namebase
                },
                "sg_lighting_output": {
                    "link_type": "local",
                    "local_path": str(self.lighting_output.normpath()),
                    "name": self.lighting_output.namebase
                }
            }
        )

        print ">> Render setup complete.\n",
        return


class MyWindow(Publish, QtWidgets.QDialog):
    def __init__(self, **kwargs):
        super(MyWindow, self).__init__(**kwargs)
        self.ui = self.import_ui()
        self.render_path = self.get_render_path().dirname()

        reload(render_setup)
        common = render_setup.Common()
        common.file_output()
        common.metadata()
        self.version = common.drg.renderVersion.get()

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
        previous = sorted([version.namebase for version in self.render_path.dirs()])[::-1]

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
        self.ui.publish_btn.clicked.connect(self.publish_lighting)
        return

    def publish_lighting(self):
        # get ui data
        user_comment = self.ui.comment_txt.toPlainText()
        completed_tasks = self.ui.task_lsw.selectedItems()

        # process comment to update to shotgun first
        # comments are inconsequential to publish errors
        if user_comment:
            self.comment = user_comment + "\n\n"

        for task in completed_tasks:
            task_name = task.text()
            if "Addressed Tasks" not in self.comment:
                self.comment += "Addressed Task(s):"
            self.comment += "\n{}".format(task_name)

        # do work in Maya
        # publish fail will open the return file, the file before any publishing work began,
        # and remove both working and publish file
        self.lighting(version_label=self.version)
        try:
            for task in completed_tasks:
                task_name, task_id = task.text(), int(task.toolTip())
                self.set_task(task_name=task_name, task_id=task_id)

            self.lighting_output = path(self.ui.render_lbl.text())
            self.update_shotgun()
        except:
            openFile(self.return_file, f=1)
            self.working_file.remove_p()
            self.lighting_file.remove_p()

        self.ui.close()
        return
