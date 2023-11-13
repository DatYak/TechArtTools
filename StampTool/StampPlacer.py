import maya.api.OpenMaya as om
import maya.OpenMaya as omold
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel

kXPositionFlag = "-xp"
kXPositionLongFlag = "-xposition"
kYPositionFlag = "-yp"
kYPositionLongFlag = "-yposition"
kStampPathFlag = "-sp"
kStampPathLongFlag = "-stamppath"


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
    
    COMMAND_NAME = 'GetStampMatrix'

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
                print (stampPath)
                stamp = cmds.file(stampPath, i=True, typ='FBX', mnc=True, ns=':', rnn=True)

                cmds.xform(stamp, m=matrixList)
                cmds.xform(stamp, s=(1,1,1))
                break        
    
    
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
        syntax.addFlag(kStampPathFlag, kStampPathLongFlag, om.MSyntax.kString)
        return syntax