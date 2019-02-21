from . import sg, project
from pymel.core.system import Workspace, warning
from pymel.core.animation import playbackOptions
import pymel.util.path as path


def update_timeline(frame_range=None):
    try:
        workspace = Workspace()
        shot_code = path(workspace.fileRules["scene"]).basename()  # Shot_###

        filter = [
            ["project", "is", project],
            ["code", "is", shot_code]
        ]
        frame_range = sg.find_one("Shot", filter, ["sg_frame_range"])["sg_frame_range"]

        start, end = [int(t) for t in frame_range.split("-")]
        playbackOptions(min=start, max=end)
    except:
        warning("Update timeline failed, set project to shot.")
        pass
    print ">> updated timeline: {}".format(frame_range),
    return
