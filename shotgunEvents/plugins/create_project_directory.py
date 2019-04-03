import os
import shutil
import shotgun_api3


def registerCallbacks(reg):
    """
    Register all necessary or appropriate callbacks for this plugin.
    """
    file_object = open(r"//genesisnx/genesisnx/Animation/Shotgun/System/Tools/shotgun/create_project_directory.txt",
                       "r")

    eventFilter = {
        "Shotgun_Project_Change": ["name", "sg_client", "sg_brand"],
        "Shotgun_Asset_Change": ["code"],
        "Shotgun_Shot_Change": ["code"]
    }
    server = "https://vaynerproductions.shotgunstudio.com"
    script_name = os.path.basename(__file__).split(".")[0] + ".py"
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
    # check for event id and project before continuing
    event_id = event.get("id")
    project = event["project"]
    if project is None:
        project = event.get("entity", {})

    if None is [event_id, project]:
        logger.warning("Missing info in event dictionary, skipping.")
        return

    # check for project path by getting the client, brand, and project
    name = {"project": project["name"]}
    for f in ["sg_client", "sg_brand"]:
        key = f.split("_")[1]
        data = sg.find_one("Project", [["id", "is", project["id"]]], [f])
        if None is data:
            logger.info("Missing {}".format(f))
            return
        name[key] = data[f]["name"]

    media_space = sg.find_one(
        "CustomNonProjectEntity28",
        filters=[["sg_projects", "is", project]],
        fields=["sg_unc_path"]
    )
    unc_path = media_space["sg_unc_path"]

    # create project, shot, and asset directory
    event_type = event["event_type"]
    start = r"{}/Animation/Projects/Client/{}/{}/{}".format(
        unc_path,
        name["client"],
        name["brand"],
        name["project"]
    )

    if "Shotgun_Project_Change" == event_type:
        if not os.path.exists(start):
            logger.info(">> created project directory: {}".format(start))
            os.makedirs(start)
            os.rmdir(start)
            template = r"//genesisnx/genesisnx/Animation/Directory Source/New Project/0000_Project"
            shutil.copytree(template, start)
        logger.info(">> created project directory")
    elif "Shotgun_Shot_Change" == event_type:
        # omitting tests, assets, rigs, dynamics
        scene_dir = r"{}/Project Directory/02_Production/04_Maya/scenes".format(start)

        # create shot paths for cameras, layouts, cache, lighting, animation
        new_shot = event["meta"]["new_value"]
        folders = []  # full path to each scene process, including images
        for s in ["Cameras", "Layouts", "Lighting", "Dynamics", "Animation"]:
            for fld in os.listdir(scene_dir):
                if s in fld:
                    new_folder = r"{}/{}/{}".format(scene_dir, fld, new_shot)
                    folders += [new_folder]

        # /sourceimages contains /Assets, /HDRI, and /000_Unsorted -- everything that isn't HDRI goes into Assets,
        # including textures from Shots. I know. Confusing.
        source_images_dir = scene_dir.replace("scenes", "sourceimages/Assets/{}".format(new_shot))

        cache_dir = "{}/06_Cache/08_Animation/{}".format(scene_dir, new_shot)

        folders += [source_images_dir, cache_dir]
        # create folders
        for pth in folders:
            try:
                os.makedirs(pth)
            except:
                pass

        logger.info(">> created shot directory")

        # create and link camera entity to newly created shot
        camera_entity = sg.find_one(
            "Shot",
            [["project", "is", project],
             ["code", "is", new_shot]],
            ["sg_camera"]
        )["sg_camera"]

        if not camera_entity:
            shot_entity = event["entity"]
            data = {
                "project": project,
                "code": shot_entity["name"] + "_Cam",
                "shot_sg_camera_shots": [shot_entity],
            }
            sg.create("Camera", data)
            logger.info(">> created and link camera entity to shot")
    elif "Shotgun_Asset_Change" == event_type:
        # omit tests, dynamics, cameras, layouts, cache, lighting, animation
        sg_asset_type = sg.find_one(
            "Asset",
            [["project", "is", project],
             ["id", "is", event["meta"]["entity_id"]]],
            ["sg_asset_type"]
        )["sg_asset_type"]

        # create asset paths
        scene_dir = r"{}/Project Directory/02_Production/04_Maya/scenes".format(start)
        scene_folder = {
            "CG Model": "01_Assets",
            "CG Rig": "02_Rigs"
        }
        asset = event["meta"]["new_value"]

        asset_folder_path = r"{}/{}/{}".format(scene_dir, scene_folder[sg_asset_type], asset)
        source_images_dir = scene_dir.replace("scenes", "sourceimages/Assets/{}".format(asset))

        # create asset folders assets, rigs
        try:
            os.makedirs(asset_folder_path)
            os.makedirs(source_images_dir)
        except:
            pass
        logger.info(">> created asset directory")
    return
