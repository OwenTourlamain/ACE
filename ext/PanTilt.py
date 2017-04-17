from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

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
        setPTULayout.addWidget(self.homeButton, 2, 2)

        setGroup = QGroupBox(self.strings.PTT_SetTitle)
        setGroup.setLayout(setPTULayout)

        adjustPTULayout = QGridLayout()
        adjustPTULayout.setRowMinimumHeight(0, 55)
        adjustPTULayout.setRowMinimumHeight(1, 55)
        adjustPTULayout.setRowMinimumHeight(2, 55)
        adjustPTULayout.setRowMinimumHeight(3, 55)
        adjustPTULayout.setRowMinimumHeight(4, 55)
        adjustPTULayout.setRowMinimumHeight(5, 55)

        self.smallAdjustLeft    = SquareButton(30, u"\u2190")
        self.smallAdjustLeft.clicked.connect(self.adjustLeft)
        self.smallAdjustUp      = SquareButton(30, u"\u2191")
        self.smallAdjustUp.clicked.connect(self.adjustUp)
        self.smallAdjustRight   = SquareButton(30, u"\u2192")
        self.smallAdjustRight.clicked.connect(self.adjustRight)
        self.smallAdjustDown    = SquareButton(30, u"\u2193")
        self.smallAdjustDown.clicked.connect(self.adjustDown)

        self.largeAdjustLeft    = SquareButton(30, u"\u219E")
        self.largeAdjustLeft.clicked.connect(self.adjustLargeLeft)
        self.largeAdjustUp      = SquareButton(30, u"\u219F")
        self.largeAdjustUp.clicked.connect(self.adjustLargeUp)
        self.largeAdjustRight   = SquareButton(30, u"\u21A0")
        self.largeAdjustRight.clicked.connect(self.adjustLargeRight)
        self.largeAdjustDown    = SquareButton(30, u"\u21A1")
        self.largeAdjustDown.clicked.connect(self.adjustLargeDown)

        self.adjustHome         = SquareButton(30, u"\u2302")
        self.adjustHome.clicked.connect(self.home)

        self.largeAdjustLabel = QLabel(self.strings.PTT_LargeAdjustLabel)
        self.largeAdjustVal = SquareLineEdit(30, self.config.PTT_LargeAdjustVal)


        adjustPTULayout.addWidget(self.smallAdjustLeft,  2, 1)
        adjustPTULayout.addWidget(self.smallAdjustUp,    1, 2)
        adjustPTULayout.addWidget(self.smallAdjustRight, 2, 3)
        adjustPTULayout.addWidget(self.smallAdjustDown,  3, 2)

        adjustPTULayout.addWidget(self.largeAdjustLeft,  2, 0)
        adjustPTULayout.addWidget(self.largeAdjustUp,    0, 2)
        adjustPTULayout.addWidget(self.largeAdjustRight, 2, 4)
        adjustPTULayout.addWidget(self.largeAdjustDown,  4, 2)

        adjustPTULayout.addWidget(self.adjustHome,  2, 2)
        adjustPTULayout.addWidget(self.largeAdjustLabel, 5, 0, 4, 0)
        adjustPTULayout.addWidget(self.largeAdjustVal, 5, 4)

        currentValLayout = QHBoxLayout()

        self.currentVal = QLabel()
        self.refreshButton = QPushButton(self.strings.PTT_Refresh)
        self.refreshButton.clicked.connect(self.updatePTUVals)

        self.sideView = QLabel("Tilt")
        self.topView = QLabel("Pan")

        self.sideView.setAlignment(Qt.AlignCenter)
        self.topView.setAlignment(Qt.AlignCenter)

        self.sideViewPixmapBase = QPixmap("images/camera_side.png")
        self.topViewPixmapBase = QPixmap("images/camera_top.png")

        self.sideView.setPixmap(self.sideViewPixmapBase)
        self.topView.setPixmap(self.topViewPixmapBase)

        self.updatePTUVals()

        leftValLayout = QVBoxLayout()

        leftValLayout.addWidget(self.currentVal)
        leftValLayout.addWidget(self.refreshButton)

        currentValLayout.addLayout(leftValLayout)
        currentValLayout.addWidget(self.sideView)
        currentValLayout.addWidget(self.topView)

        currentValGroup = QGroupBox(self.strings.PTT_CurrTitle)
        currentValGroup.setLayout(currentValLayout)

        adjustGroup = QGroupBox(self.strings.PTT_AdjustTitle)
        adjustGroup.setLayout(adjustPTULayout)

        previewLayout = QVBoxLayout()

        self.preview = SquareLabel()
        self.preview.setStyleSheet("border: 1px solid black; padding: 2px")

        #self.refreshPreview = SquareButton(30, u"\u21BB")
        self.refreshPreview = QPushButton(u"\u21BB")
        self.refreshCheckbox = QCheckBox(self.strings.PTT_AutoRefresh)

        refreshPreviewLayout = QHBoxLayout()
        refreshPreviewLayout.addWidget(self.refreshPreview)
        refreshPreviewLayout.addStretch()
        refreshPreviewLayout.addWidget(self.refreshCheckbox)

        previewLayout.addWidget(self.preview)
        previewLayout.addLayout(refreshPreviewLayout)

        previewGroup = QGroupBox(self.strings.PTT_PreviewTitle)
        previewGroup.setLayout(previewLayout)

        #print(self.preview.width())
        #self.preview.setMinimumSize(QSize(self.preview.width(), self.preview.width()))

        layout = QGridLayout()

        layout.addWidget(currentValGroup, 0, 0)
        layout.addWidget(previewGroup, 1, 0)
        layout.addWidget(setGroup, 0, 1)
        layout.addWidget(adjustGroup, 1, 1)

        self.setLayout(layout)

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

        panTransform = QTransform()
        panTransform.rotate(-self.api.pancam.ptu.pan)
        topViewPixmap = self.topViewPixmapBase.transformed(panTransform)
        self.topView.setPixmap(topViewPixmap)

        tiltTransform = QTransform()
        tiltTransform.rotate(-self.api.pancam.ptu.tilt)
        sideViewPixmap = self.sideViewPixmapBase.transformed(tiltTransform)
        self.sideView.setPixmap(sideViewPixmap)

class SquareButton(QPushButton):
    """docstring for SquareButton."""

    def __init__(self, size, text=None):
        super(SquareButton, self).__init__(text)
        self.size = size

        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)
        sizeHint = self.sizeHint()
        if sizeHint.isValid():
            self.setMinimumSize(sizeHint)

    def heightForWidth(self, width):
        return self.width()

    def sizeHint(self):
        return QSize(self.size, self.size)

class SquareLineEdit(QLineEdit):
    """docstring for SquareButton."""

    def __init__(self, size, text=None):
        super(SquareLineEdit, self).__init__(text)
        self.size = size

        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)
        sizeHint = self.sizeHint()
        if sizeHint.isValid():
            self.setMinimumSize(sizeHint)

    def heightForWidth(self, width):
        return width

    def sizeHint(self):
        return QSize(self.size, self.size)

class SquareLabel(QLabel):
    """docstring for SquareButton."""

    def __init__(self, size=0, text=None):
        super(SquareLabel, self).__init__(text)
        #self.size = size

        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)
        #sizeHint = self.sizeHint()
        #if sizeHint.isValid():
        #    self.setMinimumSize(sizeHint)

    def heightForWidth(self, width):
        return width

    #def sizeHint(self):
    #    return QSize(self.size, self.size)
