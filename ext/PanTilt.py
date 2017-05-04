from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PIL.ImageQt import ImageQt

class Tab(QWidget): # HACK: Make class load dynamically
    """docstring for PanTiltTab."""

    def __init__(self, config, strings, api, verbose):
        super().__init__()
        self.verbose = verbose
        self.config = config
        self.strings = strings
        self.api = api
        self.title = self.strings.PTT_Title

        self.initTab()

    def initTab(self):
        setPTULayout = QGridLayout()

        # TODO: use acceptableinput
        self.pan = QLineEdit(self)
        #self.pan.setPlaceholderText(self.strings.PTT_Pan)

        self.tilt = QLineEdit(self)
        #self.tilt.setPlaceholderText(self.strings.PTT_Tilt)

        self.panLabel = QLabel(self.strings.PTT_Pan)
        self.pan.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.tiltLabel = QLabel(self.strings.PTT_Tilt)
        self.tilt.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))

        self.homeButton = QPushButton(self.strings.PTT_Home)
        self.homeButton.clicked.connect(self.home)

        self.setPanButton = QPushButton(self.strings.PTT_SetPan)
        self.setPanButton.clicked.connect(self.setPan)

        self.setTiltButton = QPushButton(self.strings.PTT_SetTilt)
        self.setTiltButton.clicked.connect(self.setTilt)

        #panLayout = QHBoxLayout()
        #panLayout.addWidget(self.panLabel)
        #panLayout.addWidget(self.pan)
        #panLayout.addWidget(self.setPanButton)

        #tiltLayout = QHBoxLayout()
        #tiltLayout.addWidget(self.tiltLabel)
        #tiltLayout.addWidget(self.tilt)
        #tiltLayout.addWidget(self.setTiltButton)

        #setPTULayout.addLayout(panLayout)
        #setPTULayout.addLayout(tiltLayout)
        #setPTULayout.addWidget(self.homeButton)
        setPTULayout.addWidget(self.panLabel, 0, 0)
        setPTULayout.addWidget(self.pan, 0, 1)
        setPTULayout.addWidget(self.setPanButton, 0, 2)
        setPTULayout.addWidget(self.tiltLabel, 1, 0)
        setPTULayout.addWidget(self.tilt, 1, 1)
        setPTULayout.addWidget(self.setTiltButton, 1, 2)
        setPTULayout.addWidget(self.homeButton, 0, 3)

        setGroup = QGroupBox(self.strings.PTT_SetTitle)
        setGroup.setLayout(setPTULayout)

        adjustPTULayout = QVBoxLayout()
        adjustPTULayoutLine1 = QHBoxLayout()
        adjustPTULayoutLine2 = QHBoxLayout()
        adjustPTULayoutLine3 = QHBoxLayout()
        adjustPTULayoutLine4 = QHBoxLayout()
        adjustPTULayoutLine5 = QHBoxLayout()
        adjustPTULayoutLine6 = QHBoxLayout()

        smallArrowBase = QPixmap("images/arrow_small.png")
        largeArrowBase = QPixmap("images/arrow_large.png")
        stowBase = QPixmap("images/stow.png")
        refreshBase = QPixmap("images/refresh.png")

        leftTrans = QTransform()
        leftTrans.rotate(180)
        upTrans = QTransform()
        upTrans.rotate(-90)
        downTrans = QTransform()
        downTrans.rotate(90)

        self.smallAdjustLeft    = SquareButton(30, u"\u2190")
        self.smallAdjustLeft.clicked.connect(self.adjustLeft)
        self.smallAdjustLeft.setIcon(QIcon(smallArrowBase.transformed(leftTrans)))
        self.smallAdjustUp      = SquareButton(30, u"\u2191")
        self.smallAdjustUp.clicked.connect(self.adjustUp)
        self.smallAdjustUp.setIcon(QIcon(smallArrowBase.transformed(upTrans)))
        self.smallAdjustRight   = SquareButton(30, u"\u2192")
        self.smallAdjustRight.clicked.connect(self.adjustRight)
        self.smallAdjustRight.setIcon(QIcon(smallArrowBase))
        self.smallAdjustDown    = SquareButton(30, u"\u2193")
        self.smallAdjustDown.clicked.connect(self.adjustDown)
        self.smallAdjustDown.setIcon(QIcon(smallArrowBase.transformed(downTrans)))

        self.largeAdjustLeft    = SquareButton(30, u"\u219E")
        self.largeAdjustLeft.clicked.connect(self.adjustLargeLeft)
        self.largeAdjustLeft.setIcon(QIcon(largeArrowBase.transformed(leftTrans)))
        self.largeAdjustUp      = SquareButton(30, u"\u219F")
        self.largeAdjustUp.clicked.connect(self.adjustLargeUp)
        self.largeAdjustUp.setIcon(QIcon(largeArrowBase.transformed(upTrans)))
        self.largeAdjustRight   = SquareButton(30, u"\u21A0")
        self.largeAdjustRight.clicked.connect(self.adjustLargeRight)
        self.largeAdjustRight.setIcon(QIcon(largeArrowBase))
        self.largeAdjustDown    = SquareButton(30, u"\u21A1")
        self.largeAdjustDown.clicked.connect(self.adjustLargeDown)
        self.largeAdjustDown.setIcon(QIcon(largeArrowBase.transformed(downTrans)))

        self.adjustHome         = SquareButton(30, u"\u2302")
        self.adjustHome.clicked.connect(self.home)
        self.adjustHome.setIcon(QIcon(stowBase))

        self.largeAdjustLabel = QLabel(self.strings.PTT_LargeAdjustLabel)
        self.largeAdjustVal = SquareLineEdit(30, self.config.PTT_LargeAdjustVal)


        adjustPTULayoutLine1.addWidget(self.largeAdjustUp)

        adjustPTULayoutLine2.addWidget(self.smallAdjustUp)

        adjustPTULayoutLine3.addWidget(self.largeAdjustLeft)
        adjustPTULayoutLine3.addWidget(self.smallAdjustLeft)
        adjustPTULayoutLine3.addWidget(self.adjustHome)
        adjustPTULayoutLine3.addWidget(self.smallAdjustRight)
        adjustPTULayoutLine3.addWidget(self.largeAdjustRight)

        adjustPTULayoutLine4.addWidget(self.smallAdjustDown)

        adjustPTULayoutLine5.addWidget(self.largeAdjustDown)

        adjustPTULayoutLine6.addWidget(self.largeAdjustLabel)
        adjustPTULayoutLine6.addWidget(self.largeAdjustVal)

        adjustPTULayout.addLayout(adjustPTULayoutLine1)
        adjustPTULayout.addLayout(adjustPTULayoutLine2)
        adjustPTULayout.addLayout(adjustPTULayoutLine3)
        adjustPTULayout.addLayout(adjustPTULayoutLine4)
        adjustPTULayout.addLayout(adjustPTULayoutLine5)
        adjustPTULayout.addStretch()
        adjustPTULayout.addLayout(adjustPTULayoutLine6)

        currentValLayout = QHBoxLayout()

        self.currentVal = QLabel()
        self.refreshButton = QPushButton()
        self.refreshButton.clicked.connect(self.updatePTUVals)
        self.refreshButton.setIcon(QIcon(refreshBase))

        leftValLayout = QHBoxLayout()

        currentValLayout.addWidget(self.currentVal, stretch=1)
        currentValLayout.addWidget(self.refreshButton)

        currentValGroup = QGroupBox(self.strings.PTT_CurrTitle)
        currentValGroup.setLayout(currentValLayout)

        adjustGroup = QGroupBox(self.strings.PTT_AdjustTitle)
        adjustGroup.setLayout(adjustPTULayout)

        previewLayout = QVBoxLayout()

        self.preview = SquareLabel()
        self.preview.setStyleSheet("border: 1px solid black; padding: 2px")

        #self.refreshPreview = SquareButton(30, u"\u21BB")
        self.refreshPreview = QPushButton()
        self.refreshPreview.clicked.connect(self.updatePreview)
        self.refreshPreview.setIcon(QIcon(refreshBase))
        self.refreshCheckbox = QCheckBox(self.strings.PTT_AutoRefresh)
        self.refreshCombo = QComboBox()
        self.refreshCombo.addItems(self.config.cameras)

        refreshPreviewLayout = QHBoxLayout()
        refreshPreviewLayout.addWidget(self.refreshPreview)
        refreshPreviewLayout.addWidget(self.refreshCombo)
        refreshPreviewLayout.addStretch()
        refreshPreviewLayout.addWidget(self.refreshCheckbox)

        previewLayout.addWidget(self.preview)
        previewLayout.addLayout(refreshPreviewLayout)

        previewGroup = QGroupBox(self.strings.PTT_PreviewTitle)
        previewGroup.setLayout(previewLayout)

        #print(self.preview.width())
        #self.preview.setMinimumSize(QSize(self.preview.width(), self.preview.width()))

        topLayout = QHBoxLayout()
        bottomLayout = QHBoxLayout()

        topLayout.addWidget(currentValGroup, stretch=1)
        topLayout.addWidget(previewGroup)
        bottomLayout.addWidget(setGroup, stretch=1)
        bottomLayout.addWidget(adjustGroup)
        #blankItem = QWidget()
        #layout.addWidget(blankItem, 2, 2)

        layout = QVBoxLayout()
        layout.addLayout(topLayout)
        layout.addLayout(bottomLayout)

        self.setLayout(layout)

        self.updatePTUVals()

    def setPan(self):
        ptu = self.api.pancam.ptu
        ptu.pan = float(self.pan.text())
        self.updatePTUVals()

    def setTilt(self):
        ptu = self.api.pancam.ptu
        ptu.tilt = float(self.tilt.text())
        self.updatePTUVals()

    def home(self):
        ptu = self.api.pancam.ptu
        ptu.stow()
        self.updatePTUVals()

    def adjustLeft(self):
        self.adjustPan(1)
        self.updatePTUVals()

    def adjustUp(self):
        self.adjustTilt(1)
        self.updatePTUVals()

    def adjustRight(self):
        self.adjustPan(-1)
        self.updatePTUVals()

    def adjustDown(self):
        self.adjustTilt(-1)
        self.updatePTUVals()

    def adjustLargeLeft(self):
        self.adjustPan(float(self.largeAdjustVal.text()))
        self.updatePTUVals()

    def adjustLargeUp(self):
        self.adjustTilt(float(self.largeAdjustVal.text()))
        self.updatePTUVals()

    def adjustLargeRight(self):
        self.adjustPan(float(self.largeAdjustVal.text()) * -1)
        self.updatePTUVals()

    def adjustLargeDown(self):
        self.adjustTilt(float(self.largeAdjustVal.text()) * -1)
        self.updatePTUVals()

    def adjustPan(self, val):
        self.api.pancam.ptu.pan += val

    def adjustTilt(self, val):
        self.api.pancam.ptu.tilt += val

    def updatePTUVals(self):
        self.currentVal.setText("%s:\t%.3f\n%s:\t%.3f" % (self.strings.PTT_Pan, self.api.pancam.ptu.pan,
                                                self.strings.PTT_Tilt, self.api.pancam.ptu.tilt))
        if self.refreshCheckbox.isChecked():
            self.updatePreview()

    def updatePreview(self):
        cameraNumber = self.refreshCombo.currentIndex()
        camera = self.api.pancam.cameras[cameraNumber]
        self.image = camera.get_image()
        pixmap = QPixmap.fromImage(ImageQt(self.image.as_pil_image()).scaled(self.preview.size(), Qt.KeepAspectRatio))
        self.preview.setPixmap(pixmap)

