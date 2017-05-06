# -- MultiImageCap.py - Panorama control module for ace-ng --
# Author:     Owen Tourlamain
# Supervisor: Dr. Laurence Tyler

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from time import sleep
from xml.etree import ElementTree as xml
import os

class Tab(QWidget):

    def __init__(self, config, strings, api, verbose):
        super().__init__()
        # Basic setup
        self.verbose = verbose
        self.config = config
        self.strings = strings
        self.api = api
        self.title = self.strings.MIT_Title
        # This holds all the information about the panorama, don't loose it
        self.panorama = Panorama()

        layout = QHBoxLayout()

        # Left hand column, deals with all the positions in the panorama
        self.positionsListBox = QListWidget()
        self.positionsListBox.currentItemChanged.connect(self.selectPosition)
        self.addPositionButton = QPushButton(self.strings.MIT_AddPosition)
        self.addPositionButton.clicked.connect(self.newPositionButton)
        self.removePositionButton = QPushButton(self.strings.MIT_RemovePosition)
        self.removePositionButton.clicked.connect(self.deletePositionButton)

        positionsButtonsLayout = QHBoxLayout()
        positionsButtonsLayout.addWidget(self.removePositionButton)
        positionsButtonsLayout.addWidget(self.addPositionButton)

        positionsLayout = QVBoxLayout()
        positionsLayout.addWidget(self.positionsListBox)
        positionsLayout.addLayout(positionsButtonsLayout)

        positionsGroup = QGroupBox(self.strings.MIT_PositionsTitle)
        positionsGroup.setLayout(positionsLayout)

        layout.addWidget(positionsGroup)

        # Central column, shows/edits the dtails for each position, plus the list of captures for each position.
        self.positionPan = QLineEdit()
        self.positionPan.setValidator(QDoubleValidator())
        self.positionPan.setEnabled(False)
        self.positionTilt = QLineEdit()
        self.positionTilt.setValidator(QDoubleValidator())
        self.positionTilt.setEnabled(False)
        self.positionName = QLineEdit()
        self.positionName.setEnabled(False)
        self.positionUpdateButton = QPushButton(self.strings.MIT_Update)
        self.positionUpdateButton.clicked.connect(self.updatePosition)
        self.positionUpdateButton.setEnabled(False)

        self.capturesListBox = QListWidget()
        self.capturesListBox.currentItemChanged.connect(self.selectCapture)
        self.capturesListBox.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.addCaptureButton = QPushButton(self.strings.MIT_AddCapture)
        self.addCaptureButton.clicked.connect(self.newCaptureButton)
        self.addCaptureButton.setEnabled(False)
        self.removeCaptureButton = QPushButton(self.strings.MIT_RemoveCapture)
        self.removeCaptureButton.clicked.connect(self.deleteCaptureButton)
        self.removeCaptureButton.setEnabled(False)

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

        positionFormLayout.addRow(self.strings.MIT_Name, self.positionName)
        positionFormLayout.addRow(self.strings.MIT_Pan, self.positionPan)
        positionFormLayout.addRow(self.strings.MIT_Tilt, self.positionTilt)
        positionFormLayout.addRow(self.positionUpdateButton)

        positionDetailsLayout.addLayout(positionFormLayout)
        positionDetailsLayout.addWidget(capturesGroup)

        positionDetailsGroup = QGroupBox(self.strings.MIT_PositionsDetailsTitle)
        positionDetailsGroup.setLayout(positionDetailsLayout)

        layout.addWidget(positionDetailsGroup)

        # Right hand column, shows/edits details for each capture, plus the all important go button.
        self.captureName = QLineEdit()
        self.captureName.setEnabled(False)

        self.cameraTypeComboBox = QComboBox()
        self.cameraTypeComboBox.currentIndexChanged.connect(self.updateFilters)
        self.cameraTypeComboBox.setEnabled(False)
        self.cameraTypeComboBox.setEnabled(False)

        self.filterComboBox = QComboBox()
        self.filterComboBox.setEnabled(False)

        self.captureAeMode = QComboBox()
        self.captureAeMode.currentIndexChanged.connect(self.updateAeMode)
        self.captureAeMode.setEnabled(False)

        self.captureAeAlg = QComboBox()
        self.captureAeAlg.addItems(self.config.AeAlgs)
        self.captureAeAlg.setEnabled(False)

        self.captureAeTarget = QLineEdit()
        self.captureAeTarget.setValidator(QDoubleValidator())
        self.captureAeTarget.setEnabled(False)

        self.captureAeTol = QLineEdit()
        self.captureAeTol.setValidator(QDoubleValidator())
        self.captureAeTol.setEnabled(False)

        self.captureAeMax = QLineEdit()
        self.captureAeMax.setValidator(QDoubleValidator())
        self.captureAeMax.setEnabled(False)

        self.captureAeMin = QLineEdit()
        self.captureAeMin.setValidator(QDoubleValidator())
        self.captureAeMin.setEnabled(False)

        self.captureAeRate = QLineEdit()
        self.captureAeRate.setValidator(QDoubleValidator())
        self.captureAeRate.setEnabled(False)

        self.captureGain = QLineEdit()
        self.captureGain.setValidator(QIntValidator())
        self.captureGain.setEnabled(False)

        self.captureShutter = QLineEdit()
        self.captureShutter.setValidator(QDoubleValidator())
        self.captureShutter.setEnabled(False)

        self.captureExposure = QLineEdit()
        self.captureExposure.setValidator(QDoubleValidator())
        self.captureExposure.setEnabled(False)

        self.captureMetering = QComboBox()
        self.captureMetering.currentIndexChanged.connect(self.updateMetering)
        self.captureMetering.setEnabled(False)

        self.captureRoiX = QLineEdit()
        self.captureRoiX.setValidator(QDoubleValidator())
        self.captureRoiX.setEnabled(False)

        self.captureRoiY = QLineEdit()
        self.captureRoiY.setValidator(QDoubleValidator())
        self.captureRoiY.setEnabled(False)

        self.captureRoiWidth = QLineEdit()
        self.captureRoiWidth.setValidator(QDoubleValidator())
        self.captureRoiWidth.setEnabled(False)

        self.captureRoiHeight = QLineEdit()
        self.captureRoiHeight.setValidator(QDoubleValidator())
        self.captureRoiHeight.setEnabled(False)

        self.captureUpdateButton = QPushButton(self.strings.MIT_Update)
        self.captureUpdateButton.clicked.connect(self.updateCapture)
        self.captureUpdateButton.setEnabled(False)

        captureDetailsLayout = QFormLayout()
        captureDetailsLayout.addRow(self.strings.MIT_Name, self.captureName)
        captureDetailsLayout.addRow(self.strings.MIT_CameraType, self.cameraTypeComboBox)
        captureDetailsLayout.addRow(self.strings.MIT_Filter, self.filterComboBox)
        captureDetailsLayout.addRow(self.strings.MIT_Shutter, self.captureShutter)
        captureDetailsLayout.addRow(self.strings.MIT_Exposure, self.captureExposure)
        captureDetailsLayout.addRow(self.strings.MIT_Gain, self.captureGain)
        captureDetailsLayout.addRow(self.strings.MIT_AeMode, self.captureAeMode)

        captureAeLayout = QFormLayout()
        captureAeLayout.addRow(self.strings.MIT_AeAlg, self.captureAeAlg)
        captureAeLayout.addRow(self.strings.MIT_AeTarget, self.captureAeTarget)
        captureAeLayout.addRow(self.strings.MIT_AeTol, self.captureAeTol)
        captureAeLayout.addRow(self.strings.MIT_AeMax, self.captureAeMax)
        captureAeLayout.addRow(self.strings.MIT_AeMin, self.captureAeMin)
        captureAeLayout.addRow(self.strings.MIT_AeRate, self.captureAeRate)
        self.captureAeGroup = QGroupBox(self.strings.MIT_Ae)
        self.captureAeGroup.setLayout(captureAeLayout)
        self.captureAeGroup.setHidden(True)
        captureDetailsLayout.addWidget(self.captureAeGroup)
        captureDetailsLayout.addRow(self.strings.MIT_MeteringMode, self.captureMetering)
        captureMeteringLayout = QFormLayout()
        captureMeteringLayout.addRow(self.strings.MIT_RoiX, self.captureRoiX)
        captureMeteringLayout.addRow(self.strings.MIT_RoiY, self.captureRoiY)
        captureMeteringLayout.addRow(self.strings.MIT_RoiWidth, self.captureRoiWidth)
        captureMeteringLayout.addRow(self.strings.MIT_RoiHeight, self.captureRoiHeight)
        self.captureMeteringGroup = QGroupBox(self.strings.MIT_Metering)
        self.captureMeteringGroup.setLayout(captureMeteringLayout)
        self.captureMeteringGroup.setHidden(True)
        captureDetailsLayout.addWidget(self.captureMeteringGroup)

        captureDetailsLayout.addRow(self.captureUpdateButton)

        captureDetailsGroup = QGroupBox(self.strings.MIT_CaptureDetailsTitle)
        captureDetailsGroup.setLayout(captureDetailsLayout)

        self.saveButton = QPushButton(self.strings.MIT_Save)
        self.saveButton.clicked.connect(self.saveSettings)
        self.loadButton = QPushButton(self.strings.MIT_Load)
        self.loadButton.clicked.connect(self.loadSettings)
        self.startButton = QPushButton(self.strings.MIT_Start)
        self.startButton.clicked.connect(self.capturePanorama)

        controlsLayout = QHBoxLayout()
        controlsLayout.addWidget(self.saveButton)
        controlsLayout.addWidget(self.loadButton)
        controlsLayout.addWidget(self.startButton)

        controlsGroup = QGroupBox(self.strings.MIT_ControlsTitle)
        controlsGroup.setLayout(controlsLayout)
        controlsGroup.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        captureSaveLayout = QVBoxLayout()
        captureSaveLayout.addWidget(captureDetailsGroup, stretch=1)
        captureSaveLayout.addWidget(controlsGroup)

        layout.addLayout(captureSaveLayout)

        self.setLayout(layout)

    def updateAeMode(self, current):
        if current == 1:
            self.captureAeGroup.setHidden(False)
        else:
            self.captureAeGroup.setHidden(True)

    def updateMetering(self, current):
        if current == 1:
            self.captureMeteringGroup.setHidden(False)
        else:
            self.captureMeteringGroup.setHidden(True)

    def newPositionButton(self):
        dialog = PositionDialog(self.strings)
        ret = dialog.call()
        if ret == None:
            # User cancelled the dialog
            return
        #                            Pan     Tilt    Name
        position = PanoramaPosition(ret[0], ret[1], ret[2])
        # Throw away duplicates
        if position in self.panorama.positions:
            message = QMessageBox()
            message.setText(self.strings.MIT_PositionExists)
            message.exec()
            return
        # Add to the panorama, and the list box
        self.panorama.add(position)
        index = self.panorama.getIndex(position)
        self.positionsListBox.insertItem(index, position)

    def newCaptureButton(self):
        currentItems = self.positionsListBox.selectedItems()
        if currentItems == []:
            # User cancelled the dialog
            return
        dialog = CaptureDialog(self.strings)
        ret = dialog.call()
        if ret == None:
            return
        capture = Capture(ret)
        # Throw away duplicates
        if capture in self.currentPosition.captures:
            message = QMessageBox()
            message.setText(self.strings.MIT_CaptureExists)
            message.exec()
            return
        self.currentPosition.captures.append(capture)
        self.capturesListBox.addItem(capture)

    def deletePositionButton(self):
        # Cheack we have something selceted, we can't delete nothing can we?
        currentItems = self.positionsListBox.selectedItems()
        if currentItems == []:
            return
        # Pretty sure this can only contain one item, but I'm sure someone will find a way to multi-select
        for item in currentItems:
            # Remove the item from both the panorama, and the list box
            row = self.positionsListBox.row(item)
            self.positionsListBox.takeItem(row)
            self.panorama.remove(item)
        # Blank the rest of the form so it doesnt have ghost data floating around
        self.blankPosition()
        self.blankCapture()

    def deleteCaptureButton(self):
        # Again, check we have something
        currentItems = self.capturesListBox.selectedItems()
        if currentItems == []:
            return
        for item in currentItems:
            row = self.capturesListBox.row(item)
            self.capturesListBox.takeItem(row)
            self.currentPosition.captures.remove(item)
        # Blank the right hand panel
        self.blankCapture()

    def selectPosition(self, currentItem, previousItem):
        # Do nothing if we have nothing
        if not currentItem:
            return
        self.positionPan.setText(str(currentItem.pan))
        self.positionTilt.setText(str(currentItem.tilt))
        self.positionName.setText(currentItem.name)
        # Blank the list box before we add new items, we can't use clear(),
        # Qt has a hissy fit about deleted objects if we do (even though they arent deleted)
        for row in range(self.capturesListBox.count()):
            self.capturesListBox.takeItem(0)
        for capture in currentItem.captures:
            self.capturesListBox.addItem(capture)
        # Save for later
        self.currentPosition = currentItem
        # Make the buttons work
        self.positionName.setEnabled(True)
        self.positionTilt.setEnabled(True)
        self.positionPan.setEnabled(True)
        self.positionUpdateButton.setEnabled(True)
        self.addCaptureButton.setEnabled(True)
        self.removeCaptureButton.setEnabled(True)
        # Blank the right hand panel
        self.blankCapture()

    def selectCapture(self, currentItem, previousItem):
        # Do nothing if we have nothing
        if not currentItem:
            return
        self.captureName.setText(currentItem.name)
        # Save for later
        self.currentCapture = currentItem
        self.updateFilters(currentItem.camera)
        # Make the buttons work
        self.captureName.setEnabled(True)
        self.cameraTypeComboBox.clear()
        self.cameraTypeComboBox.addItems(self.config.cameras)
        self.cameraTypeComboBox.setCurrentText(self.config.cameras[currentItem.camera])
        self.cameraTypeComboBox.setEnabled(True)
        self.filterComboBox.setEnabled(True)
        self.captureAeMode.setEnabled(True)
        self.captureAeAlg.setEnabled(True)
        self.captureAeTarget.setEnabled(True)
        self.captureAeTol.setEnabled(True)
        self.captureAeMax.setEnabled(True)
        self.captureAeMin.setEnabled(True)
        self.captureAeRate.setEnabled(True)
        self.captureGain.setEnabled(True)
        self.captureShutter.setEnabled(True)
        self.captureExposure.setEnabled(True)
        self.captureMetering.setEnabled(True)
        self.captureRoiX.setEnabled(True)
        self.captureRoiY.setEnabled(True)
        self.captureRoiWidth.setEnabled(True)
        self.captureRoiHeight.setEnabled(True)
        self.captureUpdateButton.setEnabled(True)
        self.captureMetering.addItems(self.config.Metering)
        self.captureAeMode.addItems(self.config.AeModes)

    def updatePosition(self):
        # Ignore duplicates, need to make a whole item to compare to
        tmpPosition = PanoramaPosition(float(self.positionPan.text()), float(self.positionTilt.text()), "")
        if tmpPosition in self.panorama.positions:
            message = QMessageBox()
            message.setText(self.strings.MIT_PositionExists)
            message.exec()
            return
        self.currentPosition.pan = float(self.positionPan.text())
        self.currentPosition.tilt = float(self.positionTilt.text())
        self.currentPosition.name = self.positionName.text()
        # Make sure we can actually see these changes
        self.currentPosition.updateText()

    def updateCapture(self):
        # Ignore duplicates, need to make a whole item to compare to
        if self.captureName.text() != self.currentCapture.name:
            tmpCapture = Capture(self.captureName.text())
            if tmpCapture in self.currentPosition.captures:
                message = QMessageBox()
                message.setText(self.strings.MIT_CaptureExists)
                message.exec()
                return
        self.currentCapture.name = self.captureName.text()
        self.currentCapture.camera = self.cameraTypeComboBox.currentIndex()
        self.currentCapture.filter = self.filterComboBox.currentIndex()
        self.currentCapture.gain = self.blankInt(self.captureGain.text())
        self.currentCapture.shutter = self.blankFloat(self.captureShutter.text())
        self.currentCapture.shutter_target = self.blankFloat(self.captureExposure.text())
        roi = (
            self.blankInt(self.captureRoiX.text()),
            self.blankInt(self.captureRoiY.text()),
            self.blankInt(self.captureRoiWidth.text()),
            self.blankInt(self.captureRoiHeight.text())
        )
        self.currentCapture.roi = roi
        self.currentCapture.aeMode = self.captureAeMode.currentIndex()
        self.currentCapture.aeAlg = self.captureAeAlg.currentIndex()
        self.currentCapture.aeTarget = self.blankFloat(self.captureAeTarget.text())
        self.currentCapture.aeTol = self.blankFloat(self.captureAeTol.text())
        self.currentCapture.aeMax = self.blankFloat(self.captureAeMax.text())
        self.currentCapture.aeMin = self.blankFloat(self.captureAeMin.text())
        self.currentCapture.aeRate = self.blankFloat(self.captureAeRate.text())
        # Make sure we can actually see these changes
        self.currentCapture.updateText()

    def blankInt(self, val):
        if val == "":
            return 0
        else:
            return int(val)

    def blankFloat(self, val):
        if val == "":
            return 0.0
        else:
            return float(val)

    def blankPosition(self):
        # Disable these items so it's obvious they don't do anything for now
        for row in range(self.capturesListBox.count()):
            self.capturesListBox.takeItem(0)
        self.positionName.setText("")
        self.positionName.setEnabled(False)
        self.positionTilt.setText("")
        self.positionTilt.setEnabled(False)
        self.positionPan.setText("")
        self.positionPan.setEnabled(False)
        self.addCaptureButton.setEnabled(False)
        self.removeCaptureButton.setEnabled(False)
        self.positionUpdateButton.setEnabled(False)

    def blankCapture(self):
        # Disable these items so it's obvious they don't do anything for now
        self.captureName.setText("")
        self.captureName.setEnabled(False)
        self.cameraTypeComboBox.clear()
        self.cameraTypeComboBox.setEnabled(False)
        self.filterComboBox.clear()
        self.filterComboBox.setEnabled(False)
        self.captureAeMode.setEnabled(False)
        self.captureAeAlg.setEnabled(False)
        self.captureAeTarget.setEnabled(False)
        self.captureAeTol.setEnabled(False)
        self.captureAeMax.setEnabled(False)
        self.captureAeMin.setEnabled(False)
        self.captureAeRate.setEnabled(False)
        self.captureGain.setEnabled(False)
        self.captureShutter.setEnabled(False)
        self.captureExposure.setEnabled(False)
        self.captureMetering.setEnabled(False)
        self.captureRoiX.setEnabled(False)
        self.captureRoiY.setEnabled(False)
        self.captureRoiWidth.setEnabled(False)
        self.captureRoiHeight.setEnabled(False)
        self.captureUpdateButton.setEnabled(False)
        self.captureAeGroup.setHidden(True)
        self.captureMeteringGroup.setHidden(True)
        self.captureAeMode.clear()
        self.captureMetering.clear()

    def updateFilters(self, index):
        # Qt doesn't mind if we use clear() here, still no clue why thats an issue,
        # and I'm definitely not bitter
        self.filterComboBox.clear()
        if index == 0: # 0 = LWAC
            self.filterComboBox.addItems(self.config.LWACFilters)
            self.filterComboBox.setCurrentText(self.config.LWACFilters[self.currentCapture.filter])
            self.filterComboBox.setEnabled(True)
        elif index == 1: # 1 = RWAC
            self.filterComboBox.addItems(self.config.RWACFilters)
            self.filterComboBox.setCurrentText(self.config.RWACFilters[self.currentCapture.filter])
            self.filterComboBox.setEnabled(True)
        else: # 3 = HRC (No filters)
            self.filterComboBox.setEnabled(False)

    def capturePanorama(self):
        # Get a path to save into
        dialog = PathDialog(self.strings)
        self.panorama.path = dialog.call()
        if self.panorama.path == None:
            return
        # We cant capture an empty panorama
        if len(self.panorama) == 0:
            message = QMessageBox()
            message.setText(self.strings.MIT_NoPositions)
            message.exec()
            return
        # We also can't capture a panorama if some of the positions are empty
        for position in self.panorama.positions:
            if len(position.captures) == 0:
                message = QMessageBox()
                message.setText(self.strings.MIT_EmptyPositions)
                message.exec()
                return

        dialog = CapturePanorama(self.strings, self.api, self.panorama)
        dialog.call()

    def saveSettings(self):
        file = QFileDialog.getSaveFileName(self, self.strings.MIT_SaveFile, os.path.expanduser("~"), "%s (*.pan)" % self.strings.MIT_Panoramas)
        if file[0]:
            saver = PanoramaSaver()
            saver.dump(self.panorama, file[0])

    def loadSettings(self):
        file = QFileDialog.getOpenFileName(self, self.strings.MIT_LoadFile, os.path.expanduser("~"), "%s (*.pan)" % self.strings.MIT_Panoramas)
        if file[0]:
            saver = PanoramaSaver()
            self.panorama = saver.load(file[0])
            # Panorama is loaded, but we need to refresh the GUI, again, can't use clear()
            for row in range(self.positionsListBox.count()):
                self.positionsListBox.takeItem(0)
            for position in self.panorama.positions:
                self.positionsListBox.addItem(position)
            self.blankPosition()
            self.blankCapture()

