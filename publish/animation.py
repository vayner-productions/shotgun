"""
from shotgun.Publish import animation as sg

reload(sg)
sg.get_window()


creates alembics for each referenced node
referenced nodes include:
- camera (skip alembic)
- char (anim)
- set (no anim)
- props (anim)
publishes camera..option?
option to skip playblast
versioning changes in SG site..
"""
from . import *
from PySide2 import QtCore, QtWidgets, QtUiTools
from pymel.core.system import Workspace
from pymel.util import path


def get_window():
    global mw
    try:
        mw.ui.close()
    except:
        pass

    mw = MyWindow()
    mw.ui.show()


"""
using sg_anim field to log maya alembic entity

# HELPFUL CODE
import pymel.core as pm
for ref in pm.listReferences():
    print ">>", ref.refNode
"""


class Publish:
    def __init__(self, thumbnail=None, playblast=None, maya_file=None, alembic_directory=None, comment=""):
        self.thumbnail = thumbnail
        self.playblast = playblast
        self.maya_file = maya_file
        self.alembic_directory = alembic_directory
        self.comment = comment
        self.alembic_file = None
        return

    def rich_media(self):
        return self.thumbnail, self.playblast

    def single_frame(self):
        return self.alembic_file

    def multi_frame(self):
        return self.alembic_file

    def update_shotgun(self):
        # GET ENTITY
        entity_name = path(Workspace.fileRules["scene"]).basename() + "_Anim"

        alembic_entity = sg.find_one(
            "CustomEntity05",
            [
                ["project", "is", project],
                ["code", "is", entity_name]
            ]
        )

        version_entity = sg.find_one(
            "Version",
            [
                ["project", "is", project],
                ["entity", "is", alembic_entity]
            ],
            fields=[
                "id",
                "type",
                "code"
            ],
            additional_filter_presets=[
                {
                    "preset_name": "LATEST",
                    "latest_by": "ENTITIES_CREATED_AT"
                }
            ]
        )

        # CREATE NEXT VERSION
        version_name = entity_name + "_v001"
        if version_entity:
            latest_version = version_entity["code"][-3:]
            version_name = version_name[:-3] + str(int(latest_version) + 1).zfill(3)

        # TODO: FILE LINKS {link: self.playblast}
        data = {
            "project": project,
            "code": version_name,
            "entity": alembic_entity,
            "image": self.thumbnail,
            "sg_uploaded_movie": self.playblast,
            "sg_maya_file": self.maya_file,
            "sg_alembic_directory": self.alembic_directory,
            "description": self.comment
        }
        version = sg.create("Version", data)
        return

    def animation(self):
        self.update_shotgun()
        return


class MyWindow(QtWidgets.QDialog):
    def __init__(self):
        self.ui = self.import_ui()
        self.init()
        return

    def import_ui(self):
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    def init(self):
        # TODO: GET UI WORKING
        return

    def run(self):
        publish = Publish()
        publish.animation()
        return
