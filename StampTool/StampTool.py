import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds

class StampBuddy():
    def __init__(self) -> None:
        self.toolName ='StampTool'
        self.show_ui()


    def show_ui(self):
        self.window = cmds.window(t='StampBuddy', wh=[400,250])
        self.mainLayout = cmds.columnLayout()
        if(cmds.draggerContext(self.toolName, q=True, ex=True)):
            cmds.deleteUI(self.toolName)
        self.dragContext = cmds.draggerContext(self.toolName, pc=self.place_stamp)
        cmds.button(l='Place Stamp', c=self.setup_stamp)
        cmds.showWindow(self.window)


    def setup_stamp(self, *args):
        cmds.setToolTo(self.toolName)


    def place_stamp(self, *args):
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
                x = hitPoint.x
                y = hitPoint.y
                z = hitPoint.z

                print(x, y, z)


app = StampBuddy()