"""
from shotgun import render_setup as sg
reload(sg)
sg.RenderSettings()

# FOR CUSTOM CHANGES ON VERSION LABEL/FRAME RANGE/CAMERA
from shotgun import render_setup as sg
reload(sg)
sg.RenderSettings()
common = sg.Common()
common.metadata(version_label="ALT_001")
common.frame_range(start=-12, end=0)
common.renderable_cameras(camera="other_cam")
"""

from shotgun import update_timeline
reload(update_timeline)
from pymel.core import workspace, PyNode, ls, shadingNode, sets, listNodeTypes, nodeType
from mtoa.aovs import AOVInterface
aov_ui = AOVInterface()  # could not pass as variable instance in AOVs()


class Common(object):
    def __init__(self):
        self.shot = workspace.fileRules["scene"].rsplit("/", 1)[1]  # Shot_###
        self.drg = PyNode("defaultRenderGlobals")
        self.dad = PyNode("defaultArnoldDriver")
        return

    def file_output(self):
        filename_prefix = r"Shots/{0}/<Version>/<RenderLayer>/{0}_<Version>_<RenderLayer>".format(self.shot)

        self.drg.imageFilePrefix.set(filename_prefix)
        self.dad.ai_translator.set("exr")
        self.dad.exr_compression.set(2)
        self.dad.merge_AOVs.set(1)
        self.dad.halfPrecision.set(1)
        return

    def metadata(self, version_label=None):
        self.drg.animation.set(1)
        self.drg.putFrameBeforeExt.set(1)
        self.drg.extensionPadding.set(4)

        # intended for reusing an old version or experimenting alternate versions
        if version_label:
            self.drg.renderVersion.set(version_label)
            return

        # increments up a version if the latest version has content
        shot_path = workspace.path.joinpath(workspace.fileRules["images"], "Shots", self.shot).normpath()
        shot_path.makedirs_p()

        version_label = "v001"

        versions = shot_path.dirs("v*")
        if versions:
            latest = sorted(versions)[::-1][0]
            version_label = latest.basename()

            if latest.listdir():
                version_label = "v{:03d}".format(int(version_label[1:]) + 1)

        self.drg.renderVersion.set(version_label)
        return

    def frame_range(self, start=None, end=None):
        if start is not None and end is not None:
            self.drg.startFrame.set(start)
            self.drg.endFrame.set(end)
            return

        start, end = update_timeline.get_frame_range()

        self.drg.startFrame.set(start)
        self.drg.endFrame.set(end)
        return

    @staticmethod
    def renderable_cameras(camera="render_cam"):
        for cam in ls(type="camera"):
            render_cam = camera in str(cam)
            if render_cam:
                cam.renderable.set(1)
            else:
                cam.renderable.set(0)
        return


class AOVs(object):
    def __init__(self):
        # RENDER USING ARNOLD RENDERER
        self.drg = PyNode("defaultRenderGlobals")
        self.drg.currentRenderer.set("arnold")
        return

    def maya_render_view(self):
        daro = PyNode("defaultArnoldRenderOptions")
        daro.aovMode.set(1)
        return

    def aov_browser(self, default_aovs=[]):
        default_aovs = list(set(
            default_aovs +
            [
                "diffuse_direct",
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
                "AO"
            ]
        ))

        for aov in default_aovs:
            if not aov_ui.getAOVNode(aov):
                aov_ui.addAOV(aov)

        ao_name = "aiAmbientOcclusion"
        if not ls(type=ao_name):
            ao_aov = PyNode("aiAOV_AO")
            ao_shader = shadingNode(ao_name, asShader=1)
            ao_sg = sets(name=ao_name + "SG", empty=1, renderable=1, noSurfaceShader=1)
            ao_shader.outColor >> ao_aov.defaultValue
            ao_shader.outColor >> ao_sg.surfaceShader
        return

    def light_group(self):
        lights = ls(type=["light"] + listNodeTypes("light"), dag=True)

        for light in lights:
            light.getParent().rename("_")

        another_name = {
            "aiAreaLight": "area",
            "aiAtmosphereVolume": None,
            "aiBarndoor": None,
            "aiFog": "fog",
            "aiGobo": None,
            "aiLightBlocker": None,
            "aiLightDecay": None,
            "aiMeshLight": "mesh",
            "aiPhotometricLight": "photometric",
            "aiSkyDomeLight": "dome",
            "ambientLight": "ambient",
            "areaLight": "area",
            "directionalLight": "directional",
            "lightGroup": None,
            "lightItem": None,
            "pointLight": "point",
            "spotLight": "spot",
            "volumeLight": "volume",
        }

        for light in lights:
            name = another_name[nodeType(light)]
            if not name:
                name = nodeType(light)
            name += "_01"

            top_node = light.getParent()
            top_node.rename(name)

        for light in lights:
            name = light.getParent() + "_LGT"
            light.getParent().rename(name)
            light.aiAov.set(name)
            if not aov_ui.getAOVNode(name):
                aov_ui.addAOV(name)
        return


class RenderSettings(Common, AOVs):
    def __init__(self, **kwargs):
        super(RenderSettings, self).__init__(**kwargs)

        # ensure default image file rule is set
        workspace.fileRules["images"] = "images"

        self.common_tab()
        self.aovs_tab()

        print ">> Render setup complete.\n",
        return

    def common_tab(self):
        self.file_output()
        self.metadata(version_label=None)  # self.metadata(version_label="ver_001")  # to reuse version
        self.frame_range(start=None, end=None)  # self.frame_range(start=3, end=12)  # re-render certain frames
        self.renderable_cameras(camera="render_cam")  # self.renderable_cameras(camera="other_camera")
        return

    def aovs_tab(self):
        self.maya_render_view()
        self.aov_browser(default_aovs=[])  # self.aov_browser(default_aovs=["volume"])  # add to defaults
        self.light_group()
        return
