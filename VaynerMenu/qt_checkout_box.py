from PySide2 import QtCore, QtWidgets, QtUiTools
from pymel.core import optionVar
from pymel.core.uitypes import Menu, MenuItem
from pymel.core import optionVar

def get_window():
    global mw
    try:
        mw.ui.close()
    except:
        pass
    mw = MyWindow()
    mw.ui.show()


def startup_warning_change():
    saved_pref = optionVar(q='version_checkout')
    import shotgun.checkout_scene as sg
    reload(sg)
    checkout = sg.Checkout()
    if saved_pref == 'pbox':
        checkout.run(checkout_type="published")
    else:
        checkout.run(checkout_type="processed")


def save_startup_warnings():
    cvalue = optionVar (q ="setup_warnining_display")
    if cvalue == 1:
        optionVar(iv=("setup_warnining_display", 0))
        print ">>> Warnings turned off"
    else:
        optionVar(iv=("setup_warnining_display", 1))
        print ">>> Warnings turned on"



class MyWindow(QtWidgets.QDialog):
    def __init__(self):
        self.ui = self.import_ui()
        self.connect_signals(self.ui)
        return

    def import_ui(self):
        ui_path = __file__.split(".")[0] + ".ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    def connect_signals(self, ui):
        saved_pref = optionVar(q='version_checkout')
        QtWidgets.QAbstractButton.toggle(self.ui.wbox)

        if saved_pref == 'pbox':
            QtWidgets.QAbstractButton.toggle(self.ui.pbox)
        elif saved_pref == 'wbox':
            QtWidgets.QAbstractButton.toggle(self.ui.wbox)

        self.ui.chkt_btn.clicked.connect(self.checkout_button)

    def checkout_button(self):
        import shotgun.checkout_scene as sg;
        reload(sg)
        checkout = sg.Checkout()
        if self.ui.pbox.isChecked():
            new_pref = 'pbox'
            optionVar(sv=('version_checkout', 'pbox'))
            checkout.run(checkout_type="published")
        if self.ui.wbox.isChecked():
            new_pref = 'wbox'
            optionVar(sv=('version_checkout', 'wbox'))
            checkout.run(checkout_type="processed")

        mw.ui.close()
