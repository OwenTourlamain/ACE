from PyQt5.QtWidgets import *

class Tab(QWidget): # HACK: Make class load dynamically
    """docstring for PanTiltTab."""

    def __init__(self, config, strings, api):
        super().__init__()
        self.config = config
        self.strings = strings
        self.api = api
        self.title = self.strings.MIT_Title

        self.initTab()

    def initTab(self):
        layout = QFormLayout()
        layout.addRow("Name3",QLineEdit())
        layout.addRow("Address3",QLineEdit())
        self.setLayout(layout)
