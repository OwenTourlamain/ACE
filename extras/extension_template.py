# -- extension_template.py - template file for ace-ng extesion modules --
# Author:     Owen Tourlamain
# Supervisor: Dr. Laurence Tyler
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Tab(QWidget):

    def __init__(self, config, strings, api, verbose):
        super().__init__()
        self.verbose = verbose
        self.config = config
        self.strings = strings
        self.api = api
        self.title = ""
