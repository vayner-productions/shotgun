"""
from shotgun.publish import camera as sg
reload(sg)
sg.get_window("publish_camera")

from shotgun.publish import camera as sg
reload(sg)
sg.get_window("load_camera")
"""
from . import *
from PySide2 import QtCore, QtWidgets, QtUiTools
from pymel.util import path
import pymel.core as pm


def get_window(method):
    """
    :param method: "publish_camera" or "load_camera"
    :return:
    """
    global mw
    try:
        mw.ui.close()
    except:
        pass

    mw = MyWindow()
    getattr(mw, method)()


class CameraTools(object):
    def __init__(self, camera_file=None, comment=""):
        self.camera_file = camera_file
        self.comment = comment
        self.version_name = None
        return

    def load_vayner(self):
        """loads in-house camera rig"""
        if self.camera_file is None:
            camera_path = path(__file__).dirname().dirname().joinpath("render_cam_RIG")  # skips publish module
            self.camera_file = sorted(camera_path.files())[::-1][0]  # ensures latest version
        nodes = pm.system.importFile(self.camera_file, defaultNamespace=1, returnNewNodes=1)
        top_node = pm.PyNode("render_cam_RIG")  # pm.ls(nodes, assemblies=1)[0]
        print ">> loaded: {}".format(top_node),
        return top_node

    def load_other(self):
        """intended to load tracked camera, but can also be used to load animator's own camera"""
        # open file dialog to 03_Cameras and filter for maya files
        if self.camera_file is None:
            filters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)"
            workspace = pm.system.Workspace()
            shot = path(workspace.fileRules["scene"]).basename()
            camera_path = path(workspace.getName()).joinpath("scenes", "03_Cameras", shot).normpath()
            self.camera_file = pm.fileDialog2(ff=filters, dir=camera_path, fm=1)[0]

        # import camera and place in import group to easily see
        # create render_cam_RIG null for user to place camera in
        # select import and null for user to see results
        nodes = pm.system.importFile(self.camera_file, defaultNamespace=1, returnNewNodes=1)
        if "render_cam_RIG" not in nodes:
            top_nodes = pm.ls(nodes, assemblies=1)
            camera_top_node = pm.group(em=1, name="render_cam_RIG")
            camera_top_node.setAttr("v", lock=1, k=0, cb=0)
            for at in "trs":
                for ax in "xyz":
                    camera_top_node.setAttr(at + ax, lock=1, k=0, cb=0)
            camera_filename = path(self.camera_file).basename().stripext()
            imported = pm.group(top_nodes, name=camera_filename+"_IMPORT")
            pm.select(imported, camera_top_node)  # for testing, delete later
            print ">> loaded: {}".format(imported),
        return

    def update_shotgun(self):
        """
        the second of a two-part publish set up, publish_camera() creates maya working and published versions, and calls
        this method to record all the files to the right version

        a new version of the camera entity is created, either local or off-site file is attached; logs any changes to
        the frame range
        """
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
            self.comment += "frame range changed from {} to {}".format(
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
        self.version_name = camera_entity["name"] + "_v001"
        if version_entity:
            latest_version = version_entity["code"][-3:]
            self.version_name = self.version_name[:-3] + str(int(latest_version) + 1).zfill(3)

        data = {
            "project": project,
            "code": self.version_name,  # Version Name - Shot_004_v001
            "entity": camera_entity,  # Link - Shot_001_Cam entity
            "description": self.comment,  # Description - comment
        }
        version = sg.create("Version", data)

        # PUBLISH - local and remote files are treated differently on sg
        camera_display_name = path(self.camera_file).basename()
        if root is None:
            # attaching local file
            self.camera_file = self.camera_file.normpath()
            sg.update("Version",
                      version["id"],
                      {"sg_maya_camera": {
                          "link_type": "local",
                          "local_path": self.camera_file,
                          "name": camera_display_name}})
        else:
            # uploading manually/remotely
            sg.upload("Version",
                      version["id"],
                      self.camera_file,
                      field_name="sg_maya_camera",
                      display_name=camera_display_name)
        print "\n>> published render_cam_RIG to shotgun",  # checkout_scene.py called in publish_camera() prints
        return

    def process_data(self):
        """
        determines the next camera file and ensures the directory is made
        it is used in part with animation.py to export anim's referenced camera as the next camera version
        :return:
        """
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
        if camera_files:
            latest_file = camera_files[0].split(".")
            latest_file[1] = str(int(latest_file[1]) + 1).zfill(4)
            self.camera_file = path(".".join(latest_file))
        else:
            self.camera_file = camera_path.__div__("{}_original.0001.ma".format(shot))
        return

    def publish_camera(self):
        """publishing anything parented to render_cam_RIG node--incremement and saves current file, and saves a copy to
        the published folder"""
        # determines the next camera file
        self.process_data()

        # cleans up the scene, deletes _IMPORT node
        try:
            imported = pm.ls("*_IMPORT")[0]
            if not imported.getChildren():
                pm.delete(imported)
        except:
            pass

        # - increment and save the current working file, and save a copy to the published folder
        from shotgun import checkout_scene
        reload(checkout_scene)
        checkout = checkout_scene.Checkout()
        working_file = checkout.run(checkout_type="increment")
        path(working_file).copy2(self.camera_file)

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

    def camera_tools(self, method):
        ct = CameraTools()
        if method == "publish_camera":
            ct.comment = self.ui.comment_txt.toPlainText()
        getattr(ct, method)()
        self.ui.close()
        return

    def load_camera(self):
        self.ui.publish_btn.deleteLater()
        self.ui.comment_txt.deleteLater()
        self.ui.setFixedSize(350, 94)
        self.ui.setWindowTitle("Import Camera")

        self.ui.vayner_btn.clicked.connect(lambda x="load_vayner": self.camera_tools(x))
        self.ui.other_btn.clicked.connect(lambda x="load_other": self.camera_tools(x))

        self.ui.show()
        return

    def publish_camera(self):
        self.ui.vayner_btn.deleteLater()
        self.ui.other_btn.deleteLater()
        self.ui.setFixedSize(350, 185)
        self.ui.setWindowTitle("Publish Camera")

        self.ui.publish_btn.clicked.connect(lambda x="publish_camera": self.camera_tools(x))

        self.ui.show()
        return