class PanoramaSaver(object):

    def __init__(self):
        super(PanoramaSaver, self).__init__()

    def dump(self, panorama, file):
        xmlRoot = xml.Element("root")
        for position in panorama.positions:
            attributes = dict(
                name=position.name,
                pan=str(position.pan),
                tilt=str(position.tilt)
            )
            xmlPosition = xml.Element("position", attrib=attributes)
            for capture in position.captures:
                (croix, croiy, croiw, croih) = capture.roi
                capAttributes = dict(
                    name=capture.name,
                    camera=str(capture.camera),
                    filter=str(capture.filter),
                    gain = str(capture.gain),
                    shutter = str(capture.shutter),
                    shutter_target = str(capture.shutter_target),
                    roix = str(croix),
                    roiy = str(croiy),
                    roiw = str(croiw),
                    roih = str(croih),
                    aeMode = str(capture.aeMode),
                    aeAlg = str(capture.aeAlg),
                    aeTarget = str(capture.aeTarget),
                    aeTol = str(capture.aeTol),
                    aeMax = str(capture.aeMax),
                    aeMin = str(capture.aeMin),
                    aeRate = str(capture.aeRate),
                )
                xmlCapture = xml.Element("capture", attrib=capAttributes)
                xmlPosition.append(xmlCapture)
            xmlRoot.append(xmlPosition)
        tree = xml.ElementTree(xmlRoot)
        tree.write(file)

    def load(self, file):
        panorama = Panorama()
        tree = xml.parse(file)
        xmlRoot = tree.getroot()
        for xmlPosition in xmlRoot.iter("position"):
            pan = float(xmlPosition.get("pan"))
            tilt = float(xmlPosition.get("tilt"))
            name = xmlPosition.get("name")
            position = PanoramaPosition(pan, tilt, name)
            for xmlCapture in xmlPosition.iter("capture"):
                name = xmlCapture.get("name")
                camera = int(xmlCapture.get("camera"))
                filter = int(xmlCapture.get("filter"))
                gain = int(xmlCapture.get("filter"))
                shutter = float(xmlCapture.get("filter"))
                shutter_target = float(xmlCapture.get("filter"))
                roix = int(xmlCapture.get("filter"))
                roiy = int(xmlCapture.get("filter"))
                roiw = int(xmlCapture.get("filter"))
                roih = int(xmlCapture.get("filter"))
                aeMode = float(xmlCapture.get("filter"))
                aeAlg = float(xmlCapture.get("filter"))
                aeTarget = float(xmlCapture.get("filter"))
                aeTol = float(xmlCapture.get("filter"))
                aeMax = float(xmlCapture.get("filter"))
                aeMin = float(xmlCapture.get("filter"))
                aeRate = float(xmlCapture.get("filter"))
                capture = Capture(name, camera, filter, gain, shutter, shutter_target,
                                  roix, roiy, roiw, roih, aeMode, aeAlg, aeTarget,
                                  aeTol, aeMax, aeMin, aeRate)
                position.captures.append(capture)
            panorama.add(position)
        return panorama

