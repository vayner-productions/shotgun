from pymel.util import path
import shotgun_api3


def registerCallbacks(reg):
    """
    Register all necessary or appropriate callbacks for this plugin.
    """
    file_object = open(r"//genesisnx/genesisnx/Animation/Shotgun/System/Tools/shotgun/create_project_directory.txt")

    eventFilter = {
        "Shotgun_Project_Change": ["name", "sg_client", "sg_brand"],
        "Shotgun_Asset_Change": ["code"],
        "Shotgun_Shot_Change": ["code"]
    }
    server = "https://vaynerproductions.shotgunstudio.com"
    script_name = path(__file__).basename()
    script_key = file_object.readline()

    file_object.close()

    sg = shotgun_api3.Shotgun(server, script_name, script_key)

    reg.registerCallback(
        script_name,
        script_key,
        create_project_directory,
        eventFilter,
        None,
    )
    reg.logger.debug("Registered callback.")


def create_project_directory(sg, logger, event, args):
    if "Shotgun_Project_Change" == event["event_type"]:
        logger.info(">> PROJECT CHANGED")
    elif "Shotgun_Shot_Change" == event["event_type"]:
        logger.info(">> SHOT CHANGED")
    elif "Shotgun_Asset_Change" == event["event_type"]:
        logger.info(">> ASSET CHANGED")
    logger.info(event)
    return
