"""
# CREATE TICKET FROM CODE
from shotgun import ticket
reload(ticket)
ticket.create()

# CREATE TICKET FROM UI
from shotgun import ticket
reload(ticket)
ticket.get_window()
"""
from . import *
from PySide2 import QtCore, QtWidgets, QtUiTools
from pymel.core import workspace, sceneName


def get_window():
    global mw
    try:
        mw.ui.close()
    except:
        pass

    mw = MyWindow()
    mw.ui.show()


def create(title="", type=None, description="", script_editor="", maya_file=""):
    if not maya_file:
        maya_file = sceneName()

    data = {
        "title": title,
        "project": project,  # from __init__
        "sg_ticket_type": type,
        "description": description,
        "sg_script_editor_dialogue": script_editor,
        "sg_maya_file": maya_file
    }
    ticket = sg.create("Ticket", data)
    print ">> Created ticket #{0}\nhttps://vaynerproductions.shotgunstudio.com/page/10070#Ticket_{0}".format(
        ticket["id"]
    ),
    return ticket


class MyWindow(QtWidgets.QDialog):
    def __init__(self):
        self.ui = self.import_ui()
        self.init_ui()

    def import_ui(self):
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    def create_ticket(self):
        title = self.ui.title_lne.text()
        type = self.ui.type_cbx.currentText()
        description = self.ui.description_txt.toPlainText()
        script_editor = self.ui.script_txt.toPlainText()

        self.ui.close()
        create(title=title, type=type, description=description, script_editor=script_editor)
        return

    def init_ui(self):
        self.ui.attach_btn.deleteLater()
        self.ui.submit_btn.clicked.connect(self.create_ticket)
        return
