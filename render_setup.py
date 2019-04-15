"""
from shotgun import render_setup
reload(render_setup)
render_setup.update()
"""


from pymel.core import Workspace

workspace = Workspace()


def update():
    render_settings = RenderSettings()
    render_settings.common_tab()
    render_settings.aovs_tab()
    return


class Common(object):
    def __init__(self):
        return


class AOVs(object):
    def __init__(self):
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
