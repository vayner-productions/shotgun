import pymel.core as pm

# Name of the global variable for the Maya window
main_maya_window = pm.language.melGlobals['gMainWindow']

# Build a menu and parent underthe Maya Window
vayner_menu = pm.menu('Vayner', parent=main_maya_window, tearOff=1)

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

# update timeline - timeline reflects sg_frame_range
update_timeline = """
import shotgun.update_timeline as sg

reload(sg)
sg.update_timeline()
"""
update_timeline_item = pm.menuItem(label="Update Timeline",
                                 command=update_timeline,
                                 parent=vayner_menu)

# publish scene - increment and save this file and update shotgun fields
organize_textures = """
import shotgun.organize_textures as sg

reload(sg)
sg.organize_textures()
"""
organize_textures_item = pm.menuItem(label="Organize Textures",
                                 command=organize_textures,
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

# add divider for artist specific scripts
pm.menuItem(divider=1, dividerLabel="Lighting")

# render setup - for lighters to prep there render globals
render_setup = """
from shotgun import render_setup as sg
reload(sg)
sg.get_window()
"""
render_setup_item = pm.menuItem(label="Render Setup",
                                command=render_setup,
                                parent=vayner_menu)

"""
# delete Vayner menu
import pymel.core as pm
main_maya_window = pm.language.melGlobals['gMainWindow']
if pm.menu('Vayner', q=1, exists=1):
    pm.deleteUI('Vayner')
"""

"""
# load menu from script editor
import pymel.core as pm
from shotgun import vayner_menu as sg
reload(sg)
"""