class SquareButton(QToolButton):
    """docstring for SquareButton."""

    def __init__(self, size=0, text=None):
        super(SquareButton, self).__init__()
        #self.size = size

        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)
        #sizeHint = self.sizeHint()
        #if sizeHint.isValid():
        #    self.setMinimumSize(sizeHint)

    def heightForWidth(self, width):
        return self.width()

#   def sizeHint(self):
#        return QSize(self.size, self.size)

class SquareLineEdit(QLineEdit):
    """docstring for SquareButton."""

    def __init__(self, size=0, text=None):
        super(SquareLineEdit, self).__init__(text)
        #self.size = size

        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)
        #sizeHint = self.sizeHint()
        #if sizeHint.isValid():
        #    self.setMinimumSize(sizeHint)

    def heightForWidth(self, width):
        return self.width()

#    def sizeHint(self):
#        return QSize(self.size, self.size)

class SquareLabel(QLabel):
    """docstring for SquareButton."""

    def __init__(self, size=0, text=None):
        super(SquareLabel, self).__init__(text)
        #self.size = size

        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)
        #sizeHint = self.sizeHint()
        #if sizeHint.isValid():
        #    self.setMinimumSize(sizeHint)

    def heightForWidth(self, width):
        return self.width()

#    def sizeHint(self):
#        return QSize(self.size, self.size)
