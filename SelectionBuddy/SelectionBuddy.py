# Selection Buddy
# Created by Isaac Lovy
#
# Current features include:
#  - Save, remove, and load Maya selections via UI
#  - Lock the open library to avoid unwanted changes
#  - Selections saved and loaded from JSON libraries
#  - Reorder selections

import math
import maya.OpenMaya as om
import maya.OpenMayaUI as omu
import maya.cmds as cmds
import json

winName = 'SelectionBuddy'
buttonPref = 'Select '
optionWidth = 200
optionHeight = 25

class SelectionOption:
    def __init__(self, **kwargs):
        self.selection_buddy = kwargs['b']
        self.selection_name = kwargs['n']
        self.saved_selection = kwargs['s']
        self.editing = kwargs ['e']
        self.options_layout = cmds.formLayout(nd=100)
        selBTTN = cmds.button(buttonPref + self.selection_name, c=self.useSelection, w=125, h=20)

        if (self.editing):
            delBTTN = cmds.button("DEL", c=self.removeSelecton, w=35, bgc=(.95, 0.2, 0.2), h=20)
            upBTTN = cmds.button("^", c=self.moveUp, w=15, h=20)
            downBTTN = cmds.button("v", c=self.moveDown, w=15, h=20)
            cmds.formLayout(self.options_layout, edit= True,
                af=[
                    (selBTTN, 'left', 5),
                    (delBTTN, 'right', 5)],
                ac=[
                    (upBTTN, 'left', 0, selBTTN),
                    (upBTTN, 'right', 0, downBTTN),
                    (downBTTN, 'right', 0, delBTTN)]
                )

    def useSelection(self, *args):
        self.selection_buddy.useSelection(self.saved_selection)

    def removeSelecton(self, *args):
        self.selection_buddy.removeSelecton(self.selection_name)
    
    def moveUp(self, *args):
        self.selection_buddy.moveSelectionUp(self.selection_name)
        
    def moveDown(self, *args):
        self.selection_buddy.moveSelectionDown(self.selection_name)
    
    def getLayout (self):
        return self.options_layout

