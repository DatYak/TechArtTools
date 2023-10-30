"""
Level Exporter and Importer
Made by Isaac Lovy for Moles In a Bowl

Imports and Exports objects at a smaller and scaled up size respectively
To allow for large assets to be worked on at a more usable scale.
"""

"""
import maya.cmds as cmds
import sys

workspace_path = cmds.workspace( q=True, rd=True )

workspace_path += 'scripts'

sys.path.append(workspace_path)

import levelExporter
levelExporter.launch_import_export()
"""

import maya.cmds as cmds
class ImporterExporter():

    win = any
    scale_field = any

    def __init__(self):
        self.showUI()

    def showUI(self):
        self.win = cmds.window(t='Export Import Scale Tool', wh= (300,200))
        cmds.columnLayout()
        cmds.button('Import', c=self.importFBX)
        cmds.button('Export', c=self.exportFBX)
        cmds.columnLayout(p=self.win)
        cmds.text("Scale Factor")
        self.scale_field = cmds.floatField(min=.01, max=100, v=2)
        cmds.showWindow(self.win)
        
    def exportFBX(self, *args):
        scale_by = cmds.floatField(self.scale_field, q=True, v=True)
        selected_objects = cmds.ls(sl=True)

        duplicated_objects = cmds.duplicate(selected_objects, n='exportGroup', rc=True)
        cmds.select(duplicated_objects, hi=True)
        cmds.scale(scale_by, scale_by, scale_by, duplicated_objects, cp=True, a=True)

        file_path = cmds.fileDialog2(cap='Scale & Export FBX', fm=0)
        cmds.file(file_path, force=True, options='v=0;', typ='FBX export', pr=True,  es=True, fmd=0)

        cmds.delete(duplicated_objects)
        cmds.select(selected_objects)

        cmds.deleteUI(self.win)

    def importFBX(self, *args):
        scale_by = 1 / cmds.floatField(self.scale_field, q=True, v=True)
        file_path = cmds.fileDialog2(cap='Import & Scale FBX', fm=1)
        new_objects = cmds.file(file_path, i=True, mnc=True, ns=':', rnn=True)
        cmds.scale(scale_by, scale_by, scale_by, new_objects, cp=True, a=True)
        cmds.select(new_objects)

        cmds.makeIdentity(new_objects, apply=True, t=True, r=True, s=True)

        cmds.deleteUI(self.win)

def launch_import_export():
    app=ImporterExporter()