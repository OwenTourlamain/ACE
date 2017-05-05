# -- SingleImageCap.py - Camera control and image capture module for ace-ng --
# Author:     Owen Tourlamain
# Supervisor: Dr. Laurence Tyler
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PIL.ImageQt import ImageQt
import os

class Tab(QWidget):
    """docstring for SingleImageCap."""

    def __init__(self, config, strings, api, verbose):
        super().__init__()
        self.verbose = verbose
        self.config = config
        self.strings = strings
        self.api = api
        self.title = self.strings.SIT_Title

        # Set atributes for later
        self.LWACimage = None
        self.RWACimage = None
        self.HRCimage = None

        layout = QVBoxLayout()
        imageLayout = QHBoxLayout()
        LWACControlsLayout = QVBoxLayout()
        RWACControlsLayout = QVBoxLayout()
        HRCControlsLayout = QVBoxLayout()
        controlsLayout = QHBoxLayout()

        # == LWAC ==
        self.LWACcaptureButton = QPushButton(self.strings.SIT_LWACcap, self)
        self.LWACcaptureButton.clicked.connect(self.LWACcapture)

        self.LWACsaveButton = QPushButton(self.strings.SIT_Save, self)
        self.LWACsaveButton.clicked.connect(self.LWACsave)
        self.LWACsaveButton.setDisabled(True)

        self.LWACFilterCombo = QComboBox(self)
        self.LWACFilterCombo.addItems(self.config.LWACFilters)

        self.LWACpreview = SquareLabel()
        self.LWACpreview.setStyleSheet("border: 1px solid black; padding: 2px")
        imageLayout.addWidget(self.LWACpreview)
        LWACControlsLayout.addWidget(self.LWACFilterCombo)
        LWACControlsLayout.addWidget(self.LWACcaptureButton)
        LWACControlsLayout.addWidget(self.LWACsaveButton)

        # == HRC ==
        self.HRCcaptureButton = QPushButton(self.strings.SIT_HRCcap, self)
        self.HRCcaptureButton.clicked.connect(self.HRCcapture)

        self.HRCInvisibleButton = QComboBox()
        sizePolicy = QSizePolicy()
        sizePolicy.setRetainSizeWhenHidden(True)
        self.HRCInvisibleButton.setSizePolicy(sizePolicy)
        self.HRCInvisibleButton.hide()

        self.HRCsaveButton = QPushButton(self.strings.SIT_Save, self)
        self.HRCsaveButton.clicked.connect(self.HRCsave)
        self.HRCsaveButton.setDisabled(True)

        self.HRCpreview = SquareLabel()
        self.HRCpreview.setStyleSheet("border: 1px solid black; padding: 2px")
        imageLayout.addWidget(self.HRCpreview)
        HRCControlsLayout.addWidget(self.HRCInvisibleButton)
        HRCControlsLayout.addWidget(self.HRCcaptureButton)
        HRCControlsLayout.addWidget(self.HRCsaveButton)

        # == RWAC ==
        self.RWACcaptureButton = QPushButton(self.strings.SIT_RWACcap, self)
        self.RWACcaptureButton.clicked.connect(self.RWACcapture)

        self.RWACsaveButton = QPushButton(self.strings.SIT_Save, self)
        self.RWACsaveButton.clicked.connect(self.RWACsave)
        self.RWACsaveButton.setDisabled(True)

        self.RWACFilterCombo = QComboBox(self)
        self.RWACFilterCombo.addItems(self.config.RWACFilters)

        self.RWACpreview = SquareLabel()
        self.RWACpreview.setStyleSheet("border: 1px solid black; padding: 2px")
        imageLayout.addWidget(self.RWACpreview)
        RWACControlsLayout.addWidget(self.RWACFilterCombo)
        RWACControlsLayout.addWidget(self.RWACcaptureButton)
        RWACControlsLayout.addWidget(self.RWACsaveButton)
        layout.addLayout(imageLayout)
        controlsLayout.addLayout(LWACControlsLayout)
        controlsLayout.addLayout(HRCControlsLayout)
        controlsLayout.addLayout(RWACControlsLayout)
        layout.addLayout(controlsLayout)

        rootLayout = QVBoxLayout()
        rootLayout.addLayout(layout)
        rootLayout.addStretch()
        self.setLayout(rootLayout)

    def LWACcapture(self):
        camera = self.api.pancam.cameras[0]
        camera.filter = self.LWACFilterCombo.currentIndex()
        self.LWACimage = camera.get_image()
        pixmap = QPixmap.fromImage(ImageQt(self.LWACimage.as_pil_image()).scaled(self.LWACpreview.size(), Qt.KeepAspectRatio))
        self.LWACpreview.setPixmap(pixmap)
        self.LWACsaveButton.setEnabled(True)

    def RWACcapture(self):
        camera = self.api.pancam.cameras[1]
        camera.filter = self.RWACFilterCombo.currentIndex()
        self.RWACimage = camera.get_image()
        pixmap = QPixmap.fromImage(ImageQt(self.RWACimage.as_pil_image()).scaled(self.RWACpreview.size(), Qt.KeepAspectRatio))
        self.RWACpreview.setPixmap(pixmap)
        self.RWACsaveButton.setEnabled(True)

    def HRCcapture(self):
        camera = self.api.pancam.cameras[2]
        self.HRCimage = camera.get_image()
        pixmap = QPixmap.fromImage(ImageQt(self.HRCimage.as_pil_image()).scaled(self.HRCpreview.size(), Qt.KeepAspectRatio))
        self.HRCpreview.setPixmap(pixmap)
        self.HRCsaveButton.setEnabled(True)

    def LWACsave(self):
        if self.LWACimage:
            file = QFileDialog.getSaveFileName(self, self.strings.SIT_SaveImage, os.path.expanduser("~"), "%s (*.png)" % self.strings.SIT_Images)
            if file[0]:
                self.LWACimage.save_png_with_metadata(file[0])

    def RWACsave(self):
        if self.RWACimage:
            file = QFileDialog.getSaveFileName(self, self.strings.SIT_SaveImage, os.path.expanduser("~"), "%s (*.png)" % self.strings.SIT_Images)
            if file[0]:
                self.RWACimage.save_png_with_metadata(file[0])

    def HRCsave(self):
        if self.HRCimage:
            file = QFileDialog.getSaveFileName(self, self.strings.SIT_SaveImage, os.path.expanduser("~"), "%s (*.png)" % self.strings.SIT_Images)
            if file[0]:
                self.HRCimage.save_png_with_metadata(file[0])

class SquareLabel(QLabel):
    """docstring for SquareButton."""

    def __init__(self):
        super(SquareLabel, self).__init__(text)

        sizePolicy = QSizePolicy(QSizePolicy.Ignored , QSizePolicy.Ignored)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

    def heightForWidth(self, width):
        return self.width()
