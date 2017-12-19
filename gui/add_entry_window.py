import os

from PyQt5 import (QtWidgets as qt,
                   QtGui as gui,
                   QtCore as qtc)

from core import Image, Matcher
from gui.entry_editor_scene import EntryEditorScene
from gui.entry_editor_view import EntryEditorView
from log import logger


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
        self.editor_view = EntryEditorView(self.editor_scene)
        self.setCentralWidget(self.editor_view)

    def configure_window(self):
        self.setWindowTitle('New Database Entry')
        screen_size = gui.QGuiApplication.primaryScreen().availableSize()
        self.resize(int(screen_size.width() * 3 / 5), int(screen_size.height() * 3 / 5))
        self.grabGesture(qtc.Qt.PinchGesture)

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
        features_action.triggered.connect(self.calculate_features)
        self.tool_features = features_action
        self.toolbar.addAction(features_action)

        zoom_in_act = qt.QAction('Zoom In', self)
        zoom_in_act.setShortcut('Ctrl++')
        zoom_in_act.setToolTip('Zoom in')
        zoom_in_act.triggered.connect(lambda: self.editor_view.scale(1.25, 1.25))
        self.toolbar.addAction(zoom_in_act)

        zoom_out_act = qt.QAction('Zoom Out', self)
        zoom_out_act.setShortcut('Ctrl+-')
        zoom_out_act.setToolTip('Zoom Out')
        zoom_out_act.triggered.connect(lambda: self.editor_view.scale(0.75, 0.75))
        self.toolbar.addAction(zoom_out_act)

        reset_zoom_act = qt.QAction('Reset Zoom', self)
        reset_zoom_act.setShortcut('Ctrl+0')
        reset_zoom_act.setToolTip('Reset Zoom')
        reset_zoom_act.triggered.connect(lambda: self.editor_view.fit_to_entry())
        self.toolbar.addAction(reset_zoom_act)

    def load_image(self):
        filename, __ = qt.QFileDialog.getOpenFileName(self, 'Load Image', os.environ.get('HOME'), 'Image files (*.jpg)')
        if filename:
            logger.debug('Trying to load image: %s', filename)
            image = Image.from_file(filename)
            self.editor_scene.load_entry(image)

    def calculate_features(self):
        entry = self.editor_scene.entry
        if entry is None:
            return
        eq = self.matcher.histogram_equalization(entry['img'])
        features = self.matcher.features(eq)
        self.editor_scene.add_features(features)

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
