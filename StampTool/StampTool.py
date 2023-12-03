import maya.api.OpenMaya as om
import maya.OpenMaya as omold
import maya.OpenMayaUI as omui
import math
import json
import maya.cmds as cmds
import maya.mel as mel
import os

class Stamp():
    def __init__(self, **kwargs):
        self.name = kwargs ['n']
        self.stampPath = kwargs['sp']

class StampUI():
    def __init__(self, **kwargs):
        self.parent = kwargs['p']
        self.name = kwargs ['n']
        self.stampPath = kwargs['sp']
        self.show_ui()

    def show_ui(self):
        self.layout = cmds.formLayout()
        cmds.button(w=80, l=self.name, c=self.select_stamp)


    def select_stamp(self, *agrs):
        self.parent.setup_stamp_object(self.stampPath)

        
    def getLayout (self):
        return self.layout


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
        #cmds.loadPlugin('StampPlacer', qt=True)
        if(cmds.draggerContext(self.toolName, q=True, ex=True)):
            cmds.deleteUI(self.toolName)
        self.dragContext = cmds.draggerContext(self.toolName, n="Stamp Tool", rc=self.place_stamp, sp='screen')

        self.uiSize = 80

        self.show_ui()

    def show_ui(self):
        self.window = cmds.window(t='StampBuddy', wh=[400,250])
        self.mainLayout = cmds.columnLayout()

        cmds.rowLayout(nc=3)
        cmds.button(l="Load a Stamp Library", c=self.load_library)
        cmds.button(l="Save this Stamp Library", c=self.save_library)
        cmds.button(l="Create New Stamp", c=self.save_stamp)

        cmds.setParent(self.mainLayout)
        cmds.rowLayout(nc=2)
        cmds.button(l='Stamp Tool', c=self.setup_stamp_tool)
        cmds.button(l="Undo Stamp", c=self.undo_stamp)

        cmds.setParent(self.mainLayout)
        self.libraryScrollContainer = cmds.scrollLayout()
        self.libraryLayout = cmds.gridLayout()

        self.prompt_load_library()
        self.display_library()

        cmds.showWindow(self.window)


    def display_library(self):
        cmds.deleteUI(self.libraryLayout)
        cmds.setParent(self.libraryScrollContainer)

        self.libraryLayout = cmds.gridLayout(cw=self.uiSize, nc=self.numLibColumns, nr=self.numLibRows)
        indexX = 1
        indexY = 0
        index = 1
        for stamp in self.stampLibrary:
            cmds.setParent(self.libraryLayout)
            stampUI = StampUI(p=self, n=stamp.name, sp=stamp.stampPath)
            index = indexX + (indexY & self.numLibColumns)
            cmds.gridLayout(self.libraryLayout, e=True, pos=[stampUI.getLayout(), index])
            indexX += 1
            if (indexX % self.numLibColumns == self.numLibColumns):
                indexY +=1


    def calc_dimensions(self):
        winWidth = cmds.scrollLayout(self.libraryScrollContainer, q=True, saw=True)
        winHeight = cmds.scrollLayout(self.libraryScrollContainer, q=True, sah=True)
        self.numLibColumns = 1
        totalHeigth = self.uiSize * self.libraryLayout.__len__()
        if (totalHeigth > winHeight):
            self.numLibColumns = round(winWidth/self.uiSize)

        rows = winHeight / self.uiSize
        rows = math.trunc(rows)
        if (rows <= 0): rows = 1
        self.numLibRows = rows


    def recalc_stamp_grid(self):
        columns = self.numLibColumns
        rows = self.numLibRows
        self.calc_dimensions()
        if (self.numLibColumns != columns | self.numLibRows != rows):
            self.display_library()


    def checkCheckbox(self, checkbox):
        return cmds.checkBox(checkbox, q=True, v=True)


    def setup_stamp_tool(self, *args):
        cmds.setToolTo(self.toolName)


    def setup_stamp_object(self, filePath):
        self.stampPath = filePath


    def undo_stamp(self, *args):
        if (len(self.placedStamps)>0):
            stampToUndo = self.placedStamps.pop(-1)
            cmds.delete(stampToUndo)


    def place_stamp(self, *args):
        priorSelection = cmds.ls(sl=True)
        vpX, vpY, _ = cmds.draggerContext(self.dragContext, q=True, dp=True)

        #cmds.placeStamp(xp=vpX, yp=vpY, sp=str(self.stampPath))

        position = omold.MPoint()
        direction = omold.MVector()

        omui.M3dView().active3dView().viewToWorld(
            int(vpX), int(vpY),
            position,
            direction)
        
        meshIsectParams = omold.MMeshIsectAccelParams()

        for mesh in cmds.ls(typ='mesh'):
            selectionList = omold.MSelectionList()
            selectionList.add(mesh)
            dagPath = omold.MDagPath()
            selectionList.getDagPath(0, dagPath)
            fnMesh = omold.MFnMesh(dagPath)

            hitPoint = omold.MFloatPoint()
            hitRayParam = None
            hitFace = omold.intPtr()
            hitTriangle = None
            hitBary1 = None
            hitBary2 = None

            intersection = fnMesh.closestIntersection(
                omold.MFloatPoint(position),
                omold.MFloatVector(direction),
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
                
                up = omold.MVector (0, 1, 0)
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

                cmds.xform(stamp, m=matrixList)
                cmds.xform(stamp, s=(1,1,1))
                self.placedStamps.append(stamp)        
    
        
        cmds.select(priorSelection)

    
    def prompt_load_library(self):
        promptResult = cmds.confirmDialog(title='load a library', m='do you want to load a stamp library', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
        if (promptResult == 'Yes'):
            self.load_library()


    def save_stamp(self, *args):
        savePromptResult = cmds.promptDialog(t="Name", m="Choose a name for the Stamp", b=["OK", "Cancel"], db="OK", cb="Cancel", ds="Cancel")
        if savePromptResult == "OK":
            text = cmds.promptDialog(q=True, t=True)
            path = cmds.fileDialog2(cap="Choose a Stamp FBX", ff='*.fbx', fm=1)
            p = path[0]
            newstamp = Stamp(n=text, sp=p)
            self.stampLibrary.append(newstamp)
            self.display_library()


    def load_library(self, *args):
        JSONfilter = "*.json"
        self.stampLibraryPath = cmds.fileDialog2(cap="Choose a Stamp Library", ff=JSONfilter, fm=1)
        if self.stampLibraryPath is not None:
            file = open(self.stampLibraryPath[0])
            self.stampLibrary = json.load(file)


    def save_library(self, *args):
        JSONfilter = "*.json"
        self.stampLibraryPath = cmds.fileDialog2(cap="Save a Stamp Library", ff=JSONfilter)
        with open(self.stampLibraryPath[0], "w") as outfile:
            json.dump([ob.__dict__ for ob in self.stampLibrary], outfile)


app = StampBuddy()