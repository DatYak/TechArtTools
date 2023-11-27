import math
import json
import maya.cmds as cmds

class Stamp():
    def __init__(self, **kwargs):
        self.name = kwargs ['n']
        self.stampPath = kwargs['sp']
        self.imagePath = kwargs['i']


class StampUI():
    def __init__(self, **kwargs):
        self.parent = kwargs['p']
        self.name = kwargs ['n']
        self.stampPath = kwargs['sp']
        self.icon = cmds.image(kwargs['i'])
        self.show_ui()

    def show_ui(self):
        self.layout = cmds.formLayout()
        cmds.iconTextButton(w=80, l=self.name, i=self.icon, st='iconAndTextHorizontal', c=self.select_stamp)


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

        #Variable Setup
        cmds.loadPlugin('StampPlacer', qt=True)
        if(cmds.draggerContext(self.toolName, q=True, ex=True)):
            cmds.deleteUI(self.toolName)
        self.dragContext = cmds.draggerContext(self.toolName, n="Stamp Tool", rc=self.place_stamp, sp='screen')

        self.uiSize = 80

        self.show_ui()

    def show_ui(self):
        self.window = cmds.window(t='StampBuddy', wh=[400,250])
        self.mainLayout = cmds.columnLayout()

        cmds.rowLayout(nc=2)
        cmds.button(l='Stamp Tool', c=self.setup_stamp_tool)
        cmds.button(l="Create New Stamp", c=self.save_stamp)

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
            stampUI = StampUI(p=self, n=stamp.name, sp=stamp.stampPath, i=stamp.imagePath)
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


    def place_stamp(self, *args):
        priorSelection = cmds.ls(sl=True)
        vpX, vpY, _ = cmds.draggerContext(self.dragContext, q=True, dp=True)

        cmds.GetStampMatrix(xp=vpX, yp=vpY, sp=str(self.stampPath))
        
        cmds.select(priorSelection)

    
    def prompt_load_library(self):
        promptResult = cmds.confirmDialog(title='load a library', m='do you want to load a stamp library', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
        if (promptResult == 'Yes'):
            self.load_library()


    def save_stamp(self, *args):
        savePromptResult = cmds.promptDialog(t="Name", m="Choose a name for the Stamp", b=["OK", "Cancel"], db="OK", cb="Cancel", ds="Cancel")
        if savePromptResult == "OK":
            text = cmds.promptDialog(q=True, t=True)
            path = cmds.fileDialog2(cap="Choose a Stamp FBX", ff='*.fbx', fm=1)[0]
            imagePath = cmds.fileDialog2(cap="Choose an image icon", ff='*.png', fm=1)[0]
            newstamp = Stamp(n=text, sp=path, i=imagePath)
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
        self.stampLibraryPath = cmds.fileDialog2(cap="Choose a Stamp Library", ff=JSONfilter)
        with open(self.stampLibraryPath[0], "w") as outfile:
            json.dump(self.stampLibrary, outfile)


app = StampBuddy()