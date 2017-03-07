from PyQt5.QtWidgets import *

class Tab(QWidget): # HACK: Make class load dynamically
    """docstring for MultiImageCap."""

    def __init__(self, config, strings, api):
        super().__init__()
        self.config = config
        self.strings = strings
        self.api = api
        self.title = self.strings.MIT_Title

        self.initTab()

    def initTab(self):
        layout = QFormLayout()
        layout.addRow("Name2",QLineEdit())
        layout.addRow("Address2",QLineEdit())
        self.setLayout(layout)
