import os
from typing import Optional, Tuple
from PyQt5 import (QtWidgets as qt,
                   QtGui as gui,
                   QtCore as qtc)
from PyQt5.QtCore import Qt
from core import Image, Matcher, Entry, Database
from core.augments import AugmentType
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
        self.editor_view.mouse_moved.connect(self.on_mouse_move)
        self.entry_name_combo: qt.QComboBox = None
        self.entry_group_combo: qt.QComboBox = None
        self.augments_group: qt.QButtonGroup = None
        self.sidebar = self.create_sidebar()

        splitter = qt.QSplitter(Qt.Horizontal, self)

        splitter.addWidget(self.editor_view)
        splitter.addWidget(self.sidebar)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

        self.setCentralWidget(splitter)

    def create_sidebar(self) -> qt.QWidget:
        sidebar = qt.QWidget()
        layout = qt.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        area = qt.QScrollArea()
        area.setFrameStyle(0)
        content = qt.QWidget()
        content_layout = qt.QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 5)

        entries = self._database.entries
        info_box = qt.QWidget()
        form = qt.QFormLayout()
        self.entry_name_combo = qt.QComboBox(info_box)
        self.entry_name_combo.setEditable(True)
        for e in entries:
            self.entry_name_combo.addItem(e.name)
        self.entry_name_combo.setEditText('')
        form.addRow(qt.QLabel('Name:', info_box), self.entry_name_combo)
        self.entry_group_combo = qt.QComboBox(info_box)
        self.entry_group_combo.setEditable(True)
        for e in entries:
            self.entry_group_combo.addItem(e.group)
        self.entry_group_combo.setEditText('')
        form.addRow(qt.QLabel('Group:', info_box), self.entry_group_combo)
        info_box.setLayout(form)
        content_layout.addWidget(info_box)

        self.augments_group = qt.QButtonGroup(self)
        self.augments_group.setExclusive(False)
        self.augments_group.buttonClicked[int].connect(self.augment_clicked)
        augments_widget = qt.QWidget(sidebar)
        augments_layout = qt.QGridLayout()

        box_augment_widget, box_augment_button = self.toolbox_button("Box Augment", "Draws a box")
        self.augments_group.addButton(box_augment_button, AugmentType.BOX.value)
        augments_layout.addWidget(box_augment_widget, 0, 0)

        #text_augment_widget, text_augment_button = self.toolbox_button("Text Augment", "Draws text")
        #self.augments_group.addButton(text_augment_button, AugmentType.TEXT.value)
        #augments_layout.addWidget(text_augment_widget, 0, 1)

        augments_widget.setLayout(augments_layout)

        toolbox = qt.QToolBox(sidebar)
        toolbox.addItem(augments_widget, "Augments")
        content_layout.addWidget(toolbox)

        content_layout.setSizeConstraint(qt.QLayout.SetMinimumSize)
        content.setLayout(content_layout)
        area.setWidget(content)
        layout.addWidget(area)
        sidebar.setLayout(layout)
        return sidebar

    def configure_window(self):
        self.setWindowTitle('New Database Entry')
        screen_size = gui.QGuiApplication.primaryScreen().availableSize()
        self.resize(int(screen_size.width() * 3 / 5), int(screen_size.height() * 3 / 5))
        self.grabGesture(qtc.Qt.PinchGesture)
        self.statusBar().showMessage("Load an image to start")

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
            features = self.matcher.features(eq)
            self.editor_scene.add_features(features)
        self.editor_scene.state = EntryEditorState.SELECT_FEATURES if state else EntryEditorState.NONE
        self.editor_scene.set_features_visibility(state)

    def save_entry(self):
        name = self.entry_name_combo.currentText()
        group = self.entry_group_combo.currentText()
        if not name:
            info_box = qt.QMessageBox(self)
            info_box.setIcon(qt.QMessageBox.Critical)
            info_box.setText("Name can't be empty!")
            return info_box.exec()
        features = self.editor_scene.selected_features
        if len(features) < 10:
            info_box = qt.QMessageBox(self)
            info_box.setIcon(qt.QMessageBox.Critical)
            info_box.setText("At least 10 features need to be selected")
            info_box.setInformativeText(
                "You only selected %d feature%s" % (len(features), '' if len(features) == 1 else 's'))
            return info_box.exec()
        augments = [a.augment() for a in self.editor_scene.augments]
        entry = Entry(name, self.editor_scene.entry['img'], features,
                      augments=augments,
                      group=group)
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

    def toolbox_button(self,
                       text: str,
                       tooltip: Optional[str] = None,
                       shortcut: Optional[str] = None) -> Tuple[qt.QWidget, qt.QToolButton]:
        button = qt.QToolButton()
        button.setText(text)
        button.setCheckable(True)
        button.setMinimumSize(50, 50)
        tooltip = tooltip if tooltip is not None else text
        if shortcut is not None:
            button.setShortcut(shortcut)
            tooltip += "<br><b>%s</b>" % button.shortcut().toString()
        button.setToolTip(tooltip)

        grid = qt.QGridLayout()
        grid.addWidget(button, 0, 0, Qt.AlignCenter)
        grid.addWidget(qt.QLabel("Box"), 1, 0, Qt.AlignCenter)
        widget = qt.QWidget()
        widget.setLayout(grid)
        return widget, button

    def augment_clicked(self, id: int):
        augment = AugmentType(id)
        clicked = self.augments_group.button(id)
        for button in self.augments_group.buttons():
            if clicked != button:
                button.setChecked(False)

        if clicked.isChecked():
            logger.info("Changing augment to %s", augment.name)
            self.select_features(False)
            if augment is AugmentType.TEXT:
                self.editor_scene.state = EntryEditorState.INSERT_AUGMENT_TEXT
            else:
                self.editor_scene.state = EntryEditorState.INSERT_AUGMENT_ITEM
                self.editor_scene.augment_type = augment
        else:
            self.editor_scene.state = EntryEditorState.NONE

    def on_entry_change(self):
        self.tool_features.setDisabled(self.editor_scene.entry is None)
        self.tool_features.setChecked(False)
        self.tool_save.setDisabled(self.editor_scene.entry is None)
        if self.editor_scene.entry is None:
            self.statusBar().showMessage("Load an image to start")

    def on_mouse_move(self, scene_position: Tuple[float, float]):
        if self.editor_scene.entry is None:
            return
        status = '(x: {:d}, y: {:d})'.format(int(scene_position[0]), int(scene_position[1]))
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
