from pymel.core.uitypes import Menu, MenuItem

set_project = """
import shotgun.set_project as sg; reload(sg)
sg.get_window()
"""

checkout = """
from shotgun import checkout_scene as sg; reload(sg)
sg.get_window()
"""

increment_and_save = """
import shotgun.checkout_scene as sg; reload(sg)
checkout = sg.Checkout()
checkout.increment_file()
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
from shotgun import render_setup as sg; reload(sg)
sg.RenderSettings()
"""

import_camera = """
from shotgun.publish import camera as sg; reload(sg)
sg.get_window("load_camera")
"""

publish_camera = """
from shotgun.publish import camera as sg; reload(sg)
sg.get_window("publish_camera")
"""

manage_proxies = """
from shotgun.VaynerMenu import manage_proxies as sg; reload(sg)
sg.get_window()
"""

publish_animation = """
from shotgun.publish import animation as sg; reload(sg)
sg.get_window()
"""

create_ticket = """
from shotgun import ticket; reload(ticket)
ticket.get_window()
"""

reload_menu = """
from shotgun.VaynerMenu import vayner_menu as sg
reload(sg)
vm = sg.VaynerMenu()
vm.run()
"""


class VaynerMenu:
    def __init__(self):
        self.vayner_menu = None
        try:
            self.vayner_menu = Menu("Vayner")
            for item in self.vayner_menu.getItemArray()[::-1]:
                item.delete()
        except ValueError:
            self.vayner_menu = Menu("Vayner", parent="MayaWindow", tearOff=1)

        reload_menu_item = MenuItem(
            label="Reload Vayner Menu",
            command=reload_menu,
            parent="Vayner"
        )
        return

    def add_lighting_items(self):
        organize_textures_item = MenuItem(
            label="Organize Textures",
            command=organize_textures,
        )

        render_setup_item = MenuItem(
            label="Render Setup",
            command=render_setup,
        )

        publish_lighting_item = MenuItem(
            label="Publish Lighting",
            command=publish_scene,
        )
        return

    def add_animation_items(self):
        manage_proxies_item = MenuItem(
            label="Manage Proxies",
            command=manage_proxies,
        )

        update_timeline_item = MenuItem(
            label="Update Timeline",
            command=update_timeline,
        )

        publish_animation_item = MenuItem(
            label="Publish Animation",
            command=publish_animation,
        )
        return

    def add_camera_items(self):
        import_camera_item = MenuItem(
            label="Import Camera",
            command=import_camera
        )

        publish_camera_item = MenuItem(
            label="Publish Camera",
            command=publish_camera,
        )
        return

    def add_rigging_items(self):
        publish_rig_item = MenuItem(
            label="Publish Rig",
            command=publish_scene
        )
        return

    def add_modeling_items(self):
        publish_modeling_item = MenuItem(
            label="Publish Model",
            command=publish_scene
        )
        return

    def run(self):
        ticket_menu_item = MenuItem(
            label="Create Shotgun Ticket",
            command=create_ticket,
            parent="Vayner",
            insertAfter=""
        )

        lighting_menu = MenuItem(
            label="Lighting",
            subMenu=True,
            parent="Vayner",
            insertAfter=""
        )

        self.add_lighting_items()

        animation_item = MenuItem(
            label="Animation",
            subMenu=True,
            parent="Vayner",
            insertAfter=""
        )

        self.add_animation_items()

        camera_item = MenuItem(
            label="Camera",
            subMenu=True,
            parent="Vayner",
            insertAfter=""
        )

        self.add_camera_items()

        rigging_item = MenuItem(
            label="Rigging",
            subMenu=True,
            parent="Vayner",
            insertAfter=""
        )

        self.add_rigging_items()

        modeling_item = MenuItem(
            label="Modeling",
            subMenu=True,
            parent="Vayner",
            insertAfter=""
        )

        self.add_modeling_items()

        build_scene_item = MenuItem(
            label="Build Scene",
            command=build_scene,
            parent="Vayner",
            insertAfter=""
        )

        increment_and_save_item = MenuItem(
            label="Increment And Save",
            command=increment_and_save,
            parent="Vayner",
            insertAfter=""
        )

        checkout_item = MenuItem(
            "checkout_item",
            label="Checkout Scene",
            command=checkout,
            parent="Vayner",
            insertAfter=""
        )

        # removes pyc files
        from pymel.util.common import path
        shotgun = path(r"A:\Animation\Shotgun\System\Tools\shotgun")

        for pyc in shotgun.files("*.pyc"):
            pyc.remove_p()
        print ">> Vayner Menu reloaded\n",
        return
