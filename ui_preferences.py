import json
from . import checkout_scene
from pymel.util import path
from sgtk.authentication import ShotgunAuthenticator

reload(checkout_scene)
set_project = checkout_scene.SetProject()
json_file = path(set_project.project_path).joinpath("scripts", "ui_preferences.json").normpath()

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
#             "lighting": "next"
#         }
#     }
# }

import collections


def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.iteritems():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def update(dictionary=None):
    auth = ShotgunAuthenticator()
    user = str(auth.get_user())

    data = None
    try:  # reads file
        with json_file.open(mode="r") as read_file:
            data = json.load(read_file)
            data[user]  # checks for new user

        dict_merge(data[user], dictionary)
    except (IOError, ValueError):  # file is empty or does not exist, creates file
        data = dict({user: dictionary})

        with json_file.open(mode="a") as new_file:
            json.dump(data, new_file, indent=4, separators=(',', ': '))

        return
    except KeyError:  # new user, add to file
        data[user] = dictionary

    with json_file.open(mode="w") as write_file:
        json.dump(data, write_file, indent=4, separators=(',', ': '))

    print ">> Recorded Vayner Menu preferences for user.\n",
    return
