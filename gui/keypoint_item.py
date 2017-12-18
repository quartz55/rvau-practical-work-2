from log import logger
from PyQt5 import (QtWidgets as qt,
                   QtGui as gui,
                   QtCore as qtc)


class KeypointItem(qt.QGraphicsItem):
    def __init__(self):
        super().__init__()
