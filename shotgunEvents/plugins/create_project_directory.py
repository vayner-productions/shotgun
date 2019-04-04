from os import path, makedirs
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
    if "Shotgun_Project_Change" == event["event_type"]:
        create = CreateDirectory(sg, logger, event)
        create.project()
    elif "Shotgun_Shot_Change" == event["event_type"]:
        create = CreateDirectory(sg, logger, event)
        create.shot()
    elif "Shotgun_Asset_Change" == event["event_type"]:
        create = CreateDirectory(sg, logger, event)
        create.asset()
    # logger.info(event)
    return


class CreateDirectory(object):
    def __init__(self, sg, logger, event):
        self.sg = sg
        self.logger = logger
        self.event = event

        project = event["entity"]  # assumes project change
        if event["event_type"] != "Shotgun_Project_Change":
            project = event["project"]

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
            shutil.copytree(template, self.project_directory)
            mkdir(a_drive)
        except:
            pass
        return

    def shot(self):
        folders = [
            "scenes/03_Cameras",
            # "scenes/04_Layouts",  # not used
            "scenes/05_Dynamics",
            "scenes/06_Cache/08_Animation",  # 06_Cache/08_Animation/Shot_### or 06_Cache/05_Dynamics/Shot_###
            "scenes/07_Lighting",
            "scenes/08_Animation",
            "sourceimages/Assets",  # everything that isn't HDRI goes into Assets, including textures for shots
        ]

        shot_name = self.event["entity"]["name"]
        for folder in folders:
            directory = path.normpath(path.join(
                self.project_directory,
                "Project Directory/02_Production/04_Maya",
                folder,
                shot_name
            ))
            try:
                makedirs(directory)
            except:
                pass
            self.logger.info(">> {}".format(directory))
        return

    def asset(self):
        # create asset folder
        # create source images folder
        self.logger.info(">> ASSET CHANGED")
        return

