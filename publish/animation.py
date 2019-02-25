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
    def __init__(self):
        return

    def single_frame(self):
        return

    def multi_frame(self):
        return

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

        # data = {
        #     "project": project,
        #     "code": version_name,
        #     "entity": alembic_entity,
        #     "description": self.comment
        # }
        # version = sg.create("Version", data)
        return

    def animation(self):
        self.update_shotgun()
        return


class MyWindow(QtWidgets.QDialog):
    def __init__(self):
        self.ui = self.import_ui()
        return

    def import_ui(self):
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui
