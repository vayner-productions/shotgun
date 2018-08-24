import pymel.core as pm
from PySide2 import QtCore, QtWidgets, QtUiTools
import os
workspace = pm.system.workspace


def aovs_setup(lights):
    print ">> aov setup"
    return


def render_setup(camera):
    #
    # image file rule
    #

    # make sure images file rule is set to default
    workspace.fileRules["images"] = "images"

    # create a /images/Shots directory
    shots_dir = workspace.expandName(workspace.fileRules["images"]) + "/Shots"
    try:
        os.makedirs(shots_dir)
    except:
        pass

    #
    # version
    #

    # check version inside images/Shots
    current_version = None
    for ver in os.listdir(shots_dir):
        if ("v" == ver[0]) and (len(ver) == 4) and (ver[1:].isdigit()):
            current_version = ver

    if not current_version:
        current_version = "v001"
        os.makedirs(shots_dir + "/" + current_version)

    # get the next version
    next_version = None
    if not os.listdir(shots_dir + "/" + current_version):
        next_version = current_version  # use empty folder
    else:
        next_version = "v" + str(int(current_version[1:].isdigit()) + 1).zfill(3)

    # create the next version directory
    next_version_dir = shots_dir + "/" + next_version
    try:
        os.makedirs(next_version_dir)
    except:
        pass

    #
    # render settings
    #
    shot_id = os.path.basename(workspace.fileRules["scene"])
    filename_prefix = "Shots/{0}/{1}/<RenderLayer>/{0}".format(shot_id, next_version)
    start_time, end_time = pm.playbackOptions(q=1, ast=1), pm.playbackOptions(q=1, aet=1)

    # update default render globals
    drg = pm.PyNode("defaultRenderGlobals")
    drg.imageFilePrefix.set(filename_prefix)
    drg.animation.set(1)
    drg.putFrameBeforeExt.set(1)
    drg.extensionPadding.set(4)
    drg.startFrame.set(start_time)
    drg.endFrame.set(end_time)

    # update default arnold driver
    dad = pm.PyNode("defaultArnoldDriver")
    dad.ai_translator.set("exr")
    dad.exr_compression.set(3)
    dad.merge_AOVs.set(1)

    # set render camera
    for cam in pm.ls(type="camera"):
        if cam.renderable.get():
            cam.renderable.set(0)
    render_camera = pm.PyNode(camera)
    render_camera.renderable.set(1)
    print ">> render settings"
    return


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
        self.setup_ui()

    def import_ui(self):
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    def init_ui(self):
        [self.ui.light_lsw.addItem(str(light)) for light in pm.ls(type=pm.listNodeTypes("light"))]
        [self.ui.camera_lsw.addItem(str(camera)) for camera in pm.ls(type="camera")]
        return

    def setup_ui(self):
        self.ui.render_btn.clicked.connect(self.run)
        return

    def run(self):
        lights = [sel.text() for sel in self.ui.light_lsw.selectedItems()]
        camera = [sel.text() for sel in self.ui.camera_lsw.selectedItems()]

        if not lights or not camera:
            pm.warning(">> selection incomplete, select light(s) and camera")
            return

        if lights:
            aovs_setup(lights)

        camera = camera[0]  # only one camera selection
        if camera:
            render_setup(camera)
        self.ui.close()
        return
