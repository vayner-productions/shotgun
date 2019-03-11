from pymel.core.uitypes import Menu, MenuItem

save_warning = """
from shotgun.VaynerMenu import qt_checkout_box as sg; reload(sg)
sg.save_startup_warnings()
"""

set_project = """
import shotgun.set_project as sg; reload(sg)
sg.get_window()
"""

checkout_menu = """
from shotgun.VaynerMenu import qt_checkout_box as sg; reload(sg)
sg.get_window()
"""

checkout_saved_version = """
from shotgun.VaynerMenu import qt_checkout_box as sg; reload(sg)
sg.checkout_saved_option()
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

import_camera = """
from shotgun.publish import camera as sg; reload(sg)
sg.get_window("load_camera")
"""

publish_camera = """
from shotgun.publish import camera as sg; reload(sg)
sg.get_window("publish_camera")
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

        # adds checkbox for startup warning
        startup_warning_item = MenuItem(
            "startup_warning_item",
            label="Turn Off Startup Warnings",
            checkBox=True,
            command=save_warning,
            parent="Vayner"
        )

        # updates project directory
        set_project_item = MenuItem(
            label="Set Project",
            command=set_project,
            parent="Vayner"
        )

        # checkout either the published or working file
        checkout_item = MenuItem(
            "checkout_item",
            label="Checkout",
            command=checkout_saved_version,
            parent="Vayner"
        )
        # creates option box for the checkout menu item
        checkout_box_item = MenuItem(
            optionBox=True,
            command=checkout_menu,
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

        # CAMERA SUBMENU
        camera_item = MenuItem(
            label="Camera",
            subMenu=True,
            parent="Vayner"
        )

        # imports camera
        import_camera_item = MenuItem(
            label="Import Camera",
            command=import_camera
        )

        # publishes camera
        publish_camera_item = MenuItem(
            label="Publish Camera",
            command=publish_camera,
        )

        # ANIMATION SUBMENU
        animation_item = MenuItem(
            label="Animation",
            subMenu=True,
            parent="Vayner"
        )

        # matches start/end playback to frame range on shotgun site
        update_timeline_item = MenuItem(
            label="Update Timeline",
            command=update_timeline,
        )

        # LIGHTING SUBMENU
        lighting_item = MenuItem(
            label="Lighting",
            subMenu=True,
            parent="Vayner"
        )

        # places textures in /sourceimages under /Assets and /HDRI
        organize_textures_item = MenuItem(
            label="Organize Textures",
            command=organize_textures,
        )

        # templates lighters' files for render farm
        render_setup_item = MenuItem(
            label="Render Setup",
            command=render_setup,
        )

        # removes pyc files
        from pymel.util.common import path
        shotgun = path(r"A:\Animation\Shotgun\System\Tools\shotgun")

        for pyc in shotgun.files("*.pyc"):
            pyc.remove_p()

        print ">> Vayner Menu reloaded",
        return
