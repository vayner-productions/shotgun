import pymel.core as pm

# Name of the global variable for the Maya window
main_maya_window = pm.language.melGlobals['gMainWindow']

# Build a menu and parent underthe Maya Window
vayner_menu = pm.menu('Vayner', parent=main_maya_window)

# Build a menu item and parent under the 'Vayner' menu
# set project - updates workspace and scenes directory
set_project = """
import shotgun.set_project as sg

reload(sg)
sg.get_window()
"""
set_project_item = pm.menuItem(label="Set Project",
                               command=set_project,
                               parent=vayner_menu)


# check out scene - open the latest published scene
checkout_scene = """
import shotgun.checkout_scene as sg

reload(sg)
sg.checkout_scene()
"""
checkout_scene_item = pm.menuItem(label="Checkout Scene",
                                  command=checkout_scene,
                                  parent=vayner_menu)


# publish scene - increment and save this file and update shotgun fields
publish_scene = """
import shotgun.publish_scene as sg

reload(sg)
sg.get_window()
"""
publish_scene_item = pm.menuItem(label="Publish Scene",
                                 command=publish_scene,
                                 parent=vayner_menu)

