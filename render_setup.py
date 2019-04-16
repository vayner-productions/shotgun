"""
USE
"""

# Common
from . import sg, project
from pymel.core import workspace, PyNode

# AOVs
# from mtoa.core import createOptions



def update():
    render_settings = RenderSettings()
    render_settings.common_tab()
    render_settings.aovs_tab()
    return


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
        if start and end:
            self.drg.startFrame.set(start)
            self.drg.endFrame.set(end)
            return

        # # OPT 1
        # from shotgun import update_timeline as sg
        # reload(sg)
        # start, end = sg.get_frame_range()

        # OPT 2
        sg_frame_range = sg.find_one(
            "Shot",
            filters=[["project", "is", project], ["code", "is", self.shot]],
            fields=["sg_frame_range"]
        )["sg_frame_range"]
        start, end = [int(t) for t in sg_frame_range.split("-")]

        self.drg.startFrame.set(start)
        self.drg.endFrame.set(end)
        return

    def renderable_cameras(self, camera="render_cam"):
        render_cam = PyNode(camera)
        render_cam.renderable.set(1)
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

    def aov_shaders(self):
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

        from mtoa.aovs import AOVInterface
        aov_ui = AOVInterface()

        for aov in default_aovs:
            if not aov_ui.getAOVNode(aov):
                aov_ui.addAOV(aov)
        return


class RenderSettings(Common, AOVs):
    def __init__(self, **kwargs):
        super(RenderSettings).__init__(**kwargs)

        # ensure default image file rule is set
        workspace.fileRules["images"] = "images"
        return

    def common_tab(self):
        return

    def aovs_tab(self):
        return
