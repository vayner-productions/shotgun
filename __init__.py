"""
Common variables used in all shotgun tools.
"""
from sgtk import platform
engine = platform.current_engine()
sg = engine.shotgun
project = sg.find_one(
    "Project",
    [["name", "is", engine.context.project["name"]]]
)
media_space = sg.find_one(
    "CustomNonProjectEntity28",
    filters=[["sg_projects", "is", project]],
    fields=["sg_mapped_letter"]
)["sg_mapped_letter"]


root = None  # the drive you're working on i.e. Mac/../04_Maya


__all__ = ["root", "sg", "project", "media_space"]