class PositionDialog(QDialog):

    def __init__(self, strings):
        super(PositionDialog, self).__init__()

        self.pan = QLineEdit()
        self.pan.setValidator(QDoubleValidator())
        self.tilt = QLineEdit()
        self.tilt.setValidator(QDoubleValidator())
        self.name = QLineEdit()
        self.name.setPlaceholderText(strings.MIT_Optional)
        okButton = QPushButton(strings.MIT_Ok)
        okButton.setDefault(True)
        okButton.clicked.connect(self.check)

        self.setWindowTitle(strings.MIT_PositionDialog)
        self.setWindowModality(Qt.ApplicationModal)

        layout = QFormLayout()
        layout.addRow(strings.MIT_Name, self.name)
        layout.addRow(strings.MIT_Pan, self.pan)
        layout.addRow(strings.MIT_Tilt, self.tilt)
        layout.addRow(okButton)

        self.setLayout(layout)

    def call(self):
        response = self.exec_()
        if response:
            # We can't return a tuple because the dialog will just return None if it is closed, so a list it is
            return [float(self.pan.text()), float(self.tilt.text()), self.name.text()]

    def check(self):
        # Make sure we actually have enough data to make a position
        if self.pan.text() and self.tilt.text():
            self.accept()

class CaptureDialog(QDialog):

    def __init__(self, strings):
        super(CaptureDialog, self).__init__()

        self.name = QLineEdit()
        okButton = QPushButton(strings.MIT_Ok)
        okButton.setDefault(True)
        okButton.clicked.connect(self.check)

        self.setWindowTitle(strings.MIT_CaptureDialog)
        self.setWindowModality(Qt.ApplicationModal)

        layout = QFormLayout()
        layout.addRow(strings.MIT_Name, self.name)
        layout.addRow(okButton)

        self.setLayout(layout)

    def call(self):
        response = self.exec_()
        if response:
            return self.name.text()

    def check(self):
        # Make sure we actually have enough data to make a capture
        if self.name.text():
            self.accept()

