"""
initialize camera lets users import the vayner render camera rig located in shotgun/render_cam_RIG
or another camera. this other camera is intended to import a tracked camera, but can also animator's
own camera.
'other camera' also creates top node 'render_cam_RIG' and in case there are multiple cameras in the
scene, renames only camera child to top node 'render_cam'

lastly, the camera to be published in any shot scene process and updates sg_frame_range. it does
this by turning the camera rig into a referenced object. in scenes already containing referenced
camera, ref cam is imported, namespace removed, and turned into a new reference (versioned up)

if there's a new tracked camera to publish, open empty scene, set project to its respective shot, and publish
"""


import sgtk
from PySide2 import QtCore, QtWidgets, QtUiTools
from pymel.util import path
import pymel.core as pm

engine = sgtk.platform.current_engine()
sg = engine.shotgun
project = sg.find_one("Project", [["name", "is", engine.context.project["name"]]])


def get_window():
    global mw
    try:
        mw.ui.close()
    except:
        pass

    mw = MyWindow()
    mw.ui.show()


class MyWindow(QtWidgets.QDialog):
    def __init__(self):
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

    def load_vayner(self, camera_file=None):
        """loads in-house camera rig"""
        if camera_file is None:
            camera_path = path(__file__).dirname().joinpath("render_cam_RIG")
            camera_file = sorted(camera_path.files())[::-1][0]  # ensures latest version
        nodes = pm.system.importFile(camera_file, defaultNamespace=1, returnNewNodes=1)
        top_node = pm.PyNode("render_cam_RIG")  # pm.ls(nodes, assemblies=1)[0]
        self.ui.close()  # doesn't seem to matter if no ui is showing, can run in script mode too
        print ">> loaded: {}".format(top_node),
        return top_node

    def load_other(self, camera_file=None):
        """intended to load tracked camera, but can also be used to load animator's own camera"""
        # open file dialog to 03_Cameras and filter for maya files
        if camera_file is None:
            filters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)"
            workspace = pm.system.Workspace()
            shot = path(workspace.fileRules["scene"]).basename()
            camera_path = path(workspace.getName()).joinpath("scenes", "03_Cameras", shot).normpath()
            camera_file = pm.fileDialog2(ff=filters, dir=camera_path, fm=1)[0]

        # import camera and place in import group to easily see
        # create render_cam_RIG null for user to place camera in
        # select import and null for user to see results
        nodes = pm.system.importFile(camera_file, defaultNamespace=1, returnNewNodes=1)
        if "render_cam_RIG" not in nodes:
            top_nodes = pm.ls(nodes, assemblies=1)
            camera_top_node = pm.group(em=1, name="render_cam_RIG")
            camera_top_node.setAttr("v", lock=1, k=0, cb=0)
            for at in "trs":
                for ax in "xyz":
                    camera_top_node.setAttr(at + ax, lock=1, k=0, cb=0)
            camera_filename = path(camera_file).basename().stripext()
            imported = pm.group(top_nodes, name=camera_filename+"_IMPORT")
            pm.select(imported, camera_top_node)  # for testing, delete later

        self.ui.close()  # doesn't seem to matter if no ui is showing, can run in script mode too
        print ">> loaded: {}".format(imported),
        return

    def update_shotgun(self, camera_file=None, comment=""):
        """a new version of the camera entity is created, either local or off-site file is attached; logs any changes to
        the frame range"""
        # SHOT - update frame range in shot
        workspace = pm.system.Workspace()
        shot_name = path(workspace.fileRules["scene"]).basename()  # Shot_###
        shot_filters = [
            ["project", "is", project],
            ["code", "is", shot_name]
        ]
        shot_fields = [
            "id",
            "type",
            "sg_frame_range",
            "sg_camera"
        ]
        shot_entity = sg.find_one(
            "Shot",
            shot_filters,
            shot_fields  # used for camera entity updates
        )
        sg_frame_range = "{0:.0f}-{1:.0f}".format(
            pm.playbackOptions(q=1, ast=1),
            pm.playbackOptions(q=1, aet=1)
        )

        if shot_entity["sg_frame_range"] != sg_frame_range:
            comment += "frame range changed from {} to {}".format(
                shot_entity["sg_frame_range"],
                sg_frame_range
            )
            sg.update(
                "Shot",
                shot_entity["id"],
                {"sg_frame_range": sg_frame_range}
            )

        # CAMERA
        # find camera and its latest version linked to the shot
        camera_entity = shot_entity["sg_camera"][0]  # assumes shots are paired with one camera !!!
        version_filters = [
            ["project", "is", project],
            ["entity", "is", camera_entity]
        ]
        version_fields = [
            "id",
            "type",
            "code"
        ]
        version_additional_filter_presets = [
            {
                "preset_name": "LATEST",
                "latest_by": "ENTITIES_CREATED_AT"
            }
        ]
        version_entity = sg.find_one(
            "Version",
            version_filters,
            fields=version_fields,
            additional_filter_presets=version_additional_filter_presets
        )

        # create camera entity's next version
        version_name = camera_entity["name"] + "_v001"
        if version_entity:
            latest_version = version_entity["code"][-3:]
            version_name = version_name[:-3] + str(int(latest_version) + 1).zfill(3)

        data = {
            "project": project,
            "code": version_name,  # Version Name - Shot_004_v001
            "entity": camera_entity,  # Link - Shot_001_Cam entity
            "description": comment,  # Description - comment
        }
        version = sg.create("Version", data)

        # PUBLISH
        camera_display_name = path(camera_file).basename()
        camera_file = camera_file.normpath()
        sg.update("Version",
                  version["id"],
                  {"sg_maya_camera": {
                      "link_type": "local",
                      "local_path": camera_file,
                      "name": camera_display_name}})
        print ">> published render_cam_RIG to shotgun",
        return

    def publish_camera(self, comment=""):
        """publishing anything parented to render_cam_RIG node--incrememnt and saves current file, and saves a copy to
        the published folder"""
        camera_top_node = pm.PyNode("render_cam_RIG")

        cameras = camera_top_node.getChildren(ad=1, typ="camera")
        if len(cameras) > 1:
            pm.warning("too many cameras in render_cam_RIG, choose one")
            return
        elif len(cameras) == 0:
            pm.warning("place camera in render_cam_RIG")
            return

        # - create camera path based on the scene name 04_Maya/published/03_Cameras/Shot_###
        render_cam = cameras[0].getParent().rename("render_cam")
        workspace = pm.system.Workspace()
        shot = path(workspace.fileRules["scene"]).basename()
        camera_path = path(workspace.getName()).joinpath(
            "published",
            "03_Cameras",
            shot).normpath()
        camera_path.makedirs_p()

        # - create the next camera file path from the latest
        camera_files = sorted(camera_path.files("{}_original.*.ma".format(shot)))[::-1]
        camera_file = None
        if camera_files:
            latest_file = camera_files[0].split(".")
            latest_file[1] = str(int(latest_file[1]) + 1).zfill(4)
            camera_file = path(".".join(latest_file))
        else:
            camera_file = camera_path.__div__("{}_original.0001.ma".format(shot))

        try:
            imported = pm.ls("*_IMPORT")[0]
            if not imported.getChildren():
                pm.delete(imported)
        except:
            pass

        # - increment and save the current working file, and save a copy to the published folder
        from . import checkout_scene
        reload(checkout_scene)
        checkout = checkout_scene.Checkout()
        working_file = checkout.increment_file()
        path(working_file).copy2(camera_file)

        self.update_shotgun(camera_file=camera_file, comment=comment)
        self.ui.close()
        return

    def init_ui(self):
        self.ui.vayner_btn.clicked.connect(self.load_vayner)
        self.ui.other_btn.clicked.connect(self.load_other)
        self.ui.publish_btn.clicked.connect(self.publish_camera)
        return
