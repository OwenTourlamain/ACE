from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Tab(QWidget): # HACK: Make class load dynamically
    """docstring for MultiImageCap."""

    def __init__(self, config, strings, api, verbose):
        super().__init__()
        self.verbose = verbose
        self.config = config
        self.strings = strings
        self.api = api
        self.title = self.strings.MIT_Title
        self.panorama = Panorama()

        self.initTab()

    def initTab(self):
        layout = QHBoxLayout()

        self.positionsListBox = QListWidget()
        self.addPositionButton = QPushButton(self.strings.MIT_AddPosition)
        self.addPositionButton.clicked.connect(self.newPositionButton)
        self.removePositionButton = QPushButton(self.strings.MIT_RemovePosition)

        positionsButtonsLayout = QHBoxLayout()
        positionsButtonsLayout.addWidget(self.removePositionButton)
        positionsButtonsLayout.addWidget(self.addPositionButton)

        positionsLayout = QVBoxLayout()
        positionsLayout.addWidget(self.positionsListBox)
        positionsLayout.addLayout(positionsButtonsLayout)

        positionsGroup = QGroupBox(self.strings.MIT_PositionsTitle)
        positionsGroup.setLayout(positionsLayout)

        layout.addWidget(positionsGroup)

        self.positionPan = QLineEdit()
        self.positionTilt = QLineEdit()

        self.capturesListBox = QListWidget()
        self.capturesListBox.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.addCaptureButton = QPushButton(self.strings.MIT_AddCapture)
        self.removeCaptureButton = QPushButton(self.strings.MIT_RemoveCapture)

        capturesButtonsLayout = QHBoxLayout()
        capturesButtonsLayout.addWidget(self.removeCaptureButton)
        capturesButtonsLayout.addWidget(self.addCaptureButton)

        capturesLayout = QVBoxLayout()
        capturesLayout.addWidget(self.capturesListBox)
        capturesLayout.addLayout(capturesButtonsLayout)

        capturesGroup = QGroupBox(self.strings.MIT_CapturesTitle)
        capturesGroup.setLayout(capturesLayout)

        positionDetailsLayout = QVBoxLayout()
        positionFormLayout = QFormLayout()

        positionFormLayout.addRow(self.strings.MIT_Pan, self.positionPan)
        positionFormLayout.addRow(self.strings.MIT_Tilt, self.positionTilt)

        positionDetailsLayout.addLayout(positionFormLayout)
        positionDetailsLayout.addWidget(capturesGroup)

        positionDetailsGroup = QGroupBox(self.strings.MIT_PositionsDetailsTitle)
        positionDetailsGroup.setLayout(positionDetailsLayout)

        layout.addWidget(positionDetailsGroup)

        self.cameraTypeComboBox = QComboBox()

        self.filterComboBox = QComboBox()

        captureDetailsLayout = QFormLayout()
        captureDetailsLayout.addRow(self.strings.MIT_CameraType, self.cameraTypeComboBox)
        captureDetailsLayout.addRow(self.strings.MIT_Filter, self.filterComboBox)

        captureDetailsGroup = QGroupBox(self.strings.MIT_CaptureDetailsTitle)
        captureDetailsGroup.setLayout(captureDetailsLayout)

        self.saveButton = QPushButton(self.strings.MIT_Save)
        self.loadButton = QPushButton(self.strings.MIT_Load)

        saveLoadLayout = QHBoxLayout()
        saveLoadLayout.addWidget(self.saveButton)
        saveLoadLayout.addWidget(self.loadButton)

        saveLoadGroup = QGroupBox(self.strings.MIT_SaveLoadTitle)
        saveLoadGroup.setLayout(saveLoadLayout)
        saveLoadGroup.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        captureSaveLayout = QVBoxLayout()
        captureSaveLayout.addWidget(captureDetailsGroup, stretch=1)
        captureSaveLayout.addWidget(saveLoadGroup)

        layout.addLayout(captureSaveLayout)

        self.setLayout(layout)

        self.panorama = Panorama()

    def newPositionButton(self):
        dialog = PositionDialog(self.strings)
        panTilt = dialog.call()
        if panTilt == None:
            return
        position = PanoramaPosition(panTilt[0], panTilt[1])
        if position in self.panorama.positions:
            return # TODO: Popup error
        self.panorama.add(position)
        self.updatePositionList()

    def updatePositionList(self):
        self.positionsListBox.clear()
        for position in self.panorama.positions:
            self.positionsListBox.addItem(str(position))

class PositionDialog(QDialog):
    """docstring for PositionDialog."""
    def __init__(self, strings):
        super(PositionDialog, self).__init__()

        self.pan = QLineEdit()
        self.pan.setValidator(QDoubleValidator())
        self.tilt = QLineEdit()
        self.tilt.setValidator(QDoubleValidator())
        okButton = QPushButton(strings.MIT_Ok)
        okButton.setDefault(True)
        okButton.clicked.connect(self.check)

        self.setWindowTitle(strings.MIT_PositionDialog)
        self.setWindowModality(Qt.ApplicationModal)

        layout = QFormLayout()
        layout.addRow(strings.MIT_Pan, self.pan)
        layout.addRow(strings.MIT_Tilt, self.tilt)
        layout.addRow(okButton)

        self.setLayout(layout)

    def call(self):
        response = self.exec_()
        if response:
            return [float(self.pan.text()), float(self.tilt.text())]

    def check(self):
        if self.pan.text() and self.tilt.text():
            self.accept()

    def reject(self):
        QDialog.reject(self,None, None)

class Panorama(object):
    """docstring for Panorama."""
    def __init__(self):
        super(Panorama, self).__init__()

        self.positions = []

    def __getitem__(self, item):
        if item < len(self):
            raise IndexError("Index out of range")
        return self.positions[item]

    def __len__(self):
        return len(self.positions)

    def add(self, item):
        if not isinstance(item, PanoramaPosition):
            raise ValueError("Panoramas can only contain PanoramaPositions")
        self.positions.append(item)
        self.sort()

    def __str__(self):
        string = ""
        for position in self.positions:
            string += "%s\n" % str(position)
        return string

    def sort(self):
        self.positions.sort(reverse=True, key=lambda pos: pos.pan)
        self.positions.sort(reverse=True, key=lambda pos: pos.tilt)

class PanoramaPosition(QListWidgetItem):
    """docstring for PanoramaPosition."""
    def __init__(self, pan, tilt):
        super(PanoramaPosition, self).__init__()
        self.pan = pan
        self.tilt = tilt
        self.captures = []

    def __lt__(self, other):
        return self.pan > other.pan and self.tilt >= other.tilt

    def __str__(self):
        return "(%.1f,%.1f)" % (self.pan, self.tilt)

    def __eq__(self, other):
        return self.pan == other.pan and self.tilt == other.tilt
