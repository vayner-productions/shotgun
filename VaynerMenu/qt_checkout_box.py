from PySide2 import QtCore, QtWidgets, QtUiTools


def get_window():
    global mw
    try:
        mw.ui.close()
    except:
        pass
    mw = MyWindow()
    mw.ui.show()


class YouClass:
    def __init__(self):
        return


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
        saved_pref = pm.optionVar(q='version_checkout')
        QAbstractButton.toggle(self.ui.wbox)


        if saved_pref == 'pbox':
            QAbstractButton.toggle(self.ui.pbox)
        elif saved_pref == 'wbox':
            QAbstractButton.toggle(self.ui.wbox)

        self.ui.chkt_btn.clicked.connect(self.checkout_button)


    def checkout_button(self):
        if self.ui.pbox.isChecked():
            new_pref = 'pbox'
            pm.optionVar(sv=('version_checkout', 'pbox'))
        if self.ui.wbox.isChecked():
            new_pref = 'wbox'
            pm.optionVar(sv=('version_checkout', 'wbox'))

        mw.ui.close()
