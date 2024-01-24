'''
Stamp Tool For Maya
Author: Isaac Lovy

Current Features
    - Place stamps on objects using Raytracing
    - Have the size of each stamp be determined by dragged distance 
    - OR input a set scale
    - Name and store references to FBX files as stamps
    - Save, Load, and edit collections of stamps

'''

import maya.api.OpenMaya as om
import maya.OpenMaya as omold
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
import os
import math
import json


class Stamp(object):
    def __init__(self, **kwargs):
        self.__type__ = 'Stamp'
        self.name = kwargs ['n']
        self.stampPath = kwargs['sp']


def obj_dict(obj):
    return obj.__dict__


def stamp_decoder(obj):
    if '__type__' in obj and obj['__type__'] == 'Stamp':
        return (Stamp(n=obj['name'], sp=obj['stampPath']))
    return obj


class StampUI():
    def __init__(self, **kwargs):
        self.parent = kwargs['p']
        self.name = kwargs ['n']
        self.stampPath = kwargs['sp']
        self.index = kwargs['i']
        self.editing = kwargs['e']
        self.show_ui()


    def show_ui(self):
        self.layout = cmds.formLayout()
        if (not self.editing):
            cmds.button(h=20, w=80, l=self.name, c=self.select_stamp)
        else:
            cmds.rowLayout(nc=2)
            cmds.button(h=20, w=60, l=self.name, c=self.select_stamp)
            cmds.button("X", c=self.promptDelete, w=20, bgc=(.95, 0.2, 0.2), h=20)


    def select_stamp(self, *agrs):
        self.parent.setup_stamp_object(self.stampPath)

        
    def getLayout (self):
        return self.layout
    

    def promptDelete(self, *args):
        self.parent.prompt_delete_stamp(self.index)



