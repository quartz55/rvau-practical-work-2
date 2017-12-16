import os

from PyQt5 import (QtWidgets as qt,
                   QtGui as gui,
                   QtCore as qtc)

from core import Image
from gui.entry_editor import EntryEditor
from log import logger


class AddEntryWindow(qt.QMainWindow):
    def __init__(self):
        super().__init__()
        self.configure_window()
        self.configure_toolbar()

        self.entry_editor = EntryEditor()
        self.entry_editor.entry_changed.connect(self.on_entry_change)
        self.setCentralWidget(self.entry_editor)

    def configure_window(self):
        self.setWindowTitle('New Database Entry')
        self.setGeometry(0, 0, 800, 400)

    def configure_toolbar(self):
        self.toolbar: qt.QToolBar = self.addToolBar('Main Toolbar')

        load_action = qt.QAction('Load Image', self)
        load_action.setShortcut('Ctrl+O')
        load_action.setToolTip('Loads an image to be added to the database')
        load_action.triggered.connect(self.load_image)
        self.toolbar.addAction(load_action)

        features_action = qt.QAction('Features', self)
        features_action.setShortcut('Ctrl+F')
        features_action.setToolTip('Calculates feature for current image')
        features_action.triggered.connect(lambda: self.entry_editor.calculate_features())
        features_action.setDisabled(True)
        self.tool_features = features_action
        self.toolbar.addAction(features_action)

    def load_image(self):
        filename, __ = qt.QFileDialog.getOpenFileName(self, 'Load Image', os.environ.get('HOME'), 'Image files (*.jpg)')
        logger.debug('Trying to load image: %s', filename)
        image = Image.from_file(filename)
        self.entry_editor.load_entry(image)

    def on_entry_change(self):
        logger.debug('Entry changed'),
        self.tool_features.setDisabled(self.entry_editor.entry is None)

    def closeEvent(self, event):
        reply = qt.QMessageBox.question(self, 'Message',
                                        "You haven't saved the entry yet!\n"
                                        "Are you sure you want to close?", qt.QMessageBox.Yes |
                                        qt.QMessageBox.No, qt.QMessageBox.No)

        if reply == qt.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
