"""
from shotgun import render_setup
reload(render_setup)
render_setup.update()
"""


def update():
    render_settings = RenderSettings()
    render_settings.common_tab()
    render_settings.aovs_tab()
    return


class RenderSettings(object):
    def __init__(self):
        return

    def common_tab(self):
        return

    def aovs_tab(self):
        return
