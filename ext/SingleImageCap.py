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
        self.LWACcamera = self.api.pancam.cameras[0]
        self.RWACcamera = self.api.pancam.cameras[1]
        self.HRCcamera = self.api.pancam.cameras[2]

        # == LWAC ==
        self.LWACcaptureButton = QPushButton(self.strings.SIT_LWACcap)
        self.LWACcaptureButton.clicked.connect(self.LWACcapture)

        self.LWACsaveButton = QPushButton(self.strings.SIT_Save)
        self.LWACsaveButton.clicked.connect(self.LWACsave)
        self.LWACsaveButton.setDisabled(True)

        self.LWACpreview = SquareLabel()
        self.LWACpreview.setStyleSheet("border: 1px solid black; padding: 2px")

        self.LWACScroll = QScrollArea()
        self.LWACScroll.setWidgetResizable(True)

        self.LWACFilterCombo = QComboBox()
        self.LWACFilterCombo.addItems(self.config.LWACFilters)

        self.LWACAeModeNone = QRadioButton(self.strings.SIT_AeModeNone)
        self.LWACAeModeNone.toggled.connect(self.updateLWACAeMode)
        self.LWACAeModeServer = QRadioButton(self.strings.SIT_AeModeServer)
        self.LWACAeModeServer.toggled.connect(self.updateLWACAeMode)
        self.LWACAeModeCamera = QRadioButton(self.strings.SIT_AeModeCamera)
        self.LWACAeModeCamera.toggled.connect(self.updateLWACAeMode)

        self.LWACAeAlg = QComboBox()
        self.LWACAeAlg.addItems(self.config.AeAlgs)

        self.LWACAeTarget = QLineEdit(str(self.LWACcamera.ae_target))
        self.LWACAeTarget.setValidator(QDoubleValidator())

        self.LWACAeTol = QLineEdit(str(self.LWACcamera.ae_tolerance))
        self.LWACAeTol.setValidator(QDoubleValidator())

        self.LWACAeMax = QLineEdit(str(self.LWACcamera.ae_max_shutter))
        self.LWACAeMax.setValidator(QDoubleValidator())

        self.LWACAeMin = QLineEdit(str(self.LWACcamera.ae_min_shutter))
        self.LWACAeMin.setValidator(QDoubleValidator())

        self.LWACAeRate = QLineEdit(str(self.LWACcamera.ae_adjust_rate))
        self.LWACAeRate.setValidator(QDoubleValidator())

        self.LWACGain = QLineEdit(str(self.LWACcamera.gain))
        self.LWACGain.setValidator(QIntValidator())

        self.LWACShutter = QLineEdit(str(self.LWACcamera.shutter))
        self.LWACShutter.setValidator(QDoubleValidator())

        self.LWACExposure = QLineEdit(str(self.LWACcamera.shutter_target))
        self.LWACExposure.setValidator(QDoubleValidator())

        self.LWACMetering = QComboBox()
        self.LWACMetering.addItems(self.config.Metering)
        self.LWACMetering.currentIndexChanged.connect(self.updateLWACMetering)

        (roix, roiy, roiw, roih) = self.LWACcamera.roi

        self.LWACRoiX = QLineEdit(str(roix))
        self.LWACRoiX.setValidator(QDoubleValidator())

        self.LWACRoiY = QLineEdit(str(roiy))
        self.LWACRoiY.setValidator(QDoubleValidator())

        self.LWACRoiWidth = QLineEdit(str(roiw))
        self.LWACRoiWidth.setValidator(QDoubleValidator())

        self.LWACRoiHeight = QLineEdit(str(roih))
        self.LWACRoiHeight.setValidator(QDoubleValidator())

        # == HRC ==
        self.HRCInvisibleButton = QComboBox()
        sizePolicy = QSizePolicy()
        sizePolicy.setRetainSizeWhenHidden(True)
        self.HRCInvisibleButton.setSizePolicy(sizePolicy)
        self.HRCInvisibleButton.hide()

        self.HRCcaptureButton = QPushButton(self.strings.SIT_HRCcap)
        self.HRCcaptureButton.clicked.connect(self.HRCcapture)

        self.HRCsaveButton = QPushButton(self.strings.SIT_Save)
        self.HRCsaveButton.clicked.connect(self.HRCsave)
        self.HRCsaveButton.setDisabled(True)

        self.HRCpreview = SquareLabel()
        self.HRCpreview.setStyleSheet("border: 1px solid black; padding: 2px")

        self.HRCScroll = QScrollArea()
        self.HRCScroll.setWidgetResizable(True)

        self.HRCAeModeNone = QRadioButton(self.strings.SIT_AeModeNone)
        self.HRCAeModeNone.toggled.connect(self.updateHRCAeMode)
        self.HRCAeModeServer = QRadioButton(self.strings.SIT_AeModeServer)
        self.HRCAeModeServer.toggled.connect(self.updateHRCAeMode)
        self.HRCAeModeCamera = QRadioButton(self.strings.SIT_AeModeCamera)
        self.HRCAeModeCamera.toggled.connect(self.updateHRCAeMode)

        self.HRCAeAlg = QComboBox()
        self.HRCAeAlg.addItems(self.config.AeAlgs)

        self.HRCAeTarget = QLineEdit(str(self.HRCcamera.ae_target))
        self.HRCAeTarget.setValidator(QDoubleValidator())

        self.HRCAeTol = QLineEdit(str(self.HRCcamera.ae_tolerance))
        self.HRCAeTol.setValidator(QDoubleValidator())

        self.HRCAeMax = QLineEdit(str(self.HRCcamera.ae_max_shutter))
        self.HRCAeMax.setValidator(QDoubleValidator())

        self.HRCAeMin = QLineEdit(str(self.HRCcamera.ae_min_shutter))
        self.HRCAeMin.setValidator(QDoubleValidator())

        self.HRCAeRate = QLineEdit(str(self.HRCcamera.ae_adjust_rate))
        self.HRCAeRate.setValidator(QDoubleValidator())

        self.HRCGain = QLineEdit(str(self.HRCcamera.gain))
        self.HRCGain.setValidator(QIntValidator())

        self.HRCShutter = QLineEdit(str(self.HRCcamera.shutter))
        self.HRCShutter.setValidator(QDoubleValidator())

        self.HRCExposure = QLineEdit(str(self.HRCcamera.shutter_target))
        self.HRCExposure.setValidator(QDoubleValidator())

        self.HRCMetering = QComboBox()
        self.HRCMetering.addItems(self.config.Metering)
        self.HRCMetering.currentIndexChanged.connect(self.updateHRCMetering)

        (roix, roiy, roiw, roih) = self.HRCcamera.roi

        self.HRCRoiX = QLineEdit(str(roix))
        self.HRCRoiX.setValidator(QDoubleValidator())

        self.HRCRoiY = QLineEdit(str(roiy))
        self.HRCRoiY.setValidator(QDoubleValidator())

        self.HRCRoiWidth = QLineEdit(str(roiw))
        self.HRCRoiWidth.setValidator(QDoubleValidator())

        self.HRCRoiHeight = QLineEdit(str(roih))
        self.HRCRoiHeight.setValidator(QDoubleValidator())

        # == RWAC ==
        self.RWACcaptureButton = QPushButton(self.strings.SIT_RWACcap)
        self.RWACcaptureButton.clicked.connect(self.RWACcapture)

        self.RWACsaveButton = QPushButton(self.strings.SIT_Save)
        self.RWACsaveButton.clicked.connect(self.RWACsave)
        self.RWACsaveButton.setDisabled(True)

        self.RWACpreview = SquareLabel()
        self.RWACpreview.setStyleSheet("border: 1px solid black; padding: 2px")

        self.RWACScroll = QScrollArea()
        self.RWACScroll.setWidgetResizable(True)

        self.RWACFilterCombo = QComboBox()
        self.RWACFilterCombo.addItems(self.config.RWACFilters)

        self.RWACAeModeNone = QRadioButton(self.strings.SIT_AeModeNone)
        self.RWACAeModeNone.toggled.connect(self.updateRWACAeMode)
        self.RWACAeModeServer = QRadioButton(self.strings.SIT_AeModeServer)
        self.RWACAeModeServer.toggled.connect(self.updateRWACAeMode)
        self.RWACAeModeCamera = QRadioButton(self.strings.SIT_AeModeCamera)
        self.RWACAeModeCamera.toggled.connect(self.updateRWACAeMode)

        self.RWACAeAlg = QComboBox()
        self.RWACAeAlg.addItems(self.config.AeAlgs)

        self.RWACAeTarget = QLineEdit(str(self.RWACcamera.ae_target))
        self.RWACAeTarget.setValidator(QDoubleValidator())

        self.RWACAeTol = QLineEdit(str(self.RWACcamera.ae_tolerance))
        self.RWACAeTol.setValidator(QDoubleValidator())

        self.RWACAeMax = QLineEdit(str(self.RWACcamera.ae_max_shutter))
        self.RWACAeMax.setValidator(QDoubleValidator())

        self.RWACAeMin = QLineEdit(str(self.RWACcamera.ae_min_shutter))
        self.RWACAeMin.setValidator(QDoubleValidator())

        self.RWACAeRate = QLineEdit(str(self.RWACcamera.ae_adjust_rate))
        self.RWACAeRate.setValidator(QDoubleValidator())

        self.RWACGain = QLineEdit(str(self.RWACcamera.gain))
        self.RWACGain.setValidator(QIntValidator())

        self.RWACShutter = QLineEdit(str(self.RWACcamera.shutter))
        self.RWACShutter.setValidator(QDoubleValidator())

        self.RWACExposure = QLineEdit(str(self.RWACcamera.shutter_target))
        self.RWACExposure.setValidator(QDoubleValidator())

        self.RWACMetering = QComboBox()
        self.RWACMetering.addItems(self.config.Metering)
        self.RWACMetering.currentIndexChanged.connect(self.updateRWACMetering)

        (roix, roiy, roiw, roih) = self.RWACcamera.roi

        self.RWACRoiX = QLineEdit(str(roix))
        self.RWACRoiX.setValidator(QDoubleValidator())

        self.RWACRoiY = QLineEdit(str(roiy))
        self.RWACRoiY.setValidator(QDoubleValidator())

        self.RWACRoiWidth = QLineEdit(str(roiw))
        self.RWACRoiWidth.setValidator(QDoubleValidator())

        self.RWACRoiHeight = QLineEdit(str(roih))
        self.RWACRoiHeight.setValidator(QDoubleValidator())

        LWACGroup = QGroupBox(self.strings.SIT_LWACGroup)
        RWACGroup = QGroupBox(self.strings.SIT_RWACGroup)
        HRCGroup = QGroupBox(self.strings.SIT_HRCGroup)

        LWACLayout = QVBoxLayout()
        RWACLayout = QVBoxLayout()
        HRCLayout = QVBoxLayout()

        LWACScrollLayout = QFormLayout()
        LWACScrollLayout.addRow(self.strings.SIT_Filter, self.LWACFilterCombo)
        LWACScrollLayout.addRow(self.strings.SIT_Shutter, self.LWACShutter)
        LWACScrollLayout.addRow(self.strings.SIT_Exposure, self.LWACExposure)
        LWACScrollLayout.addRow(self.strings.SIT_Gain, self.LWACGain)
        LWACAeModeLayout = QHBoxLayout()
        LWACAeModeLayout.addWidget(self.LWACAeModeNone)
        LWACAeModeLayout.addWidget(self.LWACAeModeCamera)
        LWACAeModeLayout.addWidget(self.LWACAeModeServer)
        LWACAeModeGroup = QGroupBox()
        LWACAeModeGroup.setLayout(LWACAeModeLayout)
        LWACScrollLayout.addRow(self.strings.SIT_AeMode, LWACAeModeGroup)
        LWACAeLayout = QFormLayout()
        LWACAeLayout.addRow(self.strings.SIT_AeAlg, self.LWACAeAlg)
        LWACAeLayout.addRow(self.strings.SIT_AeTarget, self.LWACAeTarget)
        LWACAeLayout.addRow(self.strings.SIT_AeTol, self.LWACAeTol)
        LWACAeLayout.addRow(self.strings.SIT_AeMax, self.LWACAeMax)
        LWACAeLayout.addRow(self.strings.SIT_AeMin, self.LWACAeMin)
        LWACAeLayout.addRow(self.strings.SIT_AeRate, self.LWACAeRate)
        self.LWACAeGroup = QGroupBox(self.strings.SIT_Ae)
        self.LWACAeGroup.setLayout(LWACAeLayout)
        self.LWACAeGroup.setHidden(True)
        self.LWACAeModeNone.setChecked(True)
        LWACScrollLayout.addWidget(self.LWACAeGroup)
        LWACScrollLayout.addRow(self.strings.SIT_MeteringMode, self.LWACMetering)
        LWACMeteringLayout = QFormLayout()
        LWACMeteringLayout.addRow(self.strings.SIT_RoiX, self.LWACRoiX)
        LWACMeteringLayout.addRow(self.strings.SIT_RoiY, self.LWACRoiY)
        LWACMeteringLayout.addRow(self.strings.SIT_RoiWidth, self.LWACRoiWidth)
        LWACMeteringLayout.addRow(self.strings.SIT_RoiHeight, self.LWACRoiHeight)
        self.LWACMeteringGroup = QGroupBox(self.strings.SIT_Metering)
        self.LWACMeteringGroup.setLayout(LWACMeteringLayout)
        self.LWACMeteringGroup.setHidden(True)
        LWACScrollLayout.addWidget(self.LWACMeteringGroup)
        self.LWACScrollHolder = QWidget()
        self.LWACScrollHolder.setLayout(LWACScrollLayout)
        self.LWACScroll.setWidget(self.LWACScrollHolder)

        LWACLayout.addWidget(self.LWACpreview)
        LWACLayout.addWidget(self.LWACScroll, stretch=1)
        LWACLayout.addWidget(self.LWACcaptureButton)
        LWACLayout.addWidget(self.LWACsaveButton)

        LWACGroup.setLayout(LWACLayout)

        RWACScrollLayout = QFormLayout()
        RWACScrollLayout.addRow(self.strings.SIT_Filter, self.RWACFilterCombo)
        RWACScrollLayout.addRow(self.strings.SIT_Shutter, self.RWACShutter)
        RWACScrollLayout.addRow(self.strings.SIT_Exposure, self.RWACExposure)
        RWACScrollLayout.addRow(self.strings.SIT_Gain, self.RWACGain)
        RWACAeModeLayout = QHBoxLayout()
        RWACAeModeLayout.addWidget(self.RWACAeModeNone)
        RWACAeModeLayout.addWidget(self.RWACAeModeCamera)
        RWACAeModeLayout.addWidget(self.RWACAeModeServer)
        RWACAeModeGroup = QGroupBox()
        RWACAeModeGroup.setLayout(RWACAeModeLayout)
        RWACScrollLayout.addRow(self.strings.SIT_AeMode, RWACAeModeGroup)
        RWACAeLayout = QFormLayout()
        RWACAeLayout.addRow(self.strings.SIT_AeAlg, self.RWACAeAlg)
        RWACAeLayout.addRow(self.strings.SIT_AeTarget, self.RWACAeTarget)
        RWACAeLayout.addRow(self.strings.SIT_AeTol, self.RWACAeTol)
        RWACAeLayout.addRow(self.strings.SIT_AeMax, self.RWACAeMax)
        RWACAeLayout.addRow(self.strings.SIT_AeMin, self.RWACAeMin)
        RWACAeLayout.addRow(self.strings.SIT_AeRate, self.RWACAeRate)
        self.RWACAeGroup = QGroupBox(self.strings.SIT_Ae)
        self.RWACAeGroup.setLayout(RWACAeLayout)
        self.RWACAeGroup.setHidden(True)
        self.RWACAeModeNone.setChecked(True)
        RWACScrollLayout.addWidget(self.RWACAeGroup)
        RWACScrollLayout.addRow(self.strings.SIT_MeteringMode, self.RWACMetering)
        RWACMeteringLayout = QFormLayout()
        RWACMeteringLayout.addRow(self.strings.SIT_RoiX, self.RWACRoiX)
        RWACMeteringLayout.addRow(self.strings.SIT_RoiY, self.RWACRoiY)
        RWACMeteringLayout.addRow(self.strings.SIT_RoiWidth, self.RWACRoiWidth)
        RWACMeteringLayout.addRow(self.strings.SIT_RoiHeight, self.RWACRoiHeight)
        self.RWACMeteringGroup = QGroupBox(self.strings.SIT_Metering)
        self.RWACMeteringGroup.setLayout(RWACMeteringLayout)
        self.RWACMeteringGroup.setHidden(True)
        RWACScrollLayout.addWidget(self.RWACMeteringGroup)
        self.RWACScrollHolder = QWidget()
        self.RWACScrollHolder.setLayout(RWACScrollLayout)
        self.RWACScroll.setWidget(self.RWACScrollHolder)

        RWACLayout.addWidget(self.RWACpreview)
        RWACLayout.addWidget(self.RWACScroll, stretch=1)
        RWACLayout.addWidget(self.RWACcaptureButton)
        RWACLayout.addWidget(self.RWACsaveButton)

        RWACGroup.setLayout(RWACLayout)

        HRCScrollLayout = QFormLayout()
        HRCScrollLayout.addRow("", self.HRCInvisibleButton)
        HRCScrollLayout.addRow(self.strings.SIT_Shutter, self.HRCShutter)
        HRCScrollLayout.addRow(self.strings.SIT_Exposure, self.HRCExposure)
        HRCScrollLayout.addRow(self.strings.SIT_Gain, self.HRCGain)
        HRCAeModeLayout = QHBoxLayout()
        HRCAeModeLayout.addWidget(self.HRCAeModeNone)
        HRCAeModeLayout.addWidget(self.HRCAeModeCamera)
        HRCAeModeLayout.addWidget(self.HRCAeModeServer)
        HRCAeModeGroup = QGroupBox()
        HRCAeModeGroup.setLayout(HRCAeModeLayout)
        HRCScrollLayout.addRow(self.strings.SIT_AeMode, HRCAeModeGroup)
        HRCAeLayout = QFormLayout()
        HRCAeLayout.addRow(self.strings.SIT_AeAlg, self.HRCAeAlg)
        HRCAeLayout.addRow(self.strings.SIT_AeTarget, self.HRCAeTarget)
        HRCAeLayout.addRow(self.strings.SIT_AeTol, self.HRCAeTol)
        HRCAeLayout.addRow(self.strings.SIT_AeMax, self.HRCAeMax)
        HRCAeLayout.addRow(self.strings.SIT_AeMin, self.HRCAeMin)
        HRCAeLayout.addRow(self.strings.SIT_AeRate, self.HRCAeRate)
        self.HRCAeGroup = QGroupBox(self.strings.SIT_Ae)
        self.HRCAeGroup.setLayout(HRCAeLayout)
        self.HRCAeGroup.setHidden(True)
        self.HRCAeModeNone.setChecked(True)
        HRCScrollLayout.addWidget(self.HRCAeGroup)
        HRCScrollLayout.addRow(self.strings.SIT_MeteringMode, self.HRCMetering)
        HRCMeteringLayout = QFormLayout()
        HRCMeteringLayout.addRow(self.strings.SIT_RoiX, self.HRCRoiX)
        HRCMeteringLayout.addRow(self.strings.SIT_RoiY, self.HRCRoiY)
        HRCMeteringLayout.addRow(self.strings.SIT_RoiWidth, self.HRCRoiWidth)
        HRCMeteringLayout.addRow(self.strings.SIT_RoiHeight, self.HRCRoiHeight)
        self.HRCMeteringGroup = QGroupBox(self.strings.SIT_Metering)
        self.HRCMeteringGroup.setLayout(HRCMeteringLayout)
        self.HRCMeteringGroup.setHidden(True)
        HRCScrollLayout.addWidget(self.HRCMeteringGroup)
        self.HRCScrollHolder = QWidget()
        self.HRCScrollHolder.setLayout(HRCScrollLayout)
        self.HRCScroll.setWidget(self.HRCScrollHolder)

        HRCLayout.addWidget(self.HRCpreview)
        HRCLayout.addWidget(self.HRCScroll, stretch=1)
        HRCLayout.addWidget(self.HRCcaptureButton)
        HRCLayout.addWidget(self.HRCsaveButton)

        HRCGroup.setLayout(HRCLayout)

        layout = QHBoxLayout()
        layout.addWidget(LWACGroup)
        layout.addWidget(HRCGroup)
        layout.addWidget(RWACGroup)
        self.setLayout(layout)

    def LWACcapture(self):
        self.LWACcamera.filter = self.LWACFilterCombo.currentIndex()
        self.LWACcamera.gain = int(self.LWACGain.text())
        self.LWACcamera.shutter = float(self.LWACShutter.text())
        self.LWACcamera.shutter_target = float(self.LWACExposure.text())

        if self.LWACMetering.currentIndex() == 1:
            self.LWACcamera.roi = (int(self.LWACRoiX.text()),
                                   int(self.LWACRoiY.text()),
                                   int(self.LWACRoiWidth.text()),
                                   int(self.LWACRoiHeight.text())
                                   )
            self.LWACcamera.ae_meter_region  = 1
        else:
            self.LWACcamera.roi = (0,0,0,0)
            self.LWACcamera.ae_meter_region  = 0

        if self.LWACAeModeNone.isChecked():
            serverAE = False
            self.LWACcamera.shutter_mode = 0
        elif self.LWACAeModeServer.isChecked():
            serverAE = True
            self.LWACcamera.shutter_mode = 0
        else:
            serverAE = False
            self.LWACcamera.shutter_mode = 1

        ##self.aeAlg = capture.aeAlg ask!!
        self.LWACcamera.ae_target = float(self.LWACAeTarget.text())
        self.LWACcamera.ae_tolerance = float(self.LWACAeTol.text())
        self.LWACcamera.ae_max_shutter = float(self.LWACAeMax.text())
        self.LWACcamera.ae_min_shutter = float(self.LWACAeMin.text())
        self.LWACcamera.ae_adjust_rate = float(self.LWACAeRate.text())

        self.LWACimage = self.LWACcamera.get_image(ae=serverAE)
        pixmap = QPixmap.fromImage(ImageQt(self.LWACimage.as_pil_image()).scaled(self.LWACpreview.size(), Qt.KeepAspectRatio))
        self.LWACpreview.setPixmap(pixmap)
        self.LWACsaveButton.setEnabled(True)

    def RWACcapture(self):
        self.RWACcamera.filter = self.RWACFilterCombo.currentIndex()
        self.RWACcamera.gain = int(self.RWACGain.text())
        self.RWACcamera.shutter = float(self.RWACShutter.text())
        self.RWACcamera.shutter_target = float(self.RWACExposure.text())

        if self.RWACMetering.currentIndex() == 1:
          self.RWACcamera.roi = (int(self.RWACRoiX.text()),
                                 int(self.RWACRoiY.text()),
                                 int(self.RWACRoiWidth.text()),
                                 int(self.RWACRoiHeight.text())
                                 )
          self.RWACcamera.ae_meter_region  = 1
        else:
          self.RWACcamera.roi = (0,0,0,0)
          self.RWACcamera.ae_meter_region  = 0

        if self.RWACAeModeNone.isChecked():
          serverAE = False
          self.RWACcamera.shutter_mode = 0
        elif self.RWACAeModeServer.isChecked():
          serverAE = True
          self.RWACcamera.shutter_mode = 0
        else:
          serverAE = False
          self.RWACcamera.shutter_mode = 1

        ##self.aeAlg = capture.aeAlg ask!!
        self.RWACcamera.ae_target = float(self.RWACAeTarget.text())
        self.RWACcamera.ae_tolerance = float(self.RWACAeTol.text())
        self.RWACcamera.ae_max_shutter = float(self.RWACAeMax.text())
        self.RWACcamera.ae_min_shutter = float(self.RWACAeMin.text())
        self.RWACcamera.ae_adjust_rate = float(self.RWACAeRate.text())

        self.RWACimage = self.RWACcamera.get_image(ae=serverAE)
        pixmap = QPixmap.fromImage(ImageQt(self.RWACimage.as_pil_image()).scaled(self.RWACpreview.size(), Qt.KeepAspectRatio))
        self.RWACpreview.setPixmap(pixmap)
        self.RWACsaveButton.setEnabled(True)

    def HRCcapture(self):
        self.HRCcamera.gain = int(self.HRCGain.text())
        self.HRCcamera.shutter = float(self.HRCShutter.text())
        self.HRCcamera.shutter_target = float(self.HRCExposure.text())

        if self.HRCMetering.currentIndex() == 1:
          self.HRCcamera.roi = (int(self.HRCRoiX.text()),
                                 int(self.HRCRoiY.text()),
                                 int(self.HRCRoiWidth.text()),
                                 int(self.HRCRoiHeight.text())
                                 )
          self.HRCcamera.ae_meter_region  = 1
        else:
          self.HRCcamera.roi = (0,0,0,0)
          self.HRCcamera.ae_meter_region  = 0

        if self.HRCAeModeNone.isChecked():
          serverAE = False
          self.HRCcamera.shutter_mode = 0
        elif self.HRCAeModeServer.isChecked():
          serverAE = True
          self.HRCcamera.shutter_mode = 0
        else:
          serverAE = False
          self.HRCcamera.shutter_mode = 1

        ##self.aeAlg = capture.aeAlg ask!!
        self.HRCcamera.ae_target = float(self.HRCAeTarget.text())
        self.HRCcamera.ae_tolerance = float(self.HRCAeTol.text())
        self.HRCcamera.ae_max_shutter = float(self.HRCAeMax.text())
        self.HRCcamera.ae_min_shutter = float(self.HRCAeMin.text())
        self.HRCcamera.ae_adjust_rate = float(self.HRCAeRate.text())

        self.HRCimage = self.HRCcamera.get_image(ae=serverAE)
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

    def updateLWACAeMode(self):
        if self.LWACAeModeServer.isChecked():
            self.LWACAeGroup.setHidden(False)
        else:
            self.LWACAeGroup.setHidden(True)

    def updateRWACAeMode(self):
        if self.RWACAeModeServer.isChecked():
            self.RWACAeGroup.setHidden(False)
        else:
            self.RWACAeGroup.setHidden(True)

    def updateHRCAeMode(self):
        if self.HRCAeModeServer.isChecked():
            self.HRCAeGroup.setHidden(False)
        else:
            self.HRCAeGroup.setHidden(True)

    def updateLWACMetering(self, current):
        if current == 1:
            self.LWACMeteringGroup.setHidden(False)
        else:
            self.LWACMeteringGroup.setHidden(True)

    def updateRWACMetering(self, current):
        if current == 1:
            self.RWACMeteringGroup.setHidden(False)
        else:
            self.RWACMeteringGroup.setHidden(True)

    def updateHRCMetering(self, current):
        if current == 1:
            self.HRCMeteringGroup.setHidden(False)
        else:
            self.HRCMeteringGroup.setHidden(True)

class SquareLabel(QLabel):
    """docstring for SquareButton."""

    def __init__(self):
        super(SquareLabel, self).__init__()

        sizePolicy = QSizePolicy(QSizePolicy.Ignored , QSizePolicy.Ignored)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

    def heightForWidth(self, width):
        return self.width()
