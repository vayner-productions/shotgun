"""
develop this via the command prompt
add the following line to the command prompt:
C:\Python27\python.exe A:\Animation\Shotgun\System\Tools\shotgun\shotgunEvents\src\shotgunEventDaemon.py foreground
C:\Python27\python.exe A:\Animation\Shotgun\System\Tools\shotgun\shotgunEvents\src\shotgunEventDaemon.py install
"""
import os
import logging
import shutil


def registerCallbacks(reg):
    """
    Register all necessary or appropriate callbacks for this plugin.
    """
    eventFilter = {
        "Shotgun_Project_Change": ["name", "sg_client", "sg_brand"]
    }
    reg.registerCallback(
        os.environ["SG_SITE"],
        os.environ["SG_CREATE_PROJECT_DIRECTORY_NAME"],
        os.environ["SG_CREATE_PROJECT_DIRECTORY_KEY"],
        create_project_directory,
        eventFilter,
        None,
    )
    reg.logger.setLevel(logging.DEBUG)


def create_project_directory(sg, logger, event, args):
    event_id = event.get("id")
    project = event.get("entity", {})

    if None is [event_id, project]:
        logger.warning("Missing info in event dictionary, skipping.")
        return

    name = {"project": project["name"]}
    for f in ["sg_client", "sg_brand"]:
        key = f.split("_")[1]
        data = sg.find_one("Project", [["id", "is", project["id"]]], [f])
        # if None is data:
        #     logger.info("Missing {}".format(f))
        #     return
        name[key] = data[f]["name"]

    start = r"A:/Animation/Projects/Client/{}/{}/{}".format(
        name["client"],
        name["brand"],
        name["project"]
    )

    if not os.path.exists(start):
        os.makedirs(start)
        os.rmdir(start)
        template = r"A:/Animation/Directory Source/New Project/0000_Project"
        shutil.copytree(template, start)
        logger.info(">> create project directory: {}".format(start))
    return
