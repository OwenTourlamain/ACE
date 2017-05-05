# -- calibrate.py - colour calibration module for ace-ng --
# Author:     Owen Tourlamain
# Supervisor: Dr. Laurence Tyler
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Tab(QWidget):
    """docstring for SingleImageCap."""

    def __init__(self, config, strings, api, verbose):
        super().__init__()
        self.verbose = verbose
        self.config = config
        self.strings = strings
        self.api = api
        self.title = "Calibrate"

        calibrateButton = QPushButton("Calibrate")
        calibrateButton.clicked.connect(self.calibrate)
        layout = QVBoxLayout()
        layout.addWidget(calibrateButton)
        self.setLayout(layout)

    def calibrate(self):
        self.api.pancam.ptu.pan = 15
        self.api.pancam.ptu.tilt = -10

        Lcamera = self.api.pancam.cameras[0]
        Rcamera = self.api.pancam.cameras[1]

        for filter in range(1,4):

            Lcamera.filter = filter
            Rcamera.filter = filter

            Limage = Lcamera.get_image()
            Rimage = Rcamera.get_image()

            Limage.save_png_with_metadata("Lcalib-%d.png" % filter)
            Rimage.save_png_with_metadata("Rcalib-%d.png" % filter)

        self.api.pancam.ptu.stow()

        #RimageR = self.Rcamera.get_image()