class SelectionBuddy:
    saved_selections = {}
    selection_layout = any
    selection_library_path = any
    selection_window_layout = any
    selections_scrollLayout = any
    number_columns = 1
    number_rows = 1
    editing_library = False
    grid_view = True
    cam_select_mode = False
    hierarchy_select_mode="Saved Only"

    edit_library_btn = any
    save_selection_btn = any
    save_library_btn = any
    load_library_btn = any
    
    cam_selection_mode_btn = any
    hierarchy_select_mode_btn = any

    def __init__(self):
        self.saved_selections
        self.selection_layout
        self.createWindow()

    def createWindow(self):
        if cmds.window(winName, exists=True):
            cmds.deleteUI(winName)
        cmds.window(winName)
        self.selection_window_layout = cmds.formLayout(numberOfDivisions=100)
        optionsBar = cmds.rowColumnLayout(nr=1)
        self.edit_library_btn = cmds.button("Unlock Library", c=self.editLibrary)
        self.save_selection_btn = cmds.button("Save Selection", c=self.saveSelection, en=self.editing_library)
        self.save_library_btn = cmds.button("Save Library", c=self.saveLibrary, en=self.editing_library)
        self.load_library_btn = cmds.button("Load Library", c=self.loadLibrary, en=self.editing_library)
        cmds.setParent(self.selection_window_layout)
        self.selections_scrollLayout = cmds.scrollLayout(rc=self.recalculateGrid)
        self.calcDimentions()
        self.selection_layout = cmds.gridLayout(cw=optionWidth, nc=self.number_columns, nr=self.number_rows)
        cmds.formLayout(self.selection_window_layout, edit= True,
            af= [
                (optionsBar, 'top', 0),
                (self.selections_scrollLayout, 'bottom', 5),
                (self.selections_scrollLayout, 'right', 5),
                (self.selections_scrollLayout, 'left', 5)],
            ac=[
                (self.selections_scrollLayout, 'top', 5, optionsBar)
            ])
        cmds.setParent('..')
        modifiersBar = cmds.rowColumnLayout(nr=1)
        self.cam_selection_mode_btn = cmds.button("Select: Any", c=self.changeCamSelection)
        self.hierarchy_select_mode_btn = cmds.optionMenu("Select: Hierarchy Mode", cc=self.changeChildSelection)
        cmds.menuItem(l="Saved Only")
        cmds.menuItem(l="Saved + Children")
        self.propmtLoadLibrary()
        self.displaySelections()
        cmds.showWindow(winName)
        cmds.window(winName, e=True, wh=(300, 400))

    def saveSelection(self, *args):
        newSelection = cmds.ls(sl=True)
        savePromptResult = cmds.promptDialog(t="Save As", m="Choose a name for the selection", b=["OK", "Cancel"], db="OK", cb="Cancel", ds="Cancel")
        if savePromptResult == "OK":
            text = cmds.promptDialog(q=True, t=True)
            if self.hasSelectionName(text) == False:
                self.saved_selections.update({text : newSelection})
        self.displaySelections()

    def useSelection(self, selection, *args):
        usedSelection = list(selection)
        cmds.select(usedSelection)

        if (self.cam_select_mode):
            self.selectOnlyCameraVisible(usedSelection=usedSelection)

        if (self.hierarchy_select_mode == "Saved + Children"):
            cmds.select(usedSelection, hi=True)

    def selectOnlyCameraVisible(self, usedSelection):
            #Selecting in veiw of camera from https://forums.autodesk.com/t5/maya-programming/how-can-i-get-objects-in-camera-view/td-p/11545619
            state = cmds.selectPref(q=True, useDepth = True)
            cmds.selectPref(useDepth=True)
            
            viewPort = omu.M3dView.active3dView()
            om.MGlobal.selectFromScreen(0,0,viewPort.portWidth(),viewPort.portHeight(),om.MGlobal.kReplaceList,om.MGlobal.kSurfaceSelectMethod)
            cmds.selectPref(useDepth = state)
            inFrameObjects = cmds.ls(sl=True)
            for each in usedSelection:
                if each not in inFrameObjects:
                    usedSelection.remove(each)
            cmds.select(usedSelection)
        

    def removeSelecton(self, selection, *args):
        if (self.hasSelectionName(selection)):
            del self.saved_selections[selection]
        self.displaySelections()

    def displaySelections(self):
        cmds.deleteUI(self.selection_layout)
        cmds.setParent(self.selections_scrollLayout)
        self.selection_layout = cmds.gridLayout(cw=optionWidth, nc=self.number_columns, nr=self.number_rows)
        indexX = 1
        indexY = 0
        index = 1
        for selection in self.saved_selections:
            cmds.setParent(self.selection_layout)
            option = SelectionOption(b=self, n=selection, s=self.saved_selections[selection], e=self.editing_library)
            index = indexX + (indexY & self.number_columns)
            cmds.gridLayout(self.selection_layout, e=True, pos=[option.getLayout(), index])
            indexX += 1
            if (indexX % self.number_columns == self.number_columns):
                indexY +=1

    def calcDimentions(self):
        self.calcNumRows()
        self.calcNumColumns()
        print ("Rows = " + str(self.number_rows))
        print ("Columns = " + str(self.number_columns))

    def calcNumColumns(self):
        winWidth = cmds.scrollLayout(self.selections_scrollLayout, q=True, saw=True)
        winHeight = cmds.scrollLayout(self.selections_scrollLayout, q=True, sah=True)
        self.number_columns = 1
        if (self.grid_view):
            totalHeight = optionHeight * self.saved_selections.__len__()
            if (totalHeight > winHeight):
                self.number_columns = round(winWidth / optionWidth)

    def calcNumRows(self):
        winHeight = cmds.scrollLayout(self.selections_scrollLayout, q=True, sah=True)
        rows = winHeight / optionHeight 
        rows = math.trunc(rows)
        if (rows <= 0): rows = 1
        self.number_rows = rows

    def recalculateGrid(self):
        columns = self.number_columns
        rows = self.number_rows
        self.calcDimentions()
        if (self.number_columns != columns | self.number_rows != rows):
            self.displaySelections()

    def moveSelectionUp(self, name):
        currentIndex = self.getSelectionIndex(name=name)
        if (currentIndex != 0):
            self.swapSelection(currentIndex, currentIndex - 1)

    def moveSelectionDown(self, name):
            currentIndex = self.getSelectionIndex(name=name)
            if (currentIndex != self.saved_selections.__len__()):
                self.swapSelection(currentIndex, currentIndex + 1)

    def swapSelection(self, index1, index2):
        selTups = list(self.saved_selections.items())
        selTups[index1], selTups[index2] = selTups[index2], selTups[index1]
        self.saved_selections = dict(selTups)
        self.displaySelections()

    def getSelectionIndex(self, name):
        return list(self.saved_selections.keys()).index(name)

    def hasSelectionName(self, name):
        for selection in self.saved_selections:
            if selection == name:
                return True
        return False

    def changeCamSelection (self,*args):
        self.cam_select_mode = not self.cam_select_mode
        button_label = "Select: "
        if (self.cam_select_mode): button_label += "Cam"
        if (not self.cam_select_mode): button_label += "Any"
        cmds.button(self.cam_selection_mode_btn, e=True, l=button_label)
    
    def changeChildSelection(self,*args):
        self.hierarchy_select_mode = args[0]

    def editLibrary(self, *args):
        self.editing_library = not self.editing_library
        button_label = ""
        if (self.editing_library): button_label = "Lock Libary"
        if (not self.editing_library): button_label = "Unlock Libary"
        cmds.button(self.edit_library_btn, e=True, l=button_label)
        self.displaySelections()
        cmds.button(self.save_selection_btn, e=True, en= self.editing_library)
        cmds.button(self.save_library_btn, e=True, en= self.editing_library)
        cmds.button(self.load_library_btn, e=True, en= self.editing_library)

    def propmtLoadLibrary(self):
        loadPromptResult = cmds.confirmDialog(title='Load a Library', message='Do you want to load a saved library?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
        if loadPromptResult == 'Yes':
            self.loadLibrary()

    def loadLibrary(self, *args):
        JSONfilter = "*.json"
        self.selection_library_path = cmds.fileDialog2(cap="Choose a Selection Buddy Library", ff=JSONfilter, fm=1)
        file = open(self.selection_library_path[0])
        self.saved_selections = json.load(file)
        self.displaySelections()

    def saveLibrary(self, *args):
        JSONfilter = "*.json"
        self.selection_library_path = cmds.fileDialog2(cap="Choose a Selection Buddy Library", ff=JSONfilter)
        with open(self.selection_library_path[0], "w") as outfile:
            json.dump(self.saved_selections, outfile)

selectionSaver = SelectionBuddy()