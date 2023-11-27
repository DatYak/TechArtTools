import maya.api.OpenMaya as om
import maya.OpenMaya as omold
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
import os as os

kXPositionFlag = "-xp"
kXPositionLongFlag = "-xposition"
kYPositionFlag = "-yp"
kYPositionLongFlag = "-yposition"
kStampPathFlag = "-sp"


def maya_useNewAPI(plugin):
    pass


def initializePlugin(plugin):
    vendor = 'Isaac Lovy'
    version = '0.1.0'
    plugin_fn = om.MFnPlugin(plugin, vendor, version)

    try:
        plugin_fn.registerCommand(StampPlacerCmd.COMMAND_NAME, StampPlacerCmd.cmdCreator, StampPlacerCmd.syntaxCreator)
    except:
        om.MGlobal.displayError("Failed to register command: {0}".format(StampPlacerCmd))


def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)

    try:
        plugin_fn.deregisterCommand(StampPlacerCmd.COMMAND_NAME)
    except:
        om.MGlobal.displayError("Failed to deregister command: {0}".format(StampPlacerCmd))


class StampPlacerCmd( om.MPxCommand ):
    
    COMMAND_NAME = 'RemoveStamp'

    def __init__(self):
        om.MPxCommand.__init__(self)
    
    def doIt(self, args):
        self.redoIt(args)
        
        
    def redoIt(self, args):
        position = omold.MPoint()
        direction = omold.MVector()

        argData = om.MArgDatabase(self.syntax(), args)

        xPos = 0
        yPos = 0
        stampPath = ' '

        if argData.isFlagSet(kXPositionFlag): xPos = argData.flagArgumentInt(kXPositionFlag, 0)
        if argData.isFlagSet(kYPositionFlag): yPos = argData.flagArgumentInt(kYPositionFlag, 0)
        if argData.isFlagSet(kStampPathFlag): stampPath = argData.flagArgumentString(kStampPathFlag, 0)

        omui.M3dView().active3dView().viewToWorld(
            int(xPos), int(yPos),
            position,
            direction)
        
        meshIsectParams = omold.MMeshIsectAccelParams()

        for mesh in cmds.ls(typ='mesh'):
            selectionList = omold.MSelectionList()
            selectionList.add(mesh)
            dagPath = omold.MDagPath()
            selectionList.getDagPath(0, dagPath)
            fnMesh = omold.MFnMesh(dagPath)

            face_idx_util = omold.MScriptUtil()
            face_idx_util.createFromInt(-1)

            hitPoint = omold.MFloatPoint()
            hitRayParam = None
            hitTriangle = None
            face_int_ptr = face_idx_util.asIntPtr()
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
                face_int_ptr,
                hitTriangle,
                hitBary1,
                hitBary2)

            if (intersection):
                
    
    
    def undoIt(self):
        pass
    

    def isUndoable(self):
        return True
    

    @staticmethod
    def cmdCreator():
        return StampPlacerCmd()
    
    
    @staticmethod
    def syntaxCreator():
        syntax = om.MSyntax()
        syntax.addFlag(kXPositionFlag, kXPositionLongFlag, om.MSyntax.kDistance)
        syntax.addFlag(kYPositionFlag, kYPositionLongFlag, om.MSyntax.kDistance)
        return syntax