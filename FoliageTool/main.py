import maya.api.OpenMaya as om
import random
import math
import maya.cmds as cmds

class FoliageGenerator():

    def __init__(self):
        self.winTitle ="Foliage Tool"
        self.show_ui()


    def facing_angle(self, origin, position, defaultAxis=[0,0,1]):
        forward = om.MVector(position) - om.MVector(origin)
        forward = om.MVector.normalize(forward)
        defaultAxis = om.MVector.normalize(om.MVector(defaultAxis))
        angle = math.degrees(forward.angle(defaultAxis))

        if (origin[0] - position[0] < 0) | (origin[2] - position[2] > 0):
            print ("negating angle")
            angle = -angle

        return angle


    def generate_card(self, position, rotation, width, height, subdivY=1, curveAmnt=0):
        card = cmds.polyPlane(w=width, h=height, sx=1, sy=subdivY)
        cmds.move(0, 0, -height/2, card[0]+".scalePivot", card[0]+".rotatePivot", a=True, ls=True)
        cmds.rotate(0,0,90)
        cmds.delete(card, ch=True)
        
        #Deform for along a curve
        deformer = cmds.nonLinear(typ="bend", curvature=curveAmnt, lowBound=0, highBound=1)
        cmds.move(0, 0, -height/2, card[0]+".scalePivot", card[0]+".rotatePivot", a=True, ls=True)
        cmds.nonLinear(deformer[0], e=True, g=card[0])
        cmds.rotate(90, 0, 0)
        cmds.delete(deformer, ch=True)
        cmds.select(card[0])
        cmds.delete(card[0], ch=True)

        cmds.move(position[0], position[1], position[2], rpr=True)
        cmds.rotate(-90,0,0)
        cmds.delete(card[0], ch=True)
        cmds.rotate(rotation[0], rotation[1], rotation[2], r=True)


    def generate_grass(self, position, offset, numcards, height, width, separation, subdivY=1, curveMinMax=[0,0], faceFromCenter = True):
        i=0
        while i < numcards:
            posX = position[0] + random.uniform(-offset[0], offset[0])
            posY = position[1] + random.uniform(-offset[1], offset[1])
            posZ = position[2] + random.uniform(-offset[2], offset[2])

            dirX = random.uniform(-separation[0], separation[0])
            dirY = random.uniform(-separation[1], separation[1])
            dirZ = random.uniform(-separation[2], separation[2])

            if (faceFromCenter):
                dirY = self.facing_angle(position, [posX, posY, posZ])

            curve = random.uniform(curveMinMax[0], curveMinMax[1])

            self.generate_card([posX, posY, posZ], [dirX,dirY,dirZ], width, height, subdivY, curve)
            i+=1


    def get_floatField(self, field):
        return cmds.floatField(field, q=True, v=True)


    def get_intField(self, field):
        return cmds.intField(field, q=True, v=True)
    

    def get_floatFieldGrp(self, grp):
        return cmds.floatFieldGrp(grp, q=True, v=True)


    def show_ui(self):
        #TODO: Delete old window when making new one
        self.window = cmds.window(title=self.winTitle, widthHeight=(400, 250))
        self.mainLayout = cmds.columnLayout()

        cmds.rowLayout(nc=2, p=self.mainLayout)
        cmds.text("Number of Cards")
        self.numCardsField = cmds.intField(m=1, v=6)

        cmds.rowLayout(nc=2, p=self.mainLayout)
        cmds.text("Height")
        self.heightField = cmds.floatField(m=0.01, v=5)

        cmds.rowLayout(nc=2, p=self.mainLayout)
        cmds.text("Width")
        self.widthField = cmds.floatField(m=0.01, v=1)

        cmds.rowLayout(nc=2, p=self.mainLayout)
        cmds.text("Subdivisions Height")
        self.subdivYField = cmds.intField(m=1, v=5)

        self.curveRangeField = cmds.floatFieldGrp(p=self.mainLayout, nf=2, l="Card Curve Min Max", v1=10,v2=25)

        self.postionRangeField = cmds.floatFieldGrp(p=self.mainLayout, nf=3, l="Grass Position Range", v1=1, v2=0, v3=1)
        self.rotationField = cmds.floatFieldGrp(p=self.mainLayout, nf=3, l="Rotation Range", el="deg", v1=0, v2=0, v3=0)

        cmds.button(label="Generate Grass", p=self.mainLayout, c=lambda args : self.generate_grass([0,0,0], self.get_floatFieldGrp(self.postionRangeField), self.get_intField(self.numCardsField), self.get_floatField(self.heightField), self.get_floatField(self.widthField), self.get_floatFieldGrp(self.rotationField), self.get_intField(self.subdivYField), self.get_floatFieldGrp(self.curveRangeField)))
        cmds.showWindow(self.window)


app = FoliageGenerator()