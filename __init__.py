"""
Common variables used in all shotgun tools.
"""
from sgtk import platform
engine = platform.current_engine()
sg = engine.shotgun

sg_mapped letter = "sg_media_space.CustomNonProjectEntity28.sg_mapped_letter"
sg_unc_path = "sg_media_space.CustomNonProjectEntity28.sg_unc_path"

project = sg.find_one(
    "Project",
    fields=[["name", "is", engine.context.project["name"]]],
    filters=[sg_mapped_letter, sg_unc_path]
)

mapped_letter = project[sg_mapped_letter]
unc_path = project[sg_unc_path]

root = None  # the drive you're working on i.e. Mac/../04_Maya

__all__ = ["root", "sg", "project", "mapped_letter", "unc_path"]
