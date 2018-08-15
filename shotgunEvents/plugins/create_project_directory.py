"""
develop this via the command prompt
add the following line to the command prompt:
C:\Python27\python.exe "A:\Animation\Shotgun\System\Tools\shotgun\shotgunEvents\src\shotgunEventDaemon.py" foreground
C:\Python27\python.exe "A:\Animation\Shotgun\System\Tools\shotgun\shotgunEvents\src\shotgunEventDaemon.py" start
C:\Python27\python.exe "A:\Animation\Shotgun\System\Tools\shotgun\shotgunEvents\src\shotgunEventDaemon.py" stop
C:\Python27\python.exe "A:\Animation\Shotgun\System\Tools\shotgun\shotgunEvents\src\shotgunEventDaemon.py" install
C:\Python27\python.exe "A:\Animation\Shotgun\System\Tools\shotgun\shotgunEvents\src\shotgunEventDaemon.py" remove
python "A:\Animation\Shotgun\System\Tools\shotgun\shotgunEvents\src\shotgunEventDaemon.py" debug
"""
import os
import shutil
import shotgun_api3


def registerCallbacks(reg):
    """
    Register all necessary or appropriate callbacks for this plugin.
    """
    file_object = open(r"//192.168.255.200/GenesisNX/Animation/Shotgun/System/Tools/shotgun/create_project_directory.txt",
                       "r")

    eventFilter = {
        "Shotgun_Project_Change": ["name", "sg_client", "sg_brand"]
    }
    server = "https://vaynerproductions.shotgunstudio.com"  #os.environ["SG_SITE"]
    script_name = os.path.basename(__file__).split(".")[0] + ".py"  # os.environ["SG_CREATE_PROJECT_DIRECTORY_NAME"]
    script_key = file_object.readline()  # "ryaaewst4-qcseneqyuPrazmi"  # os.environ["SG_CREATE_PROJECT_DIRECTORY_KEY"]

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
    event_id = event.get("id")
    project = event.get("entity", {})

    if None is [event_id, project]:
        logger.warning("Missing info in event dictionary, skipping.")
        return

    name = {"project": project["name"]}
    for f in ["sg_client", "sg_brand"]:
        key = f.split("_")[1]
        data = sg.find_one("Project", [["id", "is", project["id"]]], [f])
        if None is data:
            logger.info("Missing {}".format(f))
            return
        name[key] = data[f]["name"]

    start = r"//192.168.255.200/GenesisNX/Animation/Projects/Client/{}/{}/{}".format(
        name["client"],
        name["brand"],
        name["project"]
    )

    if not os.path.exists(start):
        logger.info(">> created project directory: {}".format(start))
        os.makedirs(start)
        os.rmdir(start)
        template = r"//192.168.255.200/GenesisNX/Animation/Directory Source/New Project/0000_Project"
        shutil.copytree(template, start)
    return
