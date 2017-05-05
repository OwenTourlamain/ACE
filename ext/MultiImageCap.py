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
    """docstring for MultiImageCap."""

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
        self.filterComboBox = QComboBox()
        self.filterComboBox.setEnabled(False)
        self.captureUpdateButton = QPushButton(self.strings.MIT_Update)
        self.captureUpdateButton.clicked.connect(self.updateCapture)
        self.captureUpdateButton.setEnabled(False)

        captureDetailsLayout = QFormLayout()
        captureDetailsLayout.addRow(self.strings.MIT_Name, self.captureName)
        captureDetailsLayout.addRow(self.strings.MIT_CameraType, self.cameraTypeComboBox)
        captureDetailsLayout.addRow(self.strings.MIT_Filter, self.filterComboBox)
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
        self.captureUpdateButton.setEnabled(True)

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
        # Make sure we can actually see these changes
        self.currentCapture.updateText()

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
        self.captureUpdateButton.setEnabled(False)

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
    """docstring for PanoramaSaver."""
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
                capAttributes = dict(
                    name=capture.name,
                    camera=str(capture.camera),
                    filter=str(capture.filter)
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
                capture = Capture(name, camera, filter)
                position.captures.append(capture)
            panorama.add(position)
        return panorama


class PositionDialog(QDialog):
    """docstring for PositionDialog."""
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
    """docstring for CaptureDialog."""
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
    """docstring for CaptureDialog."""
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
    """docstring for CapturePanorama."""
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
        # This stops the dialog closing automatically when done
        self.exec_()

    def moveTo(self, position):
        self.api.pancam.ptu.pan = position.pan
        self.api.pancam.ptu.tilt = position.tilt

    def capture(self, capture, position):
        camera = self.api.pancam.cameras[capture.camera]
        camera.filter = capture.filter
        image = camera.get_image()
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
    """docstring for PanoramaPosition."""
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
    """docstring for Capture."""
    def __init__(self, name, camera=0, filter=0):
        super(Capture, self).__init__()
        self.name = name
        self.camera = camera
        self.filter = filter
        self.updateText()

    def updateText(self):
        self.setText(str(self))

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name
