import json
from . import checkout_scene
from pymel.util import path
from sgtk.authentication import ShotgunAuthenticator
import collections


class Update(object):
    def __init__(self):
        reload(checkout_scene)
        set_project = checkout_scene.SetProject()
        self.ui_preferences = path(set_project.project_path).joinpath("scripts", "ui_preferences.json").normpath()

        auth = ShotgunAuthenticator()
        self.user = str(auth.get_user())
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

    def json_file(self, dictionary=None):
        data = None
        try:  # reads file
            with self.ui_preferences.open(mode="r") as read_file:
                data = json.load(read_file)

            data[self.user]  # checks for new self.user
            self.dict_merge(data[self.user], dictionary)
        except (IOError, ValueError):  # file is empty or does not exist, creates file
            data = dict({self.user: dictionary})

            with self.ui_preferences.open(mode="a") as new_file:
                json.dump(data, new_file, indent=4, separators=(',', ': '))

            return
        except KeyError:  # new self.user, add to file
            data[self.user] = dictionary

        with self.ui_preferences.open(mode="w") as write_file:
            json.dump(data, write_file, indent=4, separators=(',', ': '))
        # print ">> Recorded Vayner Menu preferences for user.\n",
        return

    def ui(self, branch=None):
        data = None
        try:  # reads file
            with self.ui_preferences.open(mode="r") as read_file:
                data = json.load(read_file)

            data[self.user]  # checks for new self.user
        except:
            pass
            return

        branch_data = data[self.user]
        for key in branch.split("."):
            branch_data = branch_data[key]
        print ">> Loaded Vayner Menu preferences for user.\n",
        return branch_data
