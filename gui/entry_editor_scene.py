from enum import Enum, unique, auto

from PyQt5 import (QtWidgets as qt,
                   QtGui as gui,
                   QtCore as qtc)
from PyQt5.QtCore import Qt

from core import Image
from log import logger


@unique
class EntryEditorState(Enum):
    NONE = auto()
    SELECT_FEATURES = auto()


class EntryEditorScene(qt.QGraphicsScene):
    entry_changed = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.entry: dict = None
        self.features = []
        self._selection_rect: dict = None
        self._selection_rect_ui: qt.QGraphicsRectItem = None

    def load_entry(self, img: Image):
        assert type(img) is Image
        h, w, d = img.dimensions
        q_image = gui.QImage(img.rgb, w, h, w * d, gui.QImage.Format_RGB888)
        self.clear()
        self.addPixmap(gui.QPixmap(q_image))
        self.update()
        self.entry = {'img': img, 'id': None}
        self.entry_changed.emit()

    def add_features(self, features):
        pass

    def mousePressEvent(self, event: qt.QGraphicsSceneMouseEvent):
        if event.button() == Qt.LeftButton:
            pos = event.scenePos()
            self._selection_rect = {'from': (pos.x(), pos.y()), 'to': (pos.x(), pos.y())}
            self.update_selection_rect()

    def mouseReleaseEvent(self, event: qt.QGraphicsSceneMouseEvent):
        if self._selection_rect is not None:
            self._selection_rect = None
            self.removeItem(self._selection_rect_ui)
            self._selection_rect_ui = None

    def mouseMoveEvent(self, event: qt.QGraphicsSceneMouseEvent):
        if self._selection_rect is not None:
            new_x, new_y = event.scenePos().x(), event.scenePos().y()
            self._selection_rect['to'] = (new_x, new_y)
            self.update_selection_rect()

    def update_selection_rect(self):
        if self._selection_rect is not None:
            a, b = self._selection_rect['from'], self._selection_rect['to']
            top_left = qtc.QPointF(min(a[0], b[0]), min(a[1], b[1]))
            bottom_right = qtc.QPointF(max(a[0], b[0]), max(a[1], b[1]))
            rect = qtc.QRectF(top_left, bottom_right)
            if self._selection_rect_ui is None:
                self._selection_rect_ui = self.addRect(rect)
                pen = gui.QPen(Qt.black, 1, Qt.CustomDashLine)
                pen.setDashPattern([4, 4])
                self._selection_rect_ui.setPen(pen)
            else:
                self._selection_rect_ui.setRect(rect)
