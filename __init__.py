"""
Common variables used in all shotgun tools.
"""
root = None

from sgtk import platform
engine = platform.current_engine()
sg = engine.shotgun
project = sg.find_one("Project", [["name", "is", engine.context.project["name"]]])

__all__ = ["root", "sg", "project"]
