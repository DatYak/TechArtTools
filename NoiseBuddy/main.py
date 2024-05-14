import sys
import random
import math
from PySide6 import QtCore, QtWidgets, QtGui


noise_size = 512
perm = [*range(256)]
random.shuffle(perm)
perm += perm
dirs = [(math.cos(a * 2.0 * math.pi / 256),
        math.sin(a * 2.0 * math.pi / 256))
        for a in range(256)]

def fBm(x, y, per, octs):
    val = 0
    for o in range(octs):
        val += 0.5**o * noise(x*2**o, y*2**o, per*2**o)
    return val

def noise(x, y, per):
    def surflet(gridX, gridY):
        distX, distY = abs(x-gridX), abs(y-gridY)
        polyX = 1 - 6*distX**5 + 15*distX**4 - 10*distX**3
        polyY = 1 - 6*distY**5 + 15*distY**4 - 10*distY**3
        hashed = perm[perm[int(gridX)%per] + int(gridY)%per]
        grad = (x-gridX)*dirs[hashed][0] + (y-gridY)*dirs[hashed][1]
        return polyX * polyY * grad
    intX, intY = int(x), int(y)
    return (surflet(intX+0, intY+0) + surflet(intX+1, intY+0) +
            surflet(intX+0, intY+1) + surflet(intX+1, intY+1))



class NoiseBuddy(QtWidgets.QMainWindow):
    def __init__(self):
        super(NoiseBuddy, self).__init__()

        self.button = QtWidgets.QPushButton("Generate Perlin")
    
        self.img = QtGui.QImage(QtCore.QSize(noise_size, noise_size), QtGui.QImage.Format.Format_RGB888)

        self.noise_display = QtWidgets.QLabel()
        self.noise_display.setPixmap(QtGui.QPixmap(self.img))

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.noise_display)

        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)

        self.button.clicked.connect(self.GeneratePerlin)

    @QtCore.Slot()
    def GeneratePerlin(self):
        size, freq, octs, data = noise_size, 1/32.0, 5, []

        for y in range(size):
            for x in range(size):
                v = fBm(x*freq, y*freq, int(size*freq), octs)
                v = v *0.5 + 0.5
                v *= 255
                v = math.floor(v)
                data.append(int(v))
                self.img.setPixelColor(x, y, QtGui.QColor(v, v, v))

        self.noise_display.setPixmap(QtGui.QPixmap(self.img))

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    window = NoiseBuddy()
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())