class StampBuddy():
    
    stampPlugin = any

    def __init__(self) -> None:
        self.toolName ='StampTool'

        self.libraryLayout = any
        self.libraryScrollContainer = any
        self.stampLibrary = []
        self.stampLibraryPath = any

        self.stampPath = ""

        self.numLibColumns = 1
        self.numLibRows = 1

        self.placedStamps = []

        #Variable Setup
        if(cmds.draggerContext(self.toolName, q=True, ex=True)):
            cmds.deleteUI(self.toolName)
        self.dragContext = cmds.draggerContext(self.toolName, n="Stamp Tool", rc=self.place_stamp, sp='screen')

        self.uiSize = [80,20]

        self.show_ui()

    def show_ui(self):
        self.window = cmds.window(t='StampBuddy', wh=[400,250])
        self.mainLayout = cmds.columnLayout()

        cmds.rowLayout(nc=4, gsp=5)
        cmds.button(l="Load a Stamp Library", c=self.load_library)
        cmds.button(l="Save this Stamp Library", c=self.save_library)
        cmds.button(l="Create New Stamp", c=self.save_stamp)
        self.isEditingCB = cmds.checkBox(l='Editing Library?', v=False, cc=self.display_library)

        cmds.setParent(self.mainLayout)
        self.libraryFormLayout = cmds.formLayout(numberOfDivisions=100)
        optionsBar = cmds.rowLayout(nc=4, gsp=5)
        cmds.button(h=self.uiSize[1], l='Stamp Tool', c=self.setup_stamp_tool)
        self.isDraggingToggle = cmds.checkBox(h=self.uiSize[1], l='Drag To Scale', v=True)
        self.scaleEntry = cmds.floatField(h=self.uiSize[1], ann='Scale', min=0.01, v=1)
        cmds.button(h=self.uiSize[1], l="Undo Stamp", c=self.undo_stamp)

        cmds.setParent(self.libraryFormLayout)
        self.libraryScrollContainer = cmds.scrollLayout(rc=self.recalc_stamp_grid)
        self.calc_dimensions()
        self.libraryLayout = cmds.gridLayout(cwh=self.uiSize, nc=self.numLibColumns, nr=self.numLibRows, cr=True)

        cmds.formLayout(self.libraryFormLayout, edit= True,
                    af= [
                        (optionsBar, 'top', 0),
                        (self.libraryScrollContainer, 'bottom', 5),
                        (self.libraryScrollContainer, 'right', 5),
                        (self.libraryScrollContainer, 'left', 5)],
                    ac=[
                        (self.libraryScrollContainer, 'top', 5, optionsBar)
                    ])

        self.prompt_load_library()
        self.display_library()

        cmds.showWindow(self.window)


    def quit(self):
        cmds.deleteUI(self.window)


    def display_library(self, *args):
        cmds.deleteUI(self.libraryLayout)
        cmds.setParent(self.libraryScrollContainer)

        self.libraryLayout = cmds.gridLayout(cwh=self.uiSize, nc=self.numLibColumns, nr=self.numLibRows, cr=True)
        indexX = 1
        indexY = 0
        index = 1
        for stamp in self.stampLibrary:
            cmds.setParent(self.libraryLayout)
            stampUI = StampUI(p=self, n=stamp.name, sp=stamp.stampPath, i=self.stampLibrary.index(stamp), e=self.check_checkbox(self.isEditingCB))
            index = indexX + (indexY & self.numLibColumns)
            cmds.gridLayout(self.libraryLayout, e=True, pos=[stampUI.getLayout(), index])
            indexX += 1
            if (indexX % self.numLibColumns == self.numLibColumns):
                indexY +=1


    def calc_dimensions(self):
        winWidth = cmds.scrollLayout(self.libraryScrollContainer, q=True, saw=True)
        winHeight = cmds.scrollLayout(self.libraryScrollContainer, q=True, sah=True)
        self.numLibRows = 1
        totalWidth = self.uiSize[0] * self.stampLibrary.__len__()
        if (totalWidth > winWidth):
            self.numLibColumns = round(winWidth/self.uiSize[0])

        rows = winHeight / self.uiSize[1]
        rows = math.trunc(rows)
        if (rows <= 0): rows = 1
        self.numLibRows = rows


    def recalc_stamp_grid(self):
        columns = self.numLibColumns
        rows = self.numLibRows
        self.calc_dimensions()
        if (self.numLibColumns != columns | self.numLibRows != rows):
            self.display_library()


    def check_checkbox(self, checkbox):
        return cmds.checkBox(checkbox, q=True, v=True)


    def setup_stamp_tool(self, *args):
        cmds.setToolTo(self.toolName)


    def setup_stamp_object(self, filePath):
        self.stampPath = os.path.join(os.path.dirname(self.stampLibraryPath), filePath)


    def undo_stamp(self, *args):
        if (len(self.placedStamps)>0):
            stampToUndo = self.placedStamps.pop(-1)
            cmds.delete(stampToUndo)


    def place_stamp(self, *args):
        priorSelection = cmds.ls(sl=True)
        ipX, ipY, _ = cmds.draggerContext(self.dragContext, q=True, ap=True)
        vpX, vpY, _ = cmds.draggerContext(self.dragContext, q=True, dp=True)

        position = omold.MPoint()
        direction = omold.MVector()

        omui.M3dView().active3dView().viewToWorld(
            int(vpX), int(vpY),
            position,
            direction)

        initialPosition = omold.MPoint()
        initialDirection = omold.MVector()

        omui.M3dView().active3dView().viewToWorld(
            int(ipX), int(ipY),
            initialPosition,
            initialDirection)
        
        meshIsectParams = omold.MMeshIsectAccelParams()

        for mesh in cmds.ls(typ='mesh'):
            selectionList = omold.MSelectionList()
            selectionList.add(mesh)
            dagPath = omold.MDagPath()
            selectionList.getDagPath(0, dagPath)
            fnMesh = omold.MFnMesh(dagPath)

            hitPoint = omold.MFloatPoint()
            hitRayParam = omold.floatPtr()
            hitFace = omold.intPtr()
            hitTriangle = None
            hitBary1 = None
            hitBary2 = None

            intersection = fnMesh.closestIntersection(
                omold.MFloatPoint(initialPosition),
                omold.MFloatVector(initialDirection),
                None,
                None,
                False,
                omold.MSpace.kWorld,
                99999,
                False,
                meshIsectParams,
                hitPoint,
                hitRayParam,
                hitFace,
                hitTriangle,
                hitBary1,
                hitBary2)

            if (intersection):
                x = hitPoint.x
                y = hitPoint.y
                z = hitPoint.z
                
                normal = omold.MVector()
                fnMesh.getPolygonNormal(hitFace.value(), normal, omold.MSpace.kWorld)
                
                up = omold.MVector (-1, 0, 0)
                right = normal ^ up
                up = right ^ normal

                matrixList = [
                    right.x, right.y, right.z, 0.0,
                    up.x, up.y, up.z, 0.0,
                    normal.x, normal.y, normal.z, 0.0,
                    x, y, z, 1.0
                ]

                mel.eval("FBXImportMode -v add")
                stamp = cmds.file(self.stampPath, i=True, typ='FBX', mnc=True, ns=':', rnn=True)

                scale = 1
                if cmds.checkBox(self.isDraggingToggle, q=True, v=True):
                    scale = math.sqrt((initialPosition.x - position.x) ** 2 + (initialPosition.y - position.y) ** 2 + (initialPosition.z - position.z) ** 2)
                    scale *= 10 * hitRayParam.value()
                else:
                    scale = cmds.floatField(self.scaleEntry, q=True, v=True)

                cmds.xform(stamp, m=matrixList)
                cmds.xform(stamp, s=(scale,scale,scale))
                self.placedStamps.append(stamp)        
                cmds.select(priorSelection)
                return

    
    def prompt_delete_stamp(self, index):
        promptResult = cmds.confirmDialog(title='Delete Stamp: ' + self.stampLibrary[index].name + '?', m='Remove this stamp (FBX file will remain)', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
        if (promptResult == 'Yes'):
            self.stampLibrary.pop(index)
            self.display_library()


    def prompt_load_library(self):
        promptResult = cmds.confirmDialog(title='load a library', m='do you want to create or load a stamp library', button=['Create','Load'], defaultButton='Create', cancelButton='Quit', dismissString='Quit' )
        if (promptResult == 'Create'):
            self.save_library()
        if (promptResult == 'Load'):
            self.load_library()
        if(promptResult == 'Quit'):
            self.quit()


    def save_stamp(self, *args):
        savePromptResult = cmds.promptDialog(t="Name", m="Choose a name for the Stamp", b=["OK", "Cancel"], db="OK", cb="Cancel", ds="Cancel")
        if savePromptResult == "OK":
            text = cmds.promptDialog(q=True, t=True)
            path = cmds.fileDialog2(cap="Choose a Stamp FBX", ff='*.fbx', fm=1)
            p = path[0]
            p = os.path.relpath(p, os.path.dirname(self.stampLibraryPath))
            newstamp = Stamp(n=text, sp=p)
            self.stampLibrary.append(newstamp)
            self.display_library()


    def load_library(self, *args):
        prevLibPath = self.stampLibraryPath
        JSONfilter = "*.json"
        self.stampLibraryPath = cmds.fileDialog2(cap="Choose a Stamp Library", ff=JSONfilter, fm=1)
        if self.stampLibraryPath is not None:
            file = open(self.stampLibraryPath[0])
            self.stampLibrary = json.load(file, object_hook=stamp_decoder)
            file.close()
            self.stampLibraryPath = self.stampLibraryPath[0]
        else:
            self.stampLibraryPath = prevLibPath


    def save_library(self, *args):
        JSONfilter = "*.json"
        self.stampLibraryPath = cmds.fileDialog2(cap="Save a Stamp Library", ff=JSONfilter)
        self.stampLibraryPath = self.stampLibraryPath[0]
        with open(self.stampLibraryPath, "w") as outfile:
            json.dump(self.stampLibrary, outfile, default=obj_dict)


app = StampBuddy()