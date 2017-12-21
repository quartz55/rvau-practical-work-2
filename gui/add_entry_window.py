import os
from typing import Optional

from PyQt5 import (QtWidgets as qt,
                   QtGui as gui,
                   QtCore as qtc)

from core import Image, Matcher, Entry, Database
from gui.entry_editor_scene import EntryEditorScene, EntryEditorState
from gui.entry_editor_view import EntryEditorView
from log import logger


class AddEntryWindow(qt.QMainWindow):
    entry_saved = qtc.pyqtSignal(Entry)

    def __init__(self, database: Database, matcher: Matcher):
        super().__init__()
        self._database = database
        self.matcher: Matcher = matcher
        self.toolbar: qt.QToolBar = None
        self.tool_features: qt.QAction = None
        self.tool_save: qt.QAction = None
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

        load_act = self.toolbar_button('Load Image', 'Loads an image to be added to the database', 'Ctrl+O')
        load_act.triggered.connect(self.load_image)
        self.toolbar.addAction(load_act)

        self.tool_save = self.toolbar_button('Save Entry', 'Saves current image to database', 'Ctrl+S')
        self.tool_save.setDisabled(True)
        self.tool_save.triggered.connect(self.save_entry)
        self.toolbar.addAction(self.tool_save)

        self.tool_features = self.toolbar_button('Features', 'Calculates feature for current image', 'Ctrl+F')
        self.tool_features.setDisabled(True)
        self.tool_features.setCheckable(True)
        self.tool_features.toggled.connect(self.select_features)
        self.toolbar.addAction(self.tool_features)

        zoom_in_act = self.toolbar_button('Zoom In', shortcut='Ctrl++')
        zoom_in_act.triggered.connect(lambda: self.editor_view.scale(1.25, 1.25))
        self.toolbar.addAction(zoom_in_act)

        zoom_out_act = self.toolbar_button('Zoom Out', shortcut='Ctrl+-')
        zoom_out_act.triggered.connect(lambda: self.editor_view.scale(0.75, 0.75))
        self.toolbar.addAction(zoom_out_act)

        reset_zoom_act = self.toolbar_button('Reset Zoom', shortcut='Ctrl+0')
        reset_zoom_act.triggered.connect(lambda: self.editor_view.fit_to_entry())
        self.toolbar.addAction(reset_zoom_act)

    def load_image(self):
        filename, __ = qt.QFileDialog.getOpenFileName(self, 'Load Image', os.environ.get('HOME'),
                                                      'Images (*.png *.jpg)')
        if filename:
            logger.debug('Trying to load image: %s', filename)
            image = Image.from_file(filename)
            self.editor_scene.load_entry(image)

    def select_features(self, state: bool):
        entry = self.editor_scene.entry
        if entry is None:
            return
        if state and len(self.editor_scene.features) == 0:
            eq = self.matcher.histogram_equalization(entry['img'])
            hpf = self.matcher.highpass_filter(eq, 5)
            laplace = self.matcher.laplacian_gradient(eq)
            features = self.matcher.features(eq)
            self.editor_scene.add_features(features)
        self.editor_scene.state = EntryEditorState.SELECT_FEATURES if state else EntryEditorState.NONE
        self.editor_scene.set_features_visibility(state)

    def save_entry(self):
        features = self.editor_scene.selected_features
        if len(features) < 10:
            info_box = qt.QMessageBox(self)
            info_box.setIcon(qt.QMessageBox.Critical)
            info_box.setText("At least 10 features need to be selected")
            info_box.setInformativeText(
                "You only selected %d feature%s" % (len(features), '' if len(features) == 1 else 's'))
            return info_box.exec()
        entry = Entry('tmp', self.editor_scene.entry['img'], features, 'taj-mahal')
        self._database.add_entry(entry)
        info_box = qt.QMessageBox(self)
        info_box.setIcon(qt.QMessageBox.Information)
        info_box.setText("Saved successfully as '%s'" % entry.name)
        info_box.exec()
        self.entry_saved.emit(entry)

    def toolbar_button(self, text: str, tooltip: Optional[str] = None, shortcut: Optional[str] = None) -> qt.QAction:
        action = qt.QAction(text, self)
        tooltip = tooltip if tooltip is not None else text
        if shortcut is not None:
            action.setShortcut(shortcut)
            tooltip += "<br><b>%s</b>" % action.shortcut().toString()
        action.setToolTip(tooltip)
        return action

    def on_entry_change(self):
        self.tool_features.setDisabled(self.editor_scene.entry is None)
        self.tool_features.setChecked(False)
        self.tool_save.setDisabled(self.editor_scene.entry is None)

    def mouseMoveEvent(self, event: gui.QMouseEvent):
        status = 'Pos(x: %d, y: %d) ScenePos(x: %d, y: %d)' % (event.pos().x(), event.pos().y(),
                                                               self.editor_view.mapToScene(event.pos()).x(),
                                                               self.editor_view.mapToScene(event.pos()).y())
        self.statusBar().showMessage(status)

    def closeEvent(self, event):
        reply = qt.QMessageBox.question(self, 'Message',
                                        "You haven't saved the entry yet!<br>"
                                        "Are you sure you want to close?", qt.QMessageBox.Yes |
                                        qt.QMessageBox.No, qt.QMessageBox.No)

        if reply == qt.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
