import json
from . import checkout_scene
from pymel.util import path
from sgtk.authentication import ShotgunAuthenticator

reload(checkout_scene)
set_project = checkout_scene.SetProject()
json_file = path(set_project.project_path).joinpath("scripts", "ui_preferences.json").normpath()

auth = ShotgunAuthenticator()
user = str(auth.get_user())

# data = {
#     user: {
#         "checkout": {
#             "process": "Animation",
#             "entity": "Shot_001",
#             "type": "Working File",
#         },
#         "publish": {
#             "animation": {
#                 "multi": ["Hero_GEO"],
#                 "single": ["Shot_PXY"],
#                 "attributes": [
#                     "World Space",
#                     "Write Visibility",
#                     "Euler Filter",
#                     "UV Write",
#                     "Strip Namespaces",
#                     "Write UV Sets"
#                 ]
#             },
#             "lighting": {
#                 "type": "Next"
#             }
#         }
#     }
# }

script = None

# reads file
try:
    with json_file.open(mode="r") as read_file:
        data = json.load(read_file)
        data[user]  # checks for new user
except (IOError, ValueError):  # file is empty or does not exist, creates file
    data = {user: {}}

    with json_file.open(mode="a") as new_file:
        json.dump(data, new_file, indent=4, separators=(',', ': '))
except KeyError:  # new user, add to file
    pass
    # data.update({
    #     user: {
    #         "process": process,
    #         "entity": entity_name
    #     }
    # })
    # with json_file.open(mode="w") as write_file:
    #     json.dump(data, write_file, indent=4, separators=(',', ': '))
