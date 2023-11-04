import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds

class StampBuddy():
    def __init__(self) -> None:
        self.toolName ='StampTool'

        #Variable Setup
        if(cmds.draggerContext(self.toolName, q=True, ex=True)):
            cmds.deleteUI(self.toolName)
        self.dragContext = cmds.draggerContext(self.toolName, rc=self.place_stamp, sp='screen')

        self.show_ui()

    def show_ui(self):
        self.window = cmds.window(t='StampBuddy', wh=[400,250])
        self.mainLayout = cmds.columnLayout()

        cmds.button(l='Place Stamp', c=self.setup_stamp)
        cmds.rowLayout()
        self.isInsettingCheck = cmds.checkBox(l='Inset?')
        cmds.showWindow(self.window)


    def checkCheckbox(self, checkbox):
        return cmds.checkBox(checkbox, q=True, v=True)


    def setup_stamp(self, *args):
        cmds.setToolTo(self.toolName)


    def place_stamp(self, *args):
        priorSelection = cmds.ls(sl=True)
        vpX, vpY, _ = cmds.draggerContext(self.dragContext, q=True, dp=True)
        position = om.MPoint()
        direction = om.MVector()

        omui.M3dView().active3dView().viewToWorld(
            int(vpX), int(vpY),
            position,
            direction)
        
        meshIsectParams = om.MMeshIsectAccelParams()

        for mesh in cmds.ls(typ='mesh'):
            selectionList = om.MSelectionList()
            selectionList.add(mesh)
            dagPath = om.MDagPath()
            selectionList.getDagPath(0, dagPath)
            fnMesh = om.MFnMesh(dagPath)

            hitPoint = om.MFloatPoint()
            hitRayParam = om.floatPtr()
            hitFace = om.intPtr()
            hitTriangle = om.intPtr()
            hitBary1 =  om.floatPtr()
            hitBary2 =  om.floatPtr()

            intersection = fnMesh.closestIntersection(
                om.MFloatPoint(position),
                om.MFloatVector(direction),
                None,
                None,
                False,
                om.MSpace.kWorld,
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

                base = dagPath.fullPathName().__str__()

                x = hitPoint.x
                y = hitPoint.y
                z = hitPoint.z
                
                normal = om.MVector()
                fnMesh.getPolygonNormal(hitFace.value(), normal, om.MSpace.kWorld)
                
                up = om.MVector (0, 1, 0)
                right = normal ^ up
                up = right ^ normal

                matrixList = [
                    right.x, right.y, right.z, 0.0,
                    up.x, up.y, up.z, 0.0,
                    normal.x, normal.y, normal.z, 0.0,
                    x, y, z, 1.0
                ]
                stamp = cmds.polyCube()
                cmds.xform(stamp, m=matrixList)
                cmds.xform(stamp, s=(1,1,1))

                if self.checkCheckbox(self.isInsettingCheck):
                    cmds.xform(stamp, ro=(180, 0, 0))
                    combined = cmds.polyCBoolOp(base, stamp, op=2)
                    cmds.delete(combined, ch=True)

                cmds.select(priorSelection)
                break


app = StampBuddy()