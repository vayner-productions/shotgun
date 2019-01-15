"""
initialize camera lets users import the vayner render camera rig located in shotgun/render_cam_RIG
or another camera. this other camera is intended to import a tracked camera, but can also animator's
own camera.
'other camera' also creates top node 'render_cam_RIG' and in case there are multiple cameras in the
scene, renames only camera child to top node 'render_cam'

lastly, the camera to be published in any shot scene process and updates sg_frame_range. it does
this by turning the camera rig into a referenced object. in scenes already containing referenced
camera, ref cam is imported, namespace removed, and turned into a new reference (versioned up)
"""


import sgtk
from PySide2 import QtCore, QtWidgets, QtUiTools
import pymel.util.common as ppath
import pymel.core as pm

eng = sgtk.platform.current_engine()
project_name = eng.context.project["name"]
sg = eng.shotgun


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
        if camera_file is None:
            camera_path = ppath.path(__file__).dirname().joinpath("render_cam_RIG")
            camera_file = sorted(camera_path.files())[::-1][0]  # ensures latest version
        nodes = pm.system.importFile(camera_file, defaultNamespace=1, returnNewNodes=1)
        top_node = pm.ls(nodes, assemblies=1)[0]
        self.ui.close()
        print ">> loaded: {}".format(top_node),
        return top_node

    def load_other(self, camera_file=None):
        if camera_file is None:
            # open file dialog to 03_Cameras and filter for maya files
            filters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)"
            workspace = pm.system.Workspace()
            shot = ppath.path(workspace.fileRules["scene"]).basename()
            camera_path = ppath.path(workspace.getName()).joinpath("scenes", "03_Cameras", shot).normpath()
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
            camera_filename = ppath.path(camera_file).basename().stripext()
            imported = pm.group(top_nodes, name=camera_filename+"_IMPORT")
            pm.select(imported, camera_top_node)  # for testing, delete later
        self.ui.close()
        print ">> loaded: {}".format(imported),
        return

    def publish_camera(self):
        camera_top_node = pm.ls("render_cam_RIG")[0]
        cameras = camera_top_node.getChildren(ad=1, typ="camera")
        if len(cameras) > 1:
            pm.warning(">> too many cameras in render_cam_RIG, choose one")
            return
        elif len(cameras) == 0:
            pm.warning("place camera in render_cam_RIG")
            return
        else:
            render_cam = cameras[0].getParent().rename("render_cam")
            workspace = pm.system.Workspace()
            shot = ppath.path(workspace.fileRules["scene"]).basename()
            camera_path = ppath.path(workspace.getName()).joinpath("published", "03_Cameras", shot).normpath()
            camera_path.makedirs_p()

            pm.select(camera_top_node)
            camera_files = sorted(camera_path.files("{}_original.*.ma".format(shot)))[::-1]
            if camera_files:
                latest_file = camera_files[0].split(".")
                latest_file[1] = str(int(latest_file[1]) + 1).zfill(4)
                camera_file = ppath.path(".".join(latest_file))
                pm.system.exportAsReference(camera_file, namespace=":")
            else:
                camera_file = camera_path.__div__("{}_original.0001.ma".format(shot))
                pm.system.exportAsReference(camera_file, namespace=":")
            print ">> published render_cam_RIG to shotgun",

        try:
            imported = pm.ls("*_IMPORT")[0]
            if not imported.getChildren():
                pm.delete(imported)
        except:
            pass
        self.ui.close()
        return

    def init_ui(self):
        self.ui.vayner_btn.clicked.connect(self.load_vayner)
        self.ui.other_btn.clicked.connect(self.load_other)
        self.ui.publish_btn.clicked.connect(self.publish_camera)
        return
