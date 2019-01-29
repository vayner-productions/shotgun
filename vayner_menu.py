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


# check out latest working version given project settings
checkout_working_version = """
import shotgun.checkout_scene as sg

reload(sg)
checkout = sg.Checkout()
checkout.run(checkout_type="processed")
"""
checkout_working_version_item = pm.menuItem(label="Checkout Working Version",
                                  command=checkout_working_version,
                                  parent=vayner_menu)


# checkout published scene as working version with naming convention based on set project
checkout_published = """
import shotgun.checkout_scene as sg

reload(sg)
checkout = sg.Checkout()
checkout.run(checkout_type="published")
"""
checkout_published_item = pm.menuItem(label="Checkout Published Version",
                                  command=checkout_published,
                                  parent=vayner_menu)


# increment and save with naming convention based on set project
increment_and_save = """
import shotgun.checkout_scene as sg

reload(sg)
checkout = sg.Checkout()
checkout.run(checkout_type="increment")
"""
increment_and_save_item = pm.menuItem(label="Increment and Save",
                                  command=increment_and_save,
                                  parent=vayner_menu)


# build scene references all available assets assigned to shot
build_scene = """
from shotgun import build_scene as sg

reload(sg)
sg.get_window()
"""
build_scene_item = pm.menuItem(label="Build Scene",
                               command=build_scene,
                               parent=vayner_menu)


# update timeline based on shotgun site's frame range
update_timeline = """
import shotgun.update_timeline as sg

reload(sg)
sg.update_timeline()
"""
update_timeline_item = pm.menuItem(label="Update Timeline",
                                   command=update_timeline,
                                   parent=vayner_menu)

# organize textures -- not sure if anyone's using it
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
