from . import *
import pymel.core as pm
import pymel.util.common as ut
from PySide2 import QtCore, QtWidgets, QtUiTools
import os

from . import checkout_scene
reload(checkout_scene)
checkout = checkout_scene.Checkout()

scene_process, entity_name = pm.workspace.fileRules["scene"].split("/")[1:]
entity_type = "Asset"
if "Lighting" in scene_process:
    entity = sg.find_one(
        "Shot",
        [["project", "is", project], ["code", "is", entity_name]],
    )
elif "Asset" in scene_process:
    entity = sg.find_one(
        "Shot",
        [["project", "is", project], ["code", "is", entity_name], ["sg_asset_type", "is", "CG_Model"]],
    )
elif "Rig" in scene_process:
    entity = sg.find_one(
        "Shot",
        [["project", "is", project], ["code", "is", entity_name], ["sg_asset_type", "is", "CG_Rig"]],
    )


def create_thumbnail(file_name=None):
    current_time = pm.currentTime(q=1)
    if not file_name:
        file_name = pm.sceneName().replace(".ma", ".jpg").replace("scenes", "published").replace("processed", "original")
    media_file = pm.playblast(
        frame=current_time,
        format="image",
        completeFilename=file_name,
        percent=100,
        compression="jpg",
        quality=100,
        widthHeight=(960, 540),
        viewer=0,
        forceOverwrite=1,
        clearCache=1,
        offScreen=1
    )
    return media_file


def get_alembic_file(file_path):
    # parent everything in the outliner for alembic top node selection export
    top_node, name = None, pm.workspace.fileRules["scene"].rsplit("/", 1)[1] + "_ANIM"
    if pm.objExists(name):
        top_node = pm.PyNode(name)
    else:
        prefix, maya_name = name.split("_", 1)
        if prefix.isdigit():
            top_node = pm.group(em=1, n=maya_name)
        else:
            top_node = pm.group(em=1, n=name)

    default_cameras = set([pm.PyNode(cam) for cam in ["persp", "top", "front", "side"]])
    outliner = list(set(pm.ls(assemblies=1)).difference(default_cameras).difference(set([top_node])))

    if outliner:
        pm.parent(outliner, top_node)
    pm.select(clear=1)

    alembic_file = "{}/{}/{}.abc".format(
        pm.workspace.getPath(),
        pm.workspace.fileRules["Alembic"],
        ut.path.basename(pm.sceneName()).stripext().replace(".", "_").replace("processed", "original")
    )
    alembic_dir = os.path.dirname(alembic_file)
    if not os.path.exists(alembic_dir):
        os.makedirs(alembic_dir)

    mel_code = """
    AbcExport -j "-frameRange {0:.0f} {1:.0f} -stripNamespaces -uvWrite -worldSpace -writeVisibility -eulerFilter -writeUVSets -dataFormat ogawa -root |{2} -file \\"{3}\\"";
    """.format(
        pm.playbackOptions(q=1, ast=1),
        pm.playbackOptions(q=1, aet=1),
        top_node,
        alembic_file)
    pm.mel.eval(mel_code)
    return alembic_file


def get_tasks():
    scene_process = pm.workspace.fileRules["scene"].split("/")[1][3:]
    step = {
        "Assets": "Model",
        "Cameras": "Cameras",
        "Rigs": "Rig",
        "Layouts": "Layout",
        "Dynamics": "Effects",
        "Lighting": "Lighting",
        "Animation": "Animation"
    }
    task_filters = [
        ["project", "is", project],
        ["entity", "is", entity],
        ["sg_status_list", "is_not", "cmp"],
        ["sg_status_list", "is_not", "rev"],
        ["sg_status_list", "is_not", "omt"],
        ["step.Step.code", "is", step[scene_process]]
    ]
    task_fields = [
        "content"
    ]
    tasks = sg.find("Task", task_filters, task_fields)
    return tasks


def check_top_node(top_node=None, suffix=""):
    scene = pm.sceneName()
    if "07_Lighting" in scene:
        return True

    if suffix:
        if "_" not in suffix:
            suffix = "_" + suffix
    else:
        if "01_Assets" in scene:
            suffix = "_GRP"
        elif "02_Rigs" in scene:
            suffix = "_RIG"

    name = "{}{}".format(scene.basename().split("_processed.")[0], suffix)
    incomplete = 0
    prefix, maya_name = name.split("_", 1)
    try:
        if prefix.isdigit():
            top_node = pm.PyNode(maya_name)
        else:
            top_node = pm.PyNode(name)

        children = pm.ls(assemblies=1)
        for view in ["persp", "top", "front", "side", top_node]:
            if view in children:
                children.remove(view)

        if children:
            incomplete = 1
    except:
        if prefix.isdigit():
            top_node = pm.group(em=1, n=maya_name)
        else:
            top_node = pm.group(em=1, n=name)
        incomplete = 1

    if incomplete:
        pm.warning(">> Publish failed, there are objects outside the top node.")
        return False

    sg_name = scene.dirname().basename()
    attr_exists = pm.attributeQuery("sg_name", node=top_node, ex=1)

    # although it makes sense to append shotgun name only once, it is done every time to ensure any name changes in
    # shotgun are accounted for
    if attr_exists:
        top_node.sg_name.unlock()
    else:
        pm.addAttr(top_node, ln="sg_name", nn="Shotgun Name", dt="string")
    top_node.sg_name.set(sg_name)
    top_node.sg_name.lock()

    for at in "trs":
        for ax in "xyz":
            top_node.setAttr(at+ax, k=0, l=1)
    top_node.setAttr("v", k=0, l=1)
    return top_node


