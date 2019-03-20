"""
from shotgun.publish import animation as sg
reload(sg)
maya_file = pm.sceneName()  # user input
anim = sg.Publish(maya_file=maya_file)
anim.version()  # versions up by default, but not the maya file!
anim.rich_media()  # anim.rich_media(playblast=1, range="sg")
anim.attributes = ["stripNamespaces", "uvWrite", "worldSpace", "writeVisibility", "eulerFilter", "writeUVSets"]
anim.animation()
anim.update_shotgun()


from shotgun.publish import animation as sg
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
from . import camera; reload(camera)
from PySide2 import QtCore, QtWidgets, QtUiTools
from pymel.core.system import Workspace, FileReference, referenceQuery, exportAsReference, importFile, openFile, newFile
from pymel.util import path
from imghdr import what

import pymel.core as pm
workspace = Workspace()


def get_window():
    global mw
    try:
        mw.ui.close()
    except:
        pass

    mw = MyWindow()
    mw.ui.show()


class Publish(object):
    def __init__(self, thumbnail=None, playblast=None, maya_file=None, alembic_directory=None, comment="",
                 attributes=None, active_geometry=None):
        for k, v in vars().iteritems():
            if k is "self" or k is "comment":
                continue
            if v:
                v = path(v)
            setattr(self, k, v)

        # written for maya standalone and UI, maya_file needs a file for this class to work
        # assumes current scene unless specified otherwise
        if pm.sceneName():
            if not self.maya_file:
                self.maya_file = path(pm.sceneName())
        else:
            pm.warning("No maya file opened.")
            return

        self.comment = comment

        # single_frame and multi_frame creates alembic files for each node
        self.alembic_file = None

        # alembics previously published into /cache/alembic, but will now contain only the latest version
        # all publishes will be recorded in alembic directory /publish/08_Animation/Shot_###/ver_###
        self.workspace_alembic = path(workspace.expandName(workspace.fileRules["Alembic"]))
        return

    def version(self, up=1, current=None, next=None):
        """
        gets/creates version directory for instance of Publish
        updates self.alembic_directory
        creates first/next version or gets current version

        ***not necessary to use version() if alembic_directory contains a value when calling Publish()***

        :param up: (bool) by default versions up, otherwise gets current
        :param current: latest version in alembic directory
        :param next: version to be created
        :return: latest or current alembic version, depending on 'up' param
        """
        # get parent directory containing all versions
        alembic_directory = path(workspace.expandName(workspace.fileRules["scene"]).replace("scenes", "published"))
        
        # ensure folder exists
        path.makedirs_p(alembic_directory)

        # get current and next version
        version = alembic_directory.dirs("ver_*")
        if version:
            current = sorted(version)[::-1][0]
            next = path(current[:-3] + str(int(current[-3:]) + 1).zfill(3))
        else:
            current = next = alembic_directory.joinpath("ver_001")

        if up:
            alembic_directory = next
        else:
            alembic_directory = current

        self.alembic_directory = alembic_directory.normpath()
        path.makedirs_p(self.alembic_directory)
        return self.alembic_directory

    def rich_media(self, playblast=0, size=(1920, 1080), range="playback"):
        # KNOWN ISSUE: UP TO A CERTAIN NUMBER OF PLAYBLASTS/THUMBNAILS, HIGH RES NEEDS TO DOWN GRADE RESOLUTION
        # KNOWN ISSUE: DOESN'T PLAYBLAST CORRECTLY IF ACTIVE VIEW IS SCRIPT EDITOR
        # KNOWN ISSUE: PLAYBLAST STALLS THE USER FROM RESUMING WORK
        # TODO: CREATING PLAYBLASTS AND THUMBNAILS VIA MAYA STANDALONE SHOULD FIX KNOWN ISSUES
        active_editor = pm.playblast(ae=1)
        active_camera = pm.lookThru(active_editor, q=1)
        pm.lookThru(active_editor, "render_cam")

        # THUMBNAIL
        current_time = pm.currentTime(q=1)
        thumbnail = path(self.alembic_directory.joinpath("thumbnail.jpg")).normpath()
        self.thumbnail = pm.playblast(
            frame=current_time,
            format="image",
            editorPanelName=active_editor,  # perspective view
            completeFilename=thumbnail,
            percent=100,
            compression="jpg",
            quality=100,
            widthHeight=size,  # option --> (960, 540)
            viewer=0,
            forceOverwrite=1,
            clearCache=1,
            offScreen=1
        )

        if not playblast:
            pm.lookThru(active_editor, active_camera)  # set persp view back to original camera
            return self.thumbnail, self.playblast

        # PLAYBLAST
        # range is "playback"
        start_time, end_time = pm.playbackOptions(q=1, min=1), pm.playbackOptions(q=1, max=1)
        if range is "sg":
            shot_name = path(workspace.fileRules["scene"]).basename()
            frame_range = sg.find_one(
                "Shot",
                [
                    ["project", "is", project],
                    ["code", "is", shot_name]
                ],
                ["sg_frame_range"]
            )["sg_frame_range"]
            start_time, end_time = [int(t) for t in frame_range.split("-")]
        elif range is "animation":
            start_time, end_time = pm.playbackOptions(q=1, ast=1), pm.playbackOptions(q=1, aet=1)

        playblast = path(self.alembic_directory.joinpath("playblast.mov")).normpath()
        self.playblast = pm.playblast(
            startTime=start_time,
            endTime=end_time,
            format="qt",
            editorPanelName=active_editor,  # perspective view
            filename=playblast,
            percent=100,
            compression="H.264",
            quality=100,
            widthHeight=size,  # option --> (960, 540)
            viewer=0,
            forceOverwrite=1,
            clearCache=1,
            offScreen=1
        )
        pm.lookThru(active_editor, active_camera)  # set persp view back to original camera
        return self.thumbnail, self.playblast

    def get_in_view(self, **kwargs):
        kwargs.update({"av": 1, "alo": 0, "ns": 1, "pm": 1})  # defaults

        import maya.OpenMaya as om
        import maya.OpenMayaUI as omUI

        temp_camera = pm.camera()[0].rename("temp_CAM")
        window = pm.window(title="temp_WIN")
        pm.frameLayout(lv=0)
        panel = pm.modelPanel(label="Persp View")
        pm.showWindow()
        pm.modelEditor(panel, e=1, camera=temp_camera, **kwargs)
        pm.viewFit(temp_camera, all=1)

        view = omUI.M3dView.active3dView()
        om.MGlobal.selectFromScreen(0, 0, view.portWidth(), view.portHeight(), om.MGlobal.kReplaceList)

        pm.deleteUI(window)
        pm.delete(temp_camera)
        self.active_geometry = set(pm.ls(sl=1))
        pm.select(cl=1)
        return

    def single_frame(self, top_node=None):
        """
        alembic cache objects with no animation. uses self.attributes to enable alembic attributes. uses
        self.alembic_directory to store alembic files

        from shotgun.publish import animation as sg
        reload(sg)
        maya_file = pm.sceneName()  # user input
        anim = sg.Publish(maya_file=maya_file)
        anim.version(up=0)  # use latest alembic directory
        anim.attributes = ["stripNamespaces", "uvWrite", "worldSpace", "writeVisibility", "eulerFilter", "writeUVSets"]
        anim.single_frame(top_node="model_set_GEO")

        :param top_node: (str) the name of the node to cache, its children exports too
        :return: (str) path object of the full path file
        """
        if not self.alembic_directory:
            pm.warning(">> Set alembic directory.")
            return

        top_node = pm.PyNode(top_node)
        self.alembic_file = self.alembic_directory.joinpath(top_node+".abc").replace("\\", "/")
        nodes = set(top_node.getChildren(ad=1)).intersection(self.active_geometry)

        export = ""
        for node in nodes:
            export += '-root "{}" '.format(node.longName())

        job_arg = '-frameRange {0:.0f} {0:.0f} -dataFormat ogawa {1}-file "{2}"'.format(
            pm.currentTime(),
            export,
            self.alembic_file
        )

        if self.attributes:
            attributes = [job_arg] + self.attributes
            job_arg = " -".join(attributes)

        pm.select(nodes)
        pm.AbcExport(j=job_arg)
        self.alembic_file = path(self.alembic_file).normpath()
        self.clean_alembic()
        return self.alembic_file

    def multi_frame(self, top_node=None):
        """
        alembic cache objects with animation. uses self.attributes to enable alembic attributes. uses
        self.alembic_directory to store alembic files

        from shotgun.publish import animation as sg
        reload(sg)
        maya_file = "C:\Users\%USERPROFILE%\Documents\shot_000.ma"  # user input
        anim = sg.Publish(maya_file=maya_file)
        anim.version(up=1)  # versions up to the next alembic directory
        anim.attributes = []  # no attributes to enable
        anim.multi_frame(top_node="hero_RIG")

        :param top_node: (str) the name of the node to cache, its children exports too
        :return: (str) path object of the full path file
        """
        self.get_in_view()
        if not self.alembic_directory:
            pm.warning(">> Set alembic directory.")
            return

        top_node = pm.PyNode(top_node)
        self.alembic_file = self.alembic_directory.joinpath(top_node+".abc").replace("\\", "/")
        shot_name = path(workspace.fileRules["scene"]).basename()
        frame_range = sg.find_one(
            "Shot",
            [
                ["project", "is", project],
                ["code", "is", shot_name]
            ],
            ["sg_frame_range"]
        )["sg_frame_range"]
        start_time, end_time = [int(t) for t in frame_range.split("-")]

        nodes = set(top_node.getChildren(ad=1)).intersection(self.active_geometry)

        abc_hide = pm.createDisplayLayer(self.active_geometry, n="abc_hide", e=0, nr=0)
        for attr in ["playback", "texturing", "shading", "visibility"]:
            abc_hide.setAttr(attr, 0)
        abc_show = pm.createDisplayLayer(nodes, n="abc_show", e=0, nr=0)

        export = ""
        for node in nodes:
            export += '-root "{}" '.format(node.longName())

        job_arg = '-frameRange {} {} -dataFormat ogawa {}-file "{}"'.format(
            start_time,
            end_time,
            export,
            self.alembic_file
        )

        if self.attributes:
            attributes = [job_arg] + self.attributes
            job_arg = " -".join(attributes)

        pm.select(nodes)
        pm.AbcExport(j=job_arg)
        self.alembic_file = path(self.alembic_file).normpath()
        self.clean_alembic()
        return self.alembic_file

    def clean_alembic(self):
        working_file = pm.sceneName()
        newFile(f=1)

        nodes = set(importFile(self.alembic_file, rnn=1))

        outliner = set(pm.ls(assemblies=1))
        children = nodes.intersection(outliner)
        top_node = pm.group(em=1, n=self.alembic_file.namebase)
        pm.parent(children, top_node)
        for at in "trs":
            for ax in "xyz":
                top_node.setAttr(at + ax, lock=1, keyable=0, cb=0)
        top_node.setAttr("v", lock=1, keyable=0, cb=0)

        temp_alembic_file = self.alembic_file.replace(".abc", "_.abc").replace("\\", "/")

        job_arg = '-frameRange {0:.0f} {0:.0f} -dataFormat ogawa -root "{1}" -file "{2}"'.format(
            pm.currentTime(),
            top_node,
            temp_alembic_file
        )

        alembic_node = pm.ls(type="AlembicNode")

        if alembic_node:
            job_arg = '-frameRange {} {} -dataFormat ogawa -root "{}" -file "{}"'.format(
                alembic_node[0].getAttr("startFrame"),
                alembic_node[0].getAttr("endFrame"),
                top_node,
                temp_alembic_file
            )
        pm.select(top_node)
        pm.AbcExport(j=job_arg)
        openFile(working_file, f=1)
        self.alembic_file.remove_p()
        self.alembic_file = path(temp_alembic_file)
        self.alembic_file = self.alembic_file.rename(self.alembic_file.replace("_.abc", ".abc"))
        return

    def update_shotgun(self):
        # GET ENTITY - get the latest alembic entity for the shot
        entity_name = path(workspace.fileRules["scene"]).basename() + "_Anim"

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

    def animation(self, single=[], multi=[], comment="Alembics:"):
        """
        Contains .abc as they're created, path comes from self.version():
        04_Maya/published/08_Animation/Shot_###/alembic/ver_###

        Contains only the latest of all .abc for the given shot, path comes from set_project():
        04_Maya/scenes/06_Cache/08_Animation/Shot_###

        reload(sg)
        anim = sg.Publish(maya_file=pm.sceneName())
        anim.version(up=0)
        anim.attributes = ["stripNamespaces", "uvWrite", "worldSpace", "writeVisibility", "eulerFilter", "writeUVSets"]
        single = ["model_set_GEO"]
        multi = ["hero_RIG"]
        anim.animation(single=single, multi=multi)
        """
        # Creating single and multi frame alembics
        self.get_in_view()
        alembics = []
        for top_node in single:
            alembics += [self.single_frame(top_node)]

        for top_node in multi:
            alembics += [self.multi_frame(top_node)]

        # Copying alembics from /published to /06_Cache
        all_directory = path(workspace.expandName(workspace.fileRules["Alembic"]))
        
        for abc in alembics:
            dst = all_directory.joinpath(abc.basename())
            path.copy(abc, dst)

        # Adding automated comment
        if self.comment:
            self.comment += "\n\n"

        if alembics:
            self.comment += comment
            for abc in alembics:
                self.comment += "\n" + abc.basename()
        return alembics

    def proxy(self, mode="add", remove=[], add=[], export=[]):
        """
        Intended to handle 1 proxy file per shot.

        Add mode creates proxy groups:
        reload(sg)
        anim = sg.Publish(maya_file=pm.sceneName())
        anim.version(up=1)
        anim.attributes = ["stripNamespaces", "uvWrite", "worldSpace", "writeVisibility", "eulerFilter", "writeUVSets"]
        anim.proxy(mode="add")

        Export mode caches proxy groups:
        reload(sg)
        anim = sg.Publish(maya_file=pm.sceneName())
        anim.version(up=1)
        anim.attributes = ["stripNamespaces", "uvWrite", "worldSpace", "writeVisibility", "eulerFilter", "writeUVSets"]
        anim.proxy(mode="export", export=["Shot_###"])

        Remove mode removes proxy from fileRule["alembicCache"] (/06_Cache):
        reload(sg)
        anim = sg.Publish(maya_file=pm.sceneName())
        anim.version(up=0)
        anim.proxy(mode="remove", remove=["Shot_006"])

        :param mode: add, export, remove
        :param remove: (str) proxy from fileRule["alembicCache"] (/06_Cache)
        :param add: (str) by default creates Shot_###_PXY, accepts names with or without "_PXY"
        :param export: ([[single][multi]])
        :return:
        """
        if "add" == mode:
            if not add:
                name = path(workspace.fileRules["scene"]).basename()
                if pm.ls("*{}_PXY".format(name)):
                    pm.warning(">> {} already exists, nothing to create.".format(name))
                    return
                else:
                    add = [name]  # Shot_###_PXY

            proxies = []
            for name in add:
                if "_PXY" not in name:
                    name += "_PXY"
                if pm.ls("*{}".format(name)):
                    continue
                pm.group(name=name, em=1)
                proxies += [name]
            pm.select(cl=1)

            if proxies:
                print "\n".join([">> Created the following proxy groups:"] + proxies)
            else:
                pm.warning(">> Already exists, nothing to create.")
        elif "export" == mode:
            # exports proxies as single or multi frame alembics
            # they are first imported if they are already referenced
            single_proxies = set()
            for single in export[0]:
                if referenceQuery(single, inr=1):
                    single_ref = FileReference(single)
                    single_ref.importContents()
                single_proxies.add(single)
            
            multi_proxies = set()
            for multi in export[1]:
                if referenceQuery(multi, inr=1):
                    multi_ref = FileReference(multi)
                    multi_ref.importContents()
                multi_proxies.add(multi)
            
            comment = "Proxies:"
            alembics = self.animation(single=single_proxies, multi=multi_proxies, comment=comment)

            if alembics:
                print "\n>> Exported the following proxies:", self.comment.split(comment)[1],
        elif "remove" == mode:
            cache_directory = path(workspace.expandName(workspace.fileRules["alembicCache"]))

            alembics, skipped = [], []
            for abc in remove:
                abc_edit = abc.replace("PXY", "*")
                search = cache_directory.files("*{}*PXY*".format(abc_edit))
                if len(search) == 1:
                    alembics += search
                    path.remove_p(alembics[-1])
                else:
                    skipped += [abc]

            if skipped:
                pm.warning(" ".join([">> Skipped:"] + skipped))

            # Adding automated comment
            if self.comment:
                self.comment += "\n"

            if alembics:
                self.comment += "Removed:"
                for abc in alembics:
                    self.comment += "\n" + abc.basename()
        else:
            pm.warning(">> Mode is either 'add', 'export', or 'remove'.")


class MyWindow(Publish, QtWidgets.QDialog):
    def __init__(self, **kwargs):
        super(MyWindow, self).__init__(**kwargs)
        self.ui = self.import_ui()
        self.init_ui()
        self.CameraTools = camera.CameraTools()

    def import_ui(self):
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    def change_output(self):
        output_text = self.ui.input_lne.text() + "_PXY"
        self.ui.output_lbl.setText(output_text)
        return

    def create_proxy(self):
        name = self.ui.input_lne.text()
        self.proxy(mode="add", add=[name])
        return

    def move(self, side):
        move = {
            "right": {
                "from": self.ui.multi_lsw,
                "to": self.ui.single_lsw
            },
            "left": {
                "from": self.ui.single_lsw,
                "to": self.ui.multi_lsw
            }
        }

        from_lsw = move[side]["from"]
        to_lsw = move[side]["to"]

        selected = from_lsw.selectedItems()
        for item in selected:
            from_lsw.takeItem(from_lsw.row(item))
            to_lsw.addItem(item)
        return

    def plus(self):
        """
        Adding selection to multi-frame list view for caching
        :return:
        """
        selected = pm.selected()
        if not selected:
            pm.warning(">> Nothing selected to add.")
            return

        all_items = []
        for lsw in [self.ui.multi_lsw, self.ui.single_lsw]:
            for i in range(lsw.count()):
                all_items += [lsw.item(i)]

        skipping, adding = [], []
        for sel in selected:
            skip = None
            for item in all_items:
                if item.toolTip() in sel.longName():
                    skip = sel
                    skipping += [str(skip)]
                    break
            if not skip:
                adding += [sel]

        for i, item in enumerate(adding):
            lsw_item = QtWidgets.QListWidgetItem(str(item))
            lsw_item.setToolTip(item.longName())
            self.ui.multi_lsw.insertItem(i, lsw_item)

        if skipping:
            pm.warning(">> Skipping the following:")
            print "\n".join(skipping)
        return

    def minus(self):
        for item in self.ui.multi_lsw.selectedItems():
            self.ui.multi_lsw.takeItem(self.ui.multi_lsw.row(item))
            
        for item in self.ui.single_lsw.selectedItems():
            self.ui.single_lsw.takeItem(self.ui.single_lsw.row(item))
        return

    def edit(self, sign):
        if sign == "plus":
            self.plus()
        elif sign == "minus":
            self.minus()
        return

    def init_ui(self):
        # PROXY
        shot_name = path(workspace.fileRules["scene"]).basename()
        self.ui.input_lne.textChanged.connect(self.change_output)
        self.ui.input_lne.setText(shot_name)
        self.ui.proxy_btn.clicked.connect(self.create_proxy)

        # MULTI FRAME - excludes cameras and proxy nulls without geometry
        # list widget item displays item short name, and its tool tip contains its long name
        items = set(pm.ls(assemblies=1))
        remove = set()
        for item in items:
            has_mesh = item.getChildren(ad=1, type="mesh")
            has_nurbs = item.getChildren(ad=1, type="nurbsSurface")
            is_grouped = item.getChildren(type="transform")

            if has_mesh or has_nurbs and is_grouped:
                continue
            else:
                remove.add(item)

        items.difference_update(remove)

        for item in items:
            lsw_item = QtWidgets.QListWidgetItem(str(item))
            lsw_item.setToolTip(item.longName())
            self.ui.multi_lsw.addItem(lsw_item)

        # CENTER BUTTONS
        self.ui.right_btn.clicked.connect(lambda x="right": self.move(x))
        self.ui.left_btn.clicked.connect(lambda x="left": self.move(x))

        self.ui.plus_btn.clicked.connect(lambda x="plus": self.edit(x))
        self.ui.minus_btn.clicked.connect(lambda x="minus": self.edit(x))

        # PUBLISH
        self.ui.publish_btn.clicked.connect(self.run)
        return

    def run(self):
        """
        Automated comments contain what is in the alembic directory
        """
        # TESTING - uses the same maya scene file and version folder
        self.version(up=0)
        working_file = pm.sceneName()
        published_file = self.alembic_directory.joinpath(
            "{}_original.{}.ma".format(
                path(workspace.fileRules["scene"]).basename(),
                str(int(self.alembic_directory.basename().split("_")[1])).zfill(4)
            )
        )
        # path(working_file).copy2(published_file)

        # # - increment and save the current working file, and save a copy to the published version folder
        # self.version()
        # from shotgun import checkout_scene
        # reload(checkout_scene)
        # checkout = checkout_scene.Checkout()
        # working_file = checkout.run(checkout_type="increment")
        # published_file = self.alembic_directory.joinpath(
        #     "{}_original.{}.ma".format(
        #         path(workspace.fileRules["scene"]).basename(),
        #         str(int(self.alembic_directory.basename().split("_")[1])).zfill(4)
        #     )
        # )
        # path(working_file).copy2(published_file)

        # ALEMBICS - begin by creating alembics, then camera and playblast, and finally update shotgun

        # start with user comment
        self.comment += "{}".format(self.ui.comment_txt.toPlainText())

        # separate proxies from the list view, proxies run their own command from Publish()
        multi_abc, multi_pxy = [], []
        for i in range(self.ui.multi_lsw.count()):
            maya_obj = self.ui.multi_lsw.item(i).toolTip()
            if "PXY" in maya_obj:
                multi_pxy += [maya_obj]
            else:
                multi_abc += [maya_obj]

        single_abc, single_pxy = [], []
        for i in range(self.ui.single_lsw.count()):
            maya_obj = self.ui.single_lsw.item(i).toolTip()
            if "PXY" in maya_obj:
                single_pxy += [maya_obj]
            else:
                single_abc += [maya_obj]

        # all alembic attributes in the UI are checked by default
        # collect them and use them to create single and multi alembics
        abc_attributes = []
        if self.ui.world_cbx.isChecked():
            abc_attributes.append("worldSpace")
        if self.ui.writevisibility_cbx.isChecked():
            abc_attributes.append("writeVisibility")
        if self.ui.eulerfilter_cbx.isChecked():
            abc_attributes.append("eulerFilter")
        if self.ui.uvwrite_cbx.isChecked():
            abc_attributes.append("uvWrite")
        if self.ui.namespace_cbx.isChecked():
            abc_attributes.append("stripNamespaces")
        if self.ui.writeuvsets_cbx.isChecked():
            abc_attributes.append("writeUVSets")

        # create alembics
        self.maya_file = published_file
        self.attributes = abc_attributes
        self.animation(single=single_abc, multi=multi_abc)
        self.proxy(mode="export", export=[single_pxy, multi_pxy])

        # CAMERAS
        # cameras built into animation shots should always have a render_cam_RIG, see camera.py
        # process_data() works with imported nodes only
        # render_cam_RIG needs to be imported, it is referenced from the build scene tool
        if self.ui.camera_cbx.isChecked():
            if referenceQuery("render_cam_RIG", inr=1):
                render_camera = FileReference("render_cam_RIG")
                render_camera.importContents()

            # export selection as reference
            self.CameraTools.comment += "Published from Animation:\n{}".format(path(pm.sceneName()).basename())
            self.CameraTools.process_data()
            pm.select("render_cam_RIG")
            exportAsReference(self.CameraTools.camera_file, namespace=":")

            # publish camera and append comment to animation
            self.CameraTools.update_shotgun()
            self.comment += "\n\nCameras:\n{}".format(self.CameraTools.version_name)

        # PLAYBLAST - creates playblast and updates shotgun with video, otherwise a thumbnail is used
        if self.ui.skip_cbx.isChecked():
            self.rich_media(playblast=1, size=(1920, 1080), range="playback")

        # updates shotgun at the end to get all the comments
        # self.update_shotgun()
        self.ui.close()
        return
