from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PIL.ImageQt import ImageQt

class Tab(QWidget): # HACK: Make class load dynamically
    """docstring for SingleImageCap."""

    def __init__(self, config, strings, api):
        super().__init__()
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
        layout = QHBoxLayout()
        LWACLayout = QVBoxLayout()
        RWACLayout = QVBoxLayout()
        HRCLayout = QVBoxLayout()

        # == LWAC ==
        self.LWACcaptureButton = QPushButton(self.strings.SIT_LWACcap, self)
        self.LWACcaptureButton.clicked.connect(self.LWACcapture)

        self.LWACsaveButton = QPushButton(self.strings.SIT_Save, self)
        self.LWACsaveButton.clicked.connect(self.LWACsave)
        self.LWACsaveButton.setDisabled(True)

        self.LWACpreview = QLabel()
        self.LWACpreview.setFixedWidth(self.config["preview_size"])
        self.LWACpreview.setFixedHeight(self.config["preview_size"])
        self.LWACpreview.setStyleSheet("border: 1px solid black; padding: 2px")
        LWACLayout.addWidget(self.LWACpreview)
        LWACLayout.addWidget(self.LWACcaptureButton)
        LWACLayout.addWidget(self.LWACsaveButton)
        LWACLayout.addStretch(1)

        # == RWAC ==
        self.RWACcaptureButton = QPushButton(self.strings.SIT_LWACcap, self)
        self.RWACcaptureButton.clicked.connect(self.RWACcapture)

        self.RWACsaveButton = QPushButton(self.strings.SIT_Save, self)
        self.RWACsaveButton.clicked.connect(self.RWACsave)
        self.RWACsaveButton.setDisabled(True)

        self.RWACpreview = QLabel()
        self.RWACpreview.setFixedWidth(self.config["preview_size"])
        self.RWACpreview.setFixedHeight(self.config["preview_size"])
        self.RWACpreview.setStyleSheet("border: 1px solid black; padding: 2px")
        RWACLayout.addWidget(self.RWACpreview)
        RWACLayout.addWidget(self.RWACcaptureButton)
        RWACLayout.addWidget(self.RWACsaveButton)
        RWACLayout.addStretch(1)

        # == HRC ==
        self.HRCcaptureButton = QPushButton(self.strings.SIT_HRCcap, self)
        self.HRCcaptureButton.clicked.connect(self.HRCcapture)

        self.HRCsaveButton = QPushButton(self.strings.SIT_Save, self)
        self.HRCsaveButton.clicked.connect(self.HRCsave)
        self.HRCsaveButton.setDisabled(True)

        self.HRCpreview = QLabel()
        self.HRCpreview.setFixedWidth(self.config["preview_size"])
        self.HRCpreview.setFixedHeight(self.config["preview_size"])
        self.HRCpreview.setStyleSheet("border: 1px solid black; padding: 2px")
        HRCLayout.addWidget(self.HRCpreview)
        HRCLayout.addWidget(self.HRCcaptureButton)
        HRCLayout.addWidget(self.HRCsaveButton)
        HRCLayout.addStretch(1)

        layout.addLayout(LWACLayout)
        layout.addLayout(HRCLayout)
        layout.addLayout(RWACLayout)
        layout.addStretch(1)

        self.setLayout(layout)

# TODO: Refactor these,  lots of repettion
    def LWACcapture(self):
        camera = self.api.pancam.cameras[0]
        self.LWACimage = camera.get_image()
        pixmap = QPixmap.fromImage(ImageQt(self.LWACimage.as_pil_image()).scaled(self.LWACpreview.size(), Qt.KeepAspectRatio))
        self.LWACpreview.setPixmap(pixmap)
        self.LWACsaveButton.setEnabled(True)

    def RWACcapture(self):
        camera = self.api.pancam.cameras[1]
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
        if self.LWACimage:
            self.LWACimage.save_png_with_metadata("RWAC.png")

    def HRCsave(self):
        if self.LWACimage:
            self.LWACimage.save_png_with_metadata("HRC.png")