class PathDialog(QDialog):

    def __init__(self, strings):
        super(PathDialog, self).__init__()
        self.strings = strings

        self.path = QLineEdit(os.path.expanduser("~"))
        okButton = QPushButton(strings.MIT_Ok)
        okButton.setDefault(True)
        okButton.clicked.connect(self.check)

        self.setWindowTitle(strings.MIT_PathDialog)
        self.setWindowModality(Qt.ApplicationModal)

        layout = QFormLayout()
        layout.addRow(strings.MIT_Path, self.path)
        layout.addRow(okButton)

        self.setLayout(layout)

    def call(self):
        response = self.exec_()
        if response:
            return self.path.text()

    def check(self):
        # Make sure we have a valid path, and create it if it doesn't exist
        if os.path.isdir(self.path.text()):
            self.accept()
        else:
            try:
                os.makedirs(self.path.text())
                self.accept()
            except OSError:
                message = QMessageBox()
                message.setText(self.strings.MIT_InvalidPath)
                message.exec()


class CapturePanorama(QDialog):

    def __init__(self, strings, api, panorama):
        super(CapturePanorama, self).__init__()
        self.strings = strings
        self.api = api
        self.panorama = panorama
        # Used so we can fill up the progress bar correctly
        self.total = self.computeTotal()
        self.step = 100 / self.total
        self.current = 0

        self.infoLabel = QLabel()
        self.progress = QProgressBar()
        self.cancel = QPushButton(self.strings.MIT_Cancel)
        self.cancel.clicked.connect(self.reject)

        self.setWindowTitle(strings.MIT_CapturePanorama)
        self.setWindowModality(Qt.ApplicationModal)

        layout = QVBoxLayout()
        layout.addWidget(self.infoLabel)
        layout.addWidget(self.progress)
        layout.addWidget(self.cancel)

        self.setLayout(layout)

    def call(self):
        self.show()
        # Move to each position, then take all the captures neded processEvents() allows the GUI to update
        for position in self.panorama.positions:
            QApplication.processEvents()
            self.infoLabel.setText("%s %s" % (self.strings.MIT_MovingTo, position))
            QApplication.processEvents()
            self.moveTo(position)
            self.current += self.step
            self.progress.setValue(self.current)
            QApplication.processEvents()
            for capture in position.captures:
                QApplication.processEvents()
                self.infoLabel.setText("%s %s" % (self.strings.MIT_Capturing, capture))
                QApplication.processEvents()
                self.capture(capture, position)
                self.current += self.step
                self.progress.setValue(self.current)
                QApplication.processEvents()
        self.infoLabel.setText(self.strings.MIT_Done)
        self.cancel.setText(self.strings.MIT_Close)
        self.progress.setValue(100)
        # This stops the dialog closing automatically when done
        self.exec_()

    def moveTo(self, position):
        self.api.pancam.ptu.pan = position.pan
        self.api.pancam.ptu.tilt = position.tilt

    def capture(self, capture, position):
        camera = self.api.pancam.cameras[capture.camera]
        camera.filter = capture.filter
        camera.gain = capture.gain
        camera.shutter = capture.shutter
        camera.shutter_target = capture.shutter_target
        if capture.roi[2] and capture.roi[3]:
            camera.ae_meter_region = 1
            camera.roi = capture.roi
        else:
            camera.ae_meter_region = 0

        if capture.aeMode == 0:
            serverAE = False
            camera.shutter_mode = 0
        elif capture.aeMode == 1:
            serverAE = True
            camera.shutter_mode = 0
        else:
            serverAE = False
            camera.shutter_mode = 1

        ##self.aeAlg = capture.aeAlg ask!!
        camera.ae_target = capture.aeTarget
        camera.ae_tolerance = capture.aeTol
        camera.ae_max_shutter = capture.aeMax
        camera.ae_min_shutter = capture.aeMin
        camera.ae_adjust_rate = capture.aeRate

        image = camera.get_image(ae=serverAE)
        # Create a file/folder structure to store the images
        fileName = "%s_%d_%d.png" % (capture.name, capture.camera, capture.filter)
        if not os.path.isdir(os.path.join(self.panorama.path, str(position))):
            os.makedirs(os.path.join(self.panorama.path, str(position)))
        image.save_png_with_metadata(os.path.join(self.panorama.path, str(position), fileName))

    def computeTotal(self):
        total = 0
        total += len(self.panorama)
        for position in self.panorama.positions:
            total += len(position.captures)
        return total

