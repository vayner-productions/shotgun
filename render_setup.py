import pymel.core as pm
import pymel.util.path as pth
from PySide2 import QtCore, QtWidgets, QtUiTools
import os
workspace = pm.system.workspace
import mtoa.aovs as aovs
from mtoa.core import createOptions


def aovs_setup(lights):
    """updating render settings AOVs tab"""
    # enable beauty
    createOptions()
    arnold_options = pm.PyNode("defaultArnoldRenderOptions")
    arnold_options.aovMode.set(1)

    # enable default aovs
    default_aovs = ["diffuse_direct",
                    "diffuse_indirect",
                    "specular_direct",
                    "specular_indirect",
                    "sss_direct",
                    "sss_indirect",
                    "N",
                    "P",
                    "Z",
                    "crypto_asset",
                    "crypto_material",
                    "crypto_object",
                    "AO"]
    # default_aovs.extend(lights)
    for aov in default_aovs:
        if not aovs.AOVInterface().getAOVNode(aov):
            aovs.AOVInterface().addAOV(aov)

    # enable custom aovs
    # ambient occlusion
    ao_name = "aiAmbientOcclusion"
    if not pm.ls(type=ao_name):
        ao_aov = pm.PyNode("aiAOV_AO")
        ao_shader = pm.shadingNode(ao_name, asShader=1)
        ao_sg = pm.sets(name=ao_name + "SG", empty=1, renderable=1, noSurfaceShader=1)
        ao_shader.outColor >> ao_aov.defaultValue
        ao_shader.outColor >> ao_sg.surfaceShader

    # # create light group for each of the lights
    # for light in lights:
    #     shape = pm.PyNode(light).getShape()
    #     shape.aiAov.set(light)

    # merge aovs
    arnold_driver = pm.PyNode("defaultArnoldDriver")
    arnold_driver.mergeAOVs.set(1)
    arnold_driver.halfPrecision.set(1)
    print ">> aov setup"
    return


def render_setup(camera):
    """updating render settings common tab"""
    #
    # image file rule
    #

    # make sure images file rule is set to default
    workspace.fileRules["images"] = "images"

    #
    # render settings
    #

    shot_id = os.path.basename(workspace.fileRules["scene"])
    filename_prefix = "{0}/<Version>/<RenderLayer>/{0}_<Version>_<RenderLayer>".format(shot_id)
    start_time, end_time = pm.playbackOptions(q=1, ast=1), pm.playbackOptions(q=1, aet=1)

    next_version = None
    shot_path = pth(pm.workspace.expandName(pm.workspace.fileRules["images"]) + "/" + shot_id)
    shot_path.makedirs_p()

    versions = shot_path.dirs("v*")
    if versions:
        latest_path = sorted(shot_path.dirs("v*"))[::-1][0]
        current_version = latest_path.basename()
        if latest_path.files():
            next_version = "v" + str(int(current_version[1:]) + 1).zfill(3)
        else:
            next_version = current_version
    else:
        next_version = "v001"

    # update default render globals
    drg = pm.PyNode("defaultRenderGlobals")
    drg.renderVersion.set(next_version)
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
    return


def get_window():
    global mw
    try:
        mw.ui.close()
    except:
        pass

    # is_light = 0
    #
    # lights = list(set(pm.nodeType("shape", derived=True, isTypeName=True)).intersection(
    #     pm.listNodeTypes("light")))
    # for l in pm.ls(type=lights):
    #     light = str(l.getParent())
    #     if (len(light) == 8) and ("Light_" in light) and (light[-2:].isdigit()):
    #         is_light = 1
    #     else:
    #         is_light = 0
    #         break
    #
    # if not is_light:
    #     pm.warning(">> use arnold lights with this naming convention: Light_##")

    is_camera = 0

    for c in pm.ls(type="camera"):
        camera = str(c.getParent())
        if camera not in ["persp", "top", "front", "side"]:
            is_camera = 1
            break

    if not is_camera:
        pm.warning(">> could not find render camera in scene")

    # if is_light and is_camera:
    #     mw = MyWindow()
    #     mw.ui.show()
    mw = MyWindow()
    mw.ui.show()


class MyWindow(QtWidgets.QDialog):
    def __init__(self):
        self.ui = self.import_ui()
        self.init_ui()

    def import_ui(self):
        ui_path = __file__.split(".")[0] + "_.ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    def init_ui(self):
        # lights = set(pm.ls("Light_*", type="transform"))
        # all_maya_lights = set(light.getParent() for light in pm.ls(type="light"))
        # arnold_lights = list(lights.difference(all_maya_lights))
        #
        # for light in arnold_lights:
        #     light = str(light)
        #     if (len(light) == 8) and ("Light_" in light) and (light[-2:].isdigit()):
        #         self.ui.light_lsw.addItem(light)

        for c in pm.ls(type="camera"):
            camera = str(c.getParent())
            if camera not in ["persp", "top", "front", "side"]:
                self.ui.camera_lsw.addItem(camera)

        self.ui.render_btn.clicked.connect(self.run)
        return

    def run(self):
        # lights = [sel.text() for sel in self.ui.light_lsw.selectedItems()]
        camera = [sel.text() for sel in self.ui.camera_lsw.selectedItems()]

        if not camera:
            pm.warning(">> selection incomplete, select render camera")
            return

        # if lights:
        #     aovs_setup(lights)

        camera = camera[0]  # only one camera selection
        if camera:
            render_setup(camera)
            render_root = pm.workspace.expandName(pm.workspace.fileRules["images"])
            filename = pm.rendering.renderSettings(firstImageName=1)[0]
            output_path = pth("/".join([render_root, filename])).dirname().dirname()
            output_path.makedirs_p()
        print ">> render setup complete",
        self.ui.close()
        return
