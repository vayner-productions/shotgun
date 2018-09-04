from PySide2 import QtCore, QtWidgets, QtUiTools
import pymel.core as pm
import os
import shutil
workspace = pm.system.workspace


def get_shaders():
    """get shaders connected to geometry and particles in the scene"""
    shaders = []
    for se in pm.ls(type="shadingEngine"):
        se_inputs = se.inputs()
        if (len(se_inputs) > 1) and ("lambert1" not in se_inputs):
            shaders += [se_inputs[0]]
    return shaders


def export_shaders():
    """export selected shaders"""
    return


def organize_textures():
    file_nodes = pm.ls(textures=1)
    unique_files = set([])
    src_files = set([])
    for f in file_nodes:
        try:
            file_name = f.fileTextureName.get()
            src_path = pm.workspace.expandName(pm.workspace.fileRules["sourceImages"])
            name = os.path.basename(file_name)
            if file_name.rsplit(".", 1)[1] == "hdr":
                src_path = r"{}/HDRI/{}".format(src_path, name)
            else:
                shot = os.path.basename(pm.workspace.fileRules["scene"])
                src_path = r"{}/Assets/{}/{}".format(src_path, shot, name)

            # saves from copying the same file twice
            if not file_name in unique_files:
                shutil.copy2(file_name, src_path)

            # checks if the same file is coming from a different directory
            if not src_path in src_files:
                f.fileTextureName.set(src_path)
                unique_files.add(file_name)
                src_files.add([f, src_path])
        except:
            pass
    if src_files:
        pm.warning(">> Can not determine if the following are duplicates:")
        for f in src_files:
            print ">>", f
    print ">> consolidated files"
    return
