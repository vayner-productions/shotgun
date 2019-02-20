from pymel.core.uitypes import Menu, MenuItem

set_project = """
import shotgun.set_project as sg; reload(sg)
sg.get_window()
"""

checkout_published_version = """
import shotgun.checkout_scene as sg; reload(sg)
checkout = sg.Checkout()
checkout.run(checkout_type="published")
"""

checkout_working_version = """
import shotgun.checkout_scene as sg; reload(sg)
checkout = sg.Checkout()
checkout.run(checkout_type="processed")
"""

increment_and_save = """
import shotgun.checkout_scene as sg; reload(sg)
checkout = sg.Checkout()
checkout.run(checkout_type="increment")
"""

build_scene = """
import shotgun.build_scene as sg; reload(sg)
sg.get_window()
"""

update_timeline = """
import shotgun.update_timeline as sg; reload(sg)
sg.update_timeline()
"""

organize_textures = """
import shotgun.organize_textures as sg; reload(sg)
sg.organize_textures()
"""

publish_scene = """
import shotgun.publish_scene as sg; reload(sg)
sg.get_window()
"""

render_setup = """
import shotgun.render_setup as sg; reload(sg)
sg.get_window()
"""

publish_camera = """
import shotgun.initialize_camera as sg; reload(sg)
sg.get_window()
"""

class VaynerMenu:
    def __init__(self):
        self.vayner_menu = None
        try:
            self.vayner_menu = Menu("Vayner")
        except ValueError:
            self.vayner_menu = Menu("Vayner", parent="MayaWindow", tearOff=1)
        return

    def run(self):
        self.vayner_menu.deleteAllItems()

        # updates project directory
        set_project_item = MenuItem(
            label="Set Project",
            command=set_project,
            parent="Vayner"
        )

        # creates a working file from latest publish
        checkout_published_version_item = MenuItem(
            label="Checkout Published Version",
            command=checkout_published_version,
            parent="Vayner"
        )

        # open latest working file
        checkout_working_version_item = MenuItem(
            label="Checkout Working Version",
            command=checkout_working_version,
            parent="Vayner"
        )

        # increment and save current working file
        increment_and_save_item = MenuItem(
            label="Increment And Save",
            command=increment_and_save,
            parent="Vayner"
        )

        # references all available assets designated to shot
        build_scene_item = MenuItem(
            label="Build Scene",
            command=build_scene,
            parent="Vayner"
        )

        # registers current maya file and related files to shotgun site
        publish_scene_item = MenuItem(
            label="Publish Scene",
            command=publish_scene,
            parent="Vayner"
        )

        # CAMERA SECTION
        MenuItem(divider=1, dividerLabel="Camera", parent="Vayner")

        # imports and publishes camera
        publish_camera_item = MenuItem(
            label="Import and Publish Camera",
            command=publish_camera,
            parent="Vayner"
        )

        # ANIMATION SECTION
        MenuItem(divider=1, dividerLabel="Animation", parent="Vayner")

        # matches start/end playback to frame range on shotgun site
        update_timeline_item = MenuItem(
            label="Update Timeline",
            command=update_timeline,
            parent="Vayner"
        )

        # LIGHTING SECTION
        MenuItem(divider=1, dividerLabel="Lighting", parent="Vayner")

        # places textures in /sourceimages under /Assets and /HDRI
        organize_textures_item = MenuItem(
            label="Organize Textures",
            command=organize_textures,
            parent="Vayner"
        )

        # templates lighters' files for render farm
        render_setup_item = MenuItem(
            label="Render Setup",
            command=render_setup,
            parent="Vayner"
        )

        # removes pyc files
        from pymel.util.common import path
        shotgun = path(r"A:\Animation\Shotgun\System\Tools\shotgun")

        for pyc in shotgun.files("*.pyc"):
            pyc.remove_p()
        return
