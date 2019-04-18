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
    fields=["sg_mapped_letter", "sg_unc_path"]
)
mapped_letter = media_space["sg_mapped_letter"]
unc_path = media_space["sg_unc_path"]

root = None  # the drive you're working on i.e. Mac/../04_Maya


__all__ = ["root", "sg", "project", "mapped_letter", "unc_path"]

