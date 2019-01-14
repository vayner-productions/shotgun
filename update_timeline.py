from shotgun import checkout_scene
import pymel.core as pm
import sgtk.platform
engine = sgtk.platform.current_engine()


def update_timeline():
    if "Shot" in pm.workspace.fileRules["scene"]:
        sg = engine.shotgun
        project = sg.find_one("Project", [["name", "is", engine.context.project["name"]]])
        entity = checkout_scene.get_entity(pm.workspace.fileRules["scene"])
        frame_range = sg.find_one("Shot",
                                  [["project", "is", project], ["id", "is", entity["id"]]],
                                  ["sg_frame_range"]
                                  )["sg_frame_range"]

        start, end = [int(t) for t in frame_range.split("-")]
        pm.playbackOptions(min=start, max=end)
        print ">> updated timeline: {}".format(frame_range),
    else:
        pm.warning(">> for Shots only")
    return
