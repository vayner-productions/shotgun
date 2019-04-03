from os import path, mkdir
import shutil
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
    script_name = path.basename(__file__).split(".")[0] + ".py"  # no pyc files
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
    create = CreateDirectory(sg, logger, event)
    if "Shotgun_Project_Change" == event["event_type"]:
        create.project()
    elif "Shotgun_Shot_Change" == event["event_type"]:
        create.shot()
    elif "Shotgun_Asset_Change" == event["event_type"]:
        create.asset()
    # logger.info(event)
    return


class CreateDirectory(object):
    def __init__(self, sg, logger, event):
        self.sg = sg
        self.logger = logger
        self.event = event

        # project path is used in all methods
        project = event["entity"]

        unc_path = "sg_media_space.CustomNonProjectEntity28.sg_unc_path"
        client = "sg_client.CustomNonProjectEntity15.code"
        brand = "sg_brand.CustomNonProjectEntity29.code"
        project_name = "name"

        fields = sg.find_one(
            "Project",
            filters=[["id", "is", project["id"]]],
            fields=[client, brand, unc_path, project_name]
        )

        self.project_directory = path.normpath(path.join(
            fields[unc_path],
            "Animation/Projects/Client",
            fields[client],
            fields[brand],
            fields[project_name]
        ))
        return

    def project(self):
        """
        creates project directory from template for production and another project directory on A: for tracking
        :return:
        """
        self.logger.info(">> PROJECT CHANGED")

        template = path.normpath(
            "//genesisnx/genesisnx/Animation/Directory Source/New Project/0000_Project"
        )
        a_drive = path.normpath(path.join(
            "//genesisnx/genesisnx",
            self.project_directory[self.project_directory.index("Animation"):]
        ))

        try:
            mkdir(a_drive, self.project_directory)
            shutil.copytree(template, self.project_directory)
        except:
            pass
        return

    def shot(self):
        self.logger.info(">> SHOT CHANGED")
        return

    def asset(self):
        # create asset folder
        # create source images folder
        self.logger.info(">> ASSET CHANGED")
        return