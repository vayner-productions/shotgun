"""
# SET PROJECT W/CODE - USER INPUT
from shotgun import set_project as sg
reload(sg)
set = sg.SetProject(process="anim", entity="1")
set.process_data()
set.run()


# SET PROJECT W/CODE - USER PREFERENCES
from shotgun import set_project as sg
reload(sg)
set = sg.SetProject()
set.process, set.entity = set.json_preferences
set.process_data()
set.run()


# SET PROJECT FROM UI
from shotgun import set_project as sg
reload(sg)
sg.get_window()
"""

from . import *
from PySide2 import QtCore, QtWidgets, QtUiTools
from pymel.util import path
from pymel.core.system import Workspace, warning
from sgtk.authentication import ShotgunAuthenticator
import json
# import maya.mel as mel

workspace = Workspace()
auth = ShotgunAuthenticator()


def get_window():
    global mw
    try:
        mw.ui.close()
    except:
        pass

    mw = MyWindow()
    mw.ui.show()


class SetProject(object):
    def __init__(self, **kwargs):
        allowed_keys = {
            "process",  # scene process - 08_Animation
            "entity_type",  # for sg.find() - Asset/Shot
            "entity",  # to find name is Assets/Shots page - 001_Hero/Shot_001
            "project_path"  # for setting project window - ../04_Maya
        }
        self.__dict__.update((k, None) for k in allowed_keys)
        self.__dict__.update((k, v) for k, v in kwargs.items())

        self.template = {
            "00_Tests",
            "01_Assets",
            "02_Rigs",
            "03_Cameras",
            "04_Layouts",
            "05_Dynamics",
            "06_Cache",
            "07_Lighting",
            "08_Animation"
        }

        # --- project_path ---
        # used for remote-work, change the root variable
        if root:
            self.project_path = path(root).normpath()
            return

        # used for in-office development
        data = sg.find_one(
            "Project",
            [
                ["id", "is", project["id"]]
            ],
            [
                "sg_client",
                "sg_brand",
                "name"
            ]
        )
        client_brand = data["sg_client"]["name"]
        sub_brand = data["sg_brand"]["name"]
        project_name = data["name"]
        project_path = r"{}/Animation/Projects/Client/{}/{}/{}/Project Directory/02_Production/04_Maya".format(
            media_space, client_brand, sub_brand, project_name)

        self.project_path = path(project_path).normpath()
        return

    def process_data(self):
        # --- process / entity_type ---
        for dir in self.template:
            if self.process.lower() in dir.lower():
                self.process = dir
                break

        if self.process is "01_Assets" or self.process is "02_Rigs":
            self.entity_type = "Asset"
        elif self.process is "00_Tests":
            return
        else:
            self.entity_type = "Shot"

        # --- entity ---
        self.entity = sg.find_one(
            self.entity_type,  # Asset / Shot
            [["project", "is", project], ["code", "ends_with", self.entity.lower()]],
            ["code"]
        )
        return

    def json_preferences(self, process="00_Tests", entity_name="incrementalSave", data=None, update=False):
        """
        pymel.core.language.OptionVarDict records the workstation user's preferences

        This method records set project preferences of the user logged into sg desktop.
        :param process:
        :param entity_name:
        :param data: json object data
        :param update: edits json file if changes were made, ignores param defaults
        :return process, entity_name:
        """
        user = str(auth.get_user())

        script_dir = self.project_path.joinpath("scripts")
        set_project_file = script_dir.joinpath("set_project.json").normpath()

        # create json file and use param defaults
        if not set_project_file.exists():
            data = {
                user: {
                    "process": process,
                    "entity": entity_name
                }
            }
            with set_project_file.open(mode="a") as new_file:
                json.dump(data, new_file, indent=4, separators=(',', ': '))
            return process, entity_name

        # determine new or existing user on project
        try:
            with set_project_file.open(mode="r") as read_file:
                data = json.load(read_file)
                data[user]  # checks for new user, KeyError is caught below
        except KeyError:
            data = {
                user: {
                    "process": process,
                    "entity": entity_name
                }
            }
            with set_project_file.open(mode="a") as append_file:
                json.dump(data, append_file, indent=4, separators=(',', ': '))
            return process, entity_name

        # json_preferences() without arguments is similar to querying for user preferences, no changes to json file
        param_default = process is "00_Tests" or entity_name is "incrementalSave"
        if param_default:
            user_process = data[user]["process"]
            user_entity = data[user]["entity"]
            return user_process, user_entity

        # user preferences changed, update json file for existing users
        process_changed = process is not data[user]["process"]
        entity_name_changed = entity_name is not data[user]["entity"]
        if process_changed or entity_name_changed:
            data[user]["process"] = process
            data[user]["entity"] = entity_name

            with set_project_file.open(mode="w") as edit_file:
                json.dump(data, edit_file, indent=4, separators=(',', ': '))
        return process, entity_name

    def run(self):
        """
        updates the project window - current project is 04_Maya and location is project path

        template changes are also made to scene, shaders, and Alembic file rules -
        scenes/scene process folder/entity
            - scenes/08_Animation/Shot_001
            - scenes/01_Assets/001_hero
        data/001_Shaders
        scenes/06_Cache/08_Animation/Shot_###

        directories are made in create_project_directory.py OR it comes from Vayner project template
        :return:
        """
        # create_project_directory.py
        workspace.open(self.project_path)
        # mel.eval('setProject \"' + self.project_path + '\"')

        workspace.fileRules["scene"] = "/".join(["scenes", self.process, self.entity["code"]])

        if self.entity_type is "Shot":
            workspace.fileRules["Alembic"] = "/".join(["scenes", "06_Cache", "08_Animation", self.entity["code"]])

        # Vayner project template
        workspace.fileRules["shaders"] = "/".join(["data", "001_Shaders"])

        # Save preferences to script/set_project.json
        self.json_preferences(process=self.process, entity_name=self.entity["code"])
        return


