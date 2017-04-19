from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PIL.ImageQt import ImageQt

class Tab(QWidget): # HACK: Make class load dynamically
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

        self.initTab()

    def initTab(self):
        layout = QGridLayout()
        LWACLayout = QVBoxLayout()
        RWACLayout = QVBoxLayout()
        HRCLayout = QVBoxLayout()

        # == LWAC ==
        self.LWACcaptureButton = QPushButton(self.strings.SIT_LWACcap, self)
        self.LWACcaptureButton.clicked.connect(self.LWACcapture)

        self.LWACsaveButton = QPushButton(self.strings.SIT_Save, self)
        self.LWACsaveButton.clicked.connect(self.LWACsave)
        self.LWACsaveButton.setDisabled(True)

        self.LWACFilterCombo = QComboBox(self)
        self.LWACFilterCombo.addItems(self.config.LWACFilters)

        self.LWACpreview = SquareLabel()
        #self.LWACpreview.setFixedWidth(self.config.preview_size)
        #self.LWACpreview.setFixedHeight(self.config.preview_size)
        self.LWACpreview.setStyleSheet("border: 1px solid black; padding: 2px")
        layout.addWidget(self.LWACpreview, 0, 0)
        layout.addWidget(self.LWACFilterCombo, 1, 0)
        layout.addWidget(self.LWACcaptureButton, 2, 0)
        layout.addWidget(self.LWACsaveButton, 3, 0)
        #LWACLayout.addStretch(1)

        # == RWAC ==
        self.RWACcaptureButton = QPushButton(self.strings.SIT_RWACcap, self)
        self.RWACcaptureButton.clicked.connect(self.RWACcapture)

        self.RWACsaveButton = QPushButton(self.strings.SIT_Save, self)
        self.RWACsaveButton.clicked.connect(self.RWACsave)
        self.RWACsaveButton.setDisabled(True)

        self.RWACFilterCombo = QComboBox(self)
        self.RWACFilterCombo.addItems(self.config.RWACFilters)

        self.RWACpreview = SquareLabel()
        #self.RWACpreview.setFixedWidth(self.config.preview_size)
        #self.RWACpreview.setFixedHeight(self.config.preview_size)
        self.RWACpreview.setStyleSheet("border: 1px solid black; padding: 2px")
        layout.addWidget(self.RWACpreview, 0, 2)
        layout.addWidget(self.RWACFilterCombo, 1, 2)
        layout.addWidget(self.RWACcaptureButton, 2, 2)
        layout.addWidget(self.RWACsaveButton, 3, 2)
        #RWACLayout.addStretch(1)

        # == HRC ==
        self.HRCcaptureButton = QPushButton(self.strings.SIT_HRCcap, self)
        self.HRCcaptureButton.clicked.connect(self.HRCcapture)

        self.HRCsaveButton = QPushButton(self.strings.SIT_Save, self)
        self.HRCsaveButton.clicked.connect(self.HRCsave)
        self.HRCsaveButton.setDisabled(True)

        self.HRCpreview = SquareLabel()
        #self.HRCpreview.setFixedWidth(self.config.preview_size)
        #self.HRCpreview.setFixedHeight(self.config.preview_size)
        self.HRCpreview.setStyleSheet("border: 1px solid black; padding: 2px")
        layout.addWidget(self.HRCpreview, 0, 1)
        layout.addWidget(self.HRCcaptureButton, 1, 1)
        layout.addWidget(self.HRCsaveButton, 2, 1)
        #layout.addStretch(1)

        #layout.addLayout(LWACLayout)
        #layout.addLayout(HRCLayout)
        #layout.addLayout(RWACLayout)
        #layout.addStretch(1)
        
        rootLayout = QVBoxLayout()
        rootLayout.addLayout(layout)
        rootLayout.addStretch()
        self.setLayout(rootLayout)

# TODO: Refactor these,  lots of repettion
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
            self.LWACimage.save_png_with_metadata("LWAC.png")

    def RWACsave(self):
        if self.RWACimage:
            self.RWACimage.save_png_with_metadata("RWAC.png")

    def HRCsave(self):
        if self.HRCimage:
            self.HRCimage.save_png_with_metadata("HRC.png")

class SquareLabel(QLabel): #TODO: Move to utility class
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
