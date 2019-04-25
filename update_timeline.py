"""
from shotgun import update_timeline as sg
reload(sg)
sg.update_timeline()

from shotgun import update_timeline as sg
reload(sg)
sg.get_frame_range()
"""


from . import sg, project
from pymel.core.system import workspace
from pymel.core.animation import playbackOptions


def get_frame_range():
    shot_code = workspace.fileRules["scene"].rsplit("/", 1)[1]  # Shot_###

    filters = [
        ["project", "is", project],
        ["code", "is", shot_code]
    ]
    sg_frame_range = sg.find_one("Shot", filters, ["sg_frame_range"])["sg_frame_range"]

    start, end = [int(t) for t in sg_frame_range.split("-")]
    return start, end


def update_timeline(start=None, end=None):
    if not all([start, end]):
        start, end = get_frame_range()
    playbackOptions(ast=start, aet=end)
    print ">> Animation timeline changed.\n",
    return