class MyWindow(SetProject, QtWidgets.QDialog):
    def __init__(self, **kwargs):
        super(MyWindow, self).__init__(**kwargs)
        self.ui = self.import_ui()
        self.init_ui()

    def import_ui(self):
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    def change_asset_items(self):
        # asset ui items are changing because user has changed process field
        # ensure those items are entities with a corresponding folder
        process = self.ui.scene_cbx.currentText()
        entity_type = None

        if process == "01_Assets" or process == "02_Rigs":  # changing is to ==, currentText() returns unicode type
            entity_type = "Asset"
        elif process == "00_Tests":
            pass
        else:
            entity_type = "Shot"

        process_path = path(self.project_path).joinpath("scenes", process).normpath()
        entities = sg.find(
            entity_type,  # Asset / Shot
            [["project", "is", project]],
            ["code"]
        )

        subfolders = {str(sub.basename()) for sub in process_path.dirs()}
        entity_names = {entity["code"] for entity in entities}
        asset_items = sorted(entity_names.intersection(subfolders))

        # reload asset field with new elements
        self.ui.asset_cbx.clear()
        self.ui.asset_cbx.addItems(asset_items)
        return

    def set_project(self):
        self.process, self.entity = self.ui.scene_cbx.currentText(), self.ui.asset_cbx.currentText()
        self.process_data()
        self.run()
        self.ui.close()
        print ">> project set",
        return

    def init_ui(self):
        # json_preferences() and process_data() are methods in SetProject
        # they are used together to enable access to their class's attributes
        # it helps the UI display user preferences and elements of entities with a folder
        self.process, self.entity = self.json_preferences()
        self.process_data()

        # all asset or shot entities should have a corresponding folder, see create_project_directory.py
        # create UI elements representing these entities only if their folder exists
        process_path = path(self.project_path).joinpath("scenes", self.process).normpath()
        entities = sg.find(
            self.entity_type,  # Asset / Shot
            [["project", "is", project]],
            ["code"]
        )

        subfolders = {str(sub.basename()) for sub in process_path.dirs()}
        entity_names = {entity["code"] for entity in entities}
        asset_items = sorted(entity_names.intersection(subfolders))

        exclude = {
            "04_Layouts",
            "06_Cache"
        }
        scene_items = sorted(self.template.difference(exclude))

        self.ui.scene_cbx.addItems(scene_items)
        self.ui.asset_cbx.addItems(asset_items)

        # update the UI to reflect user preferences
        self.ui.scene_cbx.setCurrentText(self.process)
        self.ui.asset_cbx.setCurrentText(self.entity["code"])

        # make UI dynamic - entity items change whenever process is changed
        self.ui.scene_cbx.currentTextChanged.connect(self.change_asset_items)

        self.ui.set_project_btn.clicked.connect(self.set_project)
        return
