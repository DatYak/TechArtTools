import sys
import random
import math
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt

noise_size = 512
layer_thumb_size = 128

class NoiseLayer(QtWidgets.QHBoxLayout):
    def __init__(self):
        super(NoiseLayer, self).__init__()


    def showNoise(self, noise, parent):
        self.p = parent
        self.img = noise
        label = QtWidgets.QLabel()
        self.thumb = self.img.smoothScaled(layer_thumb_size, layer_thumb_size)
        label.setPixmap(QtGui.QPixmap(self.thumb))
        label.setMaximumSize(layer_thumb_size, layer_thumb_size)
        self.addWidget(label)

        self.blend_option = QtGui.QPainter.CompositionMode.CompositionMode_Source

        self.blend_dropdown = QtWidgets.QComboBox()
        self.blend_dropdown.addItem("Normal")
        self.blend_dropdown.addItem("Multiply")
        self.blend_dropdown.addItem("Screen")
        self.addWidget(self.blend_dropdown)
        self.blend_dropdown.currentTextChanged.connect(self.blendmodeChanged)

        self.opacity_slider = QtWidgets.QSlider(Qt.Orientation.Vertical)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(255)
        self.opacity_slider.setValue(255)
        self.addWidget(self.opacity_slider) 
        self.opacity_slider.sliderMoved.connect(self.opacityChanged)

    def opacityChanged(self, value):
        self.p.displayOutput()

    def blendmodeChanged(self, m):
        if m == "Normal": self.blend_option = QtGui.QPainter.CompositionMode.CompositionMode_Source
        if m == "Multiply": self.blend_option = QtGui.QPainter.CompositionMode.CompositionMode_Multiply
        if m == "Screen": self.blend_option = QtGui.QPainter.CompositionMode.CompositionMode_Screen
        self.p.displayOutput()


#https://gamedev.stackexchange.com/questions/23625/how-do-you-generate-tileable-perlin-noise
class PerlinNoise():

    def __init__(self):    
        self.seed()


    def seed(self):
        self.perm = [*range(256)]
        random.shuffle(self.perm)
        self.perm += self.perm
        self.dirs = [(math.cos(a * 2.0 * math.pi / 256),
                math.sin(a * 2.0 * math.pi / 256))
                for a in range(256)]


    def fBm(self, x, y, per, octs):
        val = 0
        for o in range(octs):
            val += 0.5**o * self.noise(x*2**o, y*2**o, per*2**o)
        return val


    def noise(self, x, y, per):
        def surflet(gridX, gridY):
            distX, distY = abs(x-gridX), abs(y-gridY)
            polyX = 1 - 6*distX**5 + 15*distX**4 - 10*distX**3
            polyY = 1 - 6*distY**5 + 15*distY**4 - 10*distY**3
            hashed = self.perm[self.perm[int(gridX)%per] + int(gridY)%per]
            grad = (x-gridX)*self.dirs[hashed][0] + (y-gridY)*self.dirs[hashed][1]
            return polyX * polyY * grad
        intX, intY = int(x), int(y)
        return (surflet(intX+0, intY+0) + surflet(intX+1, intY+0) +
                surflet(intX+0, intY+1) + surflet(intX+1, intY+1))



class NoiseBuddy(QtWidgets.QMainWindow):
    def __init__(self):
        super(NoiseBuddy, self).__init__()

        self.setWindowTitle("Noise Buddy")

        #Current output
        self.img = QtGui.QImage(QtCore.QSize(noise_size, noise_size), QtGui.QImage.Format.Format_RGB888)
        self.noise_display = QtWidgets.QLabel()
        self.noise_display.setPixmap(QtGui.QPixmap(self.img))

        #Individual layers
        self.noise_layers = []

        layout = QtWidgets.QVBoxLayout()
        noisesLayout = QtWidgets.QHBoxLayout()
        noisesLayout.addWidget(self.noise_display)

        self.layersScroll = QtWidgets.QScrollArea()
        self.layersWidget = QtWidgets.QWidget()
        self.scrollVBox = QtWidgets.QVBoxLayout()

        #Scroll view setup
        self.layersScroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.layersScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.layersScroll.setFixedHeight(noise_size)
        self.layersScroll.setWidgetResizable(True)

        self.layersWidget.setLayout(self.scrollVBox)

        self.layersScroll.setWidget(self.layersWidget)
        
        noisesLayout.addWidget(self.layersScroll)
        
        layout.addLayout(noisesLayout)

        #Generate noise button
        self.button = QtWidgets.QPushButton("Generate Perlin")
        layout.addWidget(self.button)

        #Frequency slider
        self.frequencySlider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.frequencySlider.setMinimum(32)
        self.frequencySlider.setMaximum(128)
        layout.addWidget(self.frequencySlider)

        #Widget
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)

        self.button.clicked.connect(self.generatePerlin)

    @QtCore.Slot()
    def generatePerlin(self):

        noise = PerlinNoise()

        freqF = float(self.frequencySlider.value())
        size, freq, octs, data = noise_size, 1/freqF, 3, []

        for y in range(size):
            for x in range(size):
                v = noise.fBm(x*freq, y*freq, int(size*freq), octs)
                v = v *0.5 + 0.5
                v *= 255
                v = math.floor(v)
                data.append(int(v))
                self.img.setPixelColor(x, y, QtGui.QColor(v, v, v))

        display = NoiseLayer()
        display.showNoise(self.img, self)
        self.noise_layers.append(display)

        self.scrollVBox.addLayout(display)
        self.scrollVBox.update()
        self.displayOutput()


    def displayOutput(self):
        self.img = QtGui.QImage(QtCore.QSize(noise_size, noise_size), QtGui.QImage.Format.Format_RGB888)
        painter = QtGui.QPainter(self.img)
        for n in self.noise_layers:
            painter.setCompositionMode(n.blend_option)
            painter.setOpacity(n.opacity_slider.value() / 255.0)
            painter.drawImage(0, 0, n.img)
        
        self.noise_display.setPixmap(QtGui.QPixmap(self.img))


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    window = NoiseBuddy()
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())