class Panorama(object):

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

    def remove(self, item):
        if item in self.positions:
            self.positions.remove(item)

    def getIndex(self, item):
        if item in self.positions:
            return self.positions.index(item)
        else:
            return -1

    def __str__(self):
        string = ""
        for position in self.positions:
            string += "%s\n" % str(position)
        return string

    def sort(self):
        # We need to make sure we put the least strain on the PTU as possible,
        # so we order the positions from top left to bottom right
        self.positions.sort(reverse=True, key=lambda pos: pos.pan)
        self.positions.sort(reverse=True, key=lambda pos: pos.tilt)

class PanoramaPosition(QListWidgetItem):

    def __init__(self, pan, tilt, name):
        super(PanoramaPosition, self).__init__()
        self.pan = pan
        self.tilt = tilt
        self.name = name
        self.captures = []
        self.updateText()

    def updateText(self):
        self.setText(str(self))

    def __lt__(self, other):
        return self.pan > other.pan and self.tilt >= other.tilt

    def __str__(self):
        if self.name:
            return self.name
        else:
            return "(%.1f,%.1f)" % (self.pan, self.tilt)

    def __eq__(self, other):
        return self.pan == other.pan and self.tilt == other.tilt

class Capture(QListWidgetItem):

    def __init__(self, name, camera=0, filter=0, gain=0.0, shutter=0.0,
                 shutter_target=0.0, roix=0, roiy=0, roiw=0, roih=0, aeMode=0,
                 aeAlg=0, aeTarget=0.0, aeTol=0.0, aeMax=0.0, aeMin=0.0, aeRate=0.0):
        super(Capture, self).__init__()
        self.name = name
        self.camera = camera
        self.filter = filter
        self.gain = gain
        self.shutter = shutter
        self.shutter_target = shutter_target
        self.roi = (roix, roiy, roiw, roih)
        self.aeMode = aeMode
        self.aeAlg = aeAlg
        self.aeTarget = aeTarget
        self.aeTol = aeTol
        self.aeMax = aeMax
        self.aeMin = aeMin
        self.aeRate = aeRate

        self.updateText()

    def updateText(self):
        self.setText(str(self))

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name