def check_cameras():
    if "01_Assets" not in pm.workspace.fileRules["scene"]:
        return

    extra_cameras = [str(cam.getParent()) for cam in pm.ls(ca=1)]
    for view in ["persp", "top", "front", "back", "side", "right", "left", "bottom"]:
        if view in extra_cameras:
            extra_cameras.remove(view)
    if extra_cameras:
        pm.warning("Remove extra cameras: {}".format(", ".join(extra_cameras)))
        return False
    return


def error():
    if check_cameras() == False:
        print check_cameras()
        return True
    if check_top_node() == False:
        return True
    return False


def publish_scene(addressed_tasks=[], comments=None):
    #
    # increments for the last maya ascii on sg
    #

    # THE NUMBERING ON THE ORIGINAL IS COMING FROM THE ORIGINAL FILE -- WRONG
    processed_file = checkout.increment_file(open_file=1)
    checkout_file = pm.sceneName()
    original_directory = ut.path(checkout_file.dirname().replace("scenes", "published"))
    original_directory.makedirs_p()

    search_pattern = checkout_file.namebase.replace("processed", "original").split(".")[0] + ".*.ma"
    original_files = sorted(original_directory.files(search_pattern))[::-1]
    original_file = None
    if original_files:
        original_file = original_files[0].normpath().split(".")
        original_file[1] = str(int(original_file[1]) + 1).zfill(4)
        original_file = ut.path(".".join(original_file)).normpath()
    else:
        original_file = original_directory.joinpath(search_pattern.replace("*", "0001")).normpath()

    ut.path.copy2(ut.path(processed_file), ut.path(original_file))
    #
    # prepare for shotgun updates
    #
    scene_process = pm.workspace.fileRules["scene"].rsplit("/", 2)[1][3:]
    data, local_path = {}, original_file.replace("/", "\\")

    if scene_process == "Assets" or scene_process == "Rigs":
        # TODO: TRACK VERSIONS!!!!
        data = {
            "sg_file": {
                "link_type": "local",
                "local_path": local_path
            }
        }
    elif scene_process == "Lighting":
        render_root = pm.workspace.expandName(pm.workspace.fileRules["images"])
        filename = pm.rendering.renderSettings(firstImageName=1)[0]
        output_path = ut.path("/".join([render_root, filename])).dirname().dirname().normpath()

        data = {
            "sg_maya_light": {
                "link_type": "local",
                "local_path": local_path
            },
            "sg_maya_render": {
                "link_type": "local",
                "local_path": r"{}".format(output_path)
            }
        }
    data.update({
        "sg_status_list": "cmpt"
    })

    sg.update(entity["type"], entity["id"], data)

    #
    # update sg on the tasks user addressed
    #
    if addressed_tasks:
        for task_name in addressed_tasks:
            task_filters = [
                ["project", "is", project],
                ["entity", "is", entity],
                ["content", "is", task_name]
            ]
            task_data = {
                "sg_status_list": "cmp"
            }
            task = sg.find_one("Task", task_filters)
            sg.update("Task", task["id"], task_data)

    #
    # update entity with a image/video link
    #
    version_name = str(original_file.parent.basename() + "_v001")

    # sg.find(
    #     "version",
    #     fields=[["project", "is", project], ["code", "contains", ]]
    # )

    version_data = {
        "project": project,
        "entity": entity,
        "code": version_name,
        "description": comments
    }
    version = sg.create("Version", version_data)
    if scene_process != "Lighting":
        media_file = create_thumbnail(file_name=original_file.replace(".ma", ".jpg"))
        sg.upload("Version", version["id"], media_file, field_name="sg_uploaded_movie")
    print ">> published all files to shotgun",
    return


def get_window():
    if error():
        return

    global mw
    try:
        mw.ui.close()
    except:
        pass

    mw = MyWindow()
    mw.ui.show()


class MyWindow(QtWidgets.QDialog):
    def __init__(self):
        self.ui = self.import_ui()
        self.tasks = get_tasks()
        self.init_ui()
        self.setup_ui()

    def import_ui(self):
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    def init_ui(self):
        for t in self.tasks:
            self.ui.task_lsw.addItem(t["content"])
        return

    def setup_ui(self):
        self.ui.publish_btn.clicked.connect(self.run)
        return

    def run(self):
        selection = [sel.text() for sel in self.ui.task_lsw.selectedItems()]
        text = self.ui.description_txt.toPlainText()
        publish_scene(addressed_tasks=selection, comments=text)
        self.ui.close()
        pass


