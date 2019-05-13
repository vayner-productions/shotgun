import json
from . import checkout_scene
from pymel.util import path
from sgtk.authentication import ShotgunAuthenticator
import collections


class Update(object):
    def __init__(self):
        reload(checkout_scene)
        set_project = checkout_scene.SetProject()
        self.json_file = path(set_project.project_path).joinpath("scripts", "ui_preferences.json").normpath()
        return

    def dict_merge(self, dct, merge_dct):
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
                self.dict_merge(dct[k], merge_dct[k])
            else:
                dct[k] = merge_dct[k]

    def json_file(self):
        return


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


def ui(dictionary=None):
    auth = ShotgunAuthenticator()
    user = str(auth.get_user())

    data = None
    try:  # reads file
        with json_file.open(mode="r") as read_file:
            data = json.load(read_file)
            data[user]  # checks for new user
    except:
        # pass
        print ">> Nothing to update.\n",
        return

    dictionary = data[user]  # kat
    for i in items:
        dictionary = dictionary[i]  # kat[checkout]  # kat[publish][lighting]

    value = None
    if not isinstance(dictionary, dict):
        value = dictionary
        dictionary = None

    for k in nested_dictionary.keys():
        dictionary[k]

    print ">> User preferences applied.\n",
    return
