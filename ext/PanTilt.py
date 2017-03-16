from PyQt5.QtWidgets import *

class Tab(QWidget): # HACK: Make class load dynamically
    """docstring for PanTiltTab."""

    def __init__(self, config, strings, api):
        super().__init__()
        self.config = config
        self.strings = strings
        self.api = api
        self.title = self.strings.PTT_Title

        self.initTab()

    def initTab(self):
        layout = QVBoxLayout()

        # TODO: use acceptableinput
        self.pan = QLineEdit(self)
        self.pan.setPlaceholderText(self.strings.PTT_Pan)

        self.tilt = QLineEdit(self)
        self.tilt.setPlaceholderText(self.strings.PTT_Tilt)

        self.homeButton = QPushButton(self.strings.PTT_Home)
        self.homeButton.clicked.connect(self.home)

        self.setPanButton = QPushButton(self.strings.PTT_SetPan)
        self.setPanButton.clicked.connect(self.setPan)

        self.setTiltButton = QPushButton(self.strings.PTT_SetTilt)
        self.setTiltButton.clicked.connect(self.setTilt)

        layout.addWidget(self.pan)
        layout.addWidget(self.setPanButton)
        layout.addWidget(self.tilt)
        layout.addWidget(self.setTiltButton)
        layout.addWidget(self.homeButton)
        self.setLayout(layout)

    def setPan(self):
        ptu = self.api.pancam.ptu
        ptu.pan = int(self.pan.text())

    def setTilt(self):
        ptu = self.api.pancam.ptu
        ptu.tilt = int(self.tilt.text())

    def home(self):
        ptu = self.api.pancam.ptu
        ptu.stow()
