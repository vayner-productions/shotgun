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
from imghdr import what

import pymel.core as pm


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
        for k, v in vars().iteritems():
            if k is "self" or k is "comment":
                continue
            if v:
                v = path(v)
            setattr(self, k, v)
        self.comment = comment
        self.alembic_file = None  # why do you need the alembic file... cant remember
        return

    def rich_media(self):
        return self.thumbnail, self.playblast

    def single_frame(self):
        return self.alembic_file

    def multi_frame(self):
        return self.alembic_file

    def update_shotgun(self):
        # GET ENTITY - get the latest alembic entity for the shot
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

        data = {
            "project": project,
            "code": version_name,
            "entity": alembic_entity,
            "description": self.comment
        }
        version = sg.create("Version", data)
        # ATTACHMENTS - local files/directories are updated, whereas remote files/directories are uploaded
        # updating each attachment to the version individually in case they're being uploaded from different places
        # remote publishes are wip, and therefore commented out of use, vayner IT deparment needs to check securities!!!
        if self.maya_file.drive == media_space:
            sg.update(
                "Version",
                version["id"],
                {
                    "sg_maya_file": {
                        "link_type": "local",
                        "local_path": str(self.maya_file.normpath()),
                        "name": str(self.maya_file.basename())
                    }
                }
            )
        else:
            sg.upload(
                "Version",
                version["id"],
                self.maya_file,
                field_name="sg_maya_file",
                display_name=r"{}".format(path(self.maya_file).basename())
            )

        if self.alembic_directory.drive == media_space:
            sg.update(
                "Version",
                version["id"],
                {
                    "sg_alembic_directory": {
                        "link_type": "local",
                        "local_path": str(self.alembic_directory.normpath()),
                        "name": str(self.alembic_directory.basename())
                    }
                }
            )
        else:
            sg.upload(
                "Version",
                version["id"],
                self.alembic_directory,
                field_name="sg_maya_file",
                display_name=r"{}".format(path(self.alembic_directory).basename())
            )

        # THUMBNAIL - ensures play icon appears for videos, images appear as thumbnails, and thumbnail from previous
        # version is reused if user opts out of making a playblast for this version
        if self.playblast and not what(self.playblast):
            sg.upload("Version", version["id"], self.playblast, field_name="sg_uploaded_movie")
            sg.update("Version", version["id"], {"image": None})
        elif self.thumbnail:
            sg.upload_thumbnail("Version", version["id"], self.thumbnail)
        elif not (self.thumbnail or self.playblast):
            sg.share_thumbnail(entities=[version], source_entity=version_entity)
        print "\n>> published animation to shotgun"
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
        self.ui.publish_btn.clicked.connect(self.run)
        return

    def run(self):
        thumbnail = None
        playblast = None
        maya_file = pm.sceneName()
        alembic_directory = None
        comment = ""
        publish = Publish(
            thumbnail=thumbnail,
            playblast=playblast,
            maya_file=maya_file,
            alembic_directory=alembic_directory,
            comment=comment
        )
        publish.update_shotgun()
        self.ui.close()
        return
