import os

from log import logger
from PyQt5 import (QtWidgets as qt,
                   QtGui as gui,
                   QtCore as qtc)
from core import Image, Matcher
from gui.entry_editor_scene import EntryEditorScene


class AddEntryWindow(qt.QMainWindow):
    def __init__(self):
        super().__init__()
        self.matcher: Matcher = Matcher()
        self.toolbar: qt.QToolBar = None
        self.tool_features: qt.QAction = None
        self.configure_window()
        self.configure_toolbar()

        self.editor_scene = EntryEditorScene()
        self.editor_scene.entry_changed.connect(self.on_entry_change)
        self.editor_view = qt.QGraphicsView(self.editor_scene)
        self.setCentralWidget(self.editor_view)

    def configure_window(self):
        self.setWindowTitle('New Database Entry')
        screen_size = gui.QGuiApplication.primaryScreen().availableSize()
        self.resize(int(screen_size.width() * 3 / 5), int(screen_size.height() * 3 / 5))

    def configure_toolbar(self):
        self.toolbar = self.addToolBar('Main Toolbar')

        load_action = qt.QAction('Load Image', self)
        load_action.setShortcut('Ctrl+O')
        load_action.setToolTip('Loads an image to be added to the database')
        load_action.triggered.connect(self.load_image)
        self.toolbar.addAction(load_action)

        features_action = qt.QAction('Features', self)
        features_action.setShortcut('Ctrl+F')
        features_action.setToolTip('Calculates feature for current image')
        features_action.setDisabled(True)
        self.tool_features = features_action
        self.toolbar.addAction(features_action)

    def load_image(self):
        filename, __ = qt.QFileDialog.getOpenFileName(self, 'Load Image', os.environ.get('HOME'), 'Image files (*.jpg)')
        logger.debug('Trying to load image: %s', filename)
        image = Image.from_file(filename)
        self.editor_scene.load_entry(image)

    def calculate_features(self):
        if self.editor_scene.entry is None:
            return

    def on_entry_change(self):
        logger.debug('Entry changed'),
        self.tool_features.setDisabled(self.editor_scene.entry is None)

    def closeEvent(self, event):
        reply = qt.QMessageBox.question(self, 'Message',
                                        "You haven't saved the entry yet!\n"
                                        "Are you sure you want to close?", qt.QMessageBox.Yes |
                                        qt.QMessageBox.No, qt.QMessageBox.No)

        if reply == qt.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
