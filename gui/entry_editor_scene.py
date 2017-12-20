from log import logger
from typing import List
from enum import Enum, unique, auto
from PyQt5 import (QtWidgets as qt,
                   QtGui as gui,
                   QtCore as qtc)
from PyQt5.QtCore import Qt
from core import Image, Feature
from gui.feature_item import FeatureItem


@unique
class EntryEditorState(Enum):
    NONE = auto()
    SELECT_FEATURES = auto()


class EntryEditorScene(qt.QGraphicsScene):
    entry_changed = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.entry: dict = None
        self.features: List[FeatureItem] = []
        self.state: EntryEditorState = EntryEditorState.NONE
        self._selection_rect: dict = None
        self._selection_rect_ui: qt.QGraphicsRectItem = None

    def load_entry(self, img: Image):
        self.state = EntryEditorState.NONE
        self.features.clear()
        self.clear()
        h, w, d = img.dimensions
        q_image = gui.QImage(img.rgb, w, h, w * d, gui.QImage.Format_RGB888)
        entry_item = self.addPixmap(gui.QPixmap(q_image))
        self.setSceneRect(entry_item.boundingRect())
        self.update()
        self.entry = {'id': None,
                      'img': img,
                      'gui': entry_item}
        self.entry_changed.emit()

    def add_features(self, features: List[Feature]):
        for f in self.features:
            self.removeItem(f)
        self.features.clear()
        for f in features:
            feature_item = FeatureItem(f)
            feature_item.setPos(*feature_item.position)
            self.addItem(feature_item)
            self.features.append(feature_item)
        self.update()

    def set_features_visibility(self, visibility: bool):
        for f in self.features:
            f.setVisible(visibility)
            f.update()

    @property
    def selected_features(self) -> List[Feature]:
        selected = []
        for i in self.selectedItems():
            if type(i) is FeatureItem:
                selected.append(i.feature)
        return selected

    def mousePressEvent(self, event: qt.QGraphicsSceneMouseEvent):
        if event.button() == Qt.LeftButton:
            pos = event.scenePos()
            if self.state == EntryEditorState.SELECT_FEATURES:
                self._selection_rect = {'from': (pos.x(), pos.y()), 'to': (pos.x(), pos.y())}
                self.update_selection_rect()

    def mouseReleaseEvent(self, event: qt.QGraphicsSceneMouseEvent):
        if self._selection_rect is not None:
            a, b = self._selection_rect['from'], self._selection_rect['to']
            top_left = qtc.QPointF(min(a[0], b[0]), min(a[1], b[1]))
            bottom_right = qtc.QPointF(max(a[0], b[0]), max(a[1], b[1]))
            rect = qtc.QRectF(top_left, bottom_right)
            in_selection = self.items(rect)
            if not event.modifiers() & Qt.ControlModifier:
                self.clearSelection()
            for selected in in_selection:
                selected.setSelected(True)
            self._selection_rect = None
            self.removeItem(self._selection_rect_ui)
            self._selection_rect_ui = None
            self.update()

    def mouseMoveEvent(self, event: qt.QGraphicsSceneMouseEvent):
        if self._selection_rect is not None:
            new_x, new_y = event.scenePos().x(), event.scenePos().y()
            self._selection_rect['to'] = (new_x, new_y)
            self.update_selection_rect()

    def update_selection_rect(self):
        if self._selection_rect is not None:
            # Update the dashed selection box
            a, b = self._selection_rect['from'], self._selection_rect['to']
            top_left = qtc.QPointF(min(a[0], b[0]), min(a[1], b[1]))
            bottom_right = qtc.QPointF(max(a[0], b[0]), max(a[1], b[1]))
            rect = qtc.QRectF(top_left, bottom_right)
            if self._selection_rect_ui is None:
                self._selection_rect_ui = self.addRect(rect)
                self._selection_rect_ui.setBrush(gui.QColor(32, 32, 32, 70))
                pen = gui.QPen(gui.QColor(234, 234, 234, 235), 2)
                self._selection_rect_ui.setPen(pen)
            else:
                self._selection_rect_ui.setRect(rect)
