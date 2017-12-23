from enum import Enum, unique, auto
from typing import List, Set, Tuple

from PyQt5 import (QtWidgets as qt,
                   QtGui as gui,
                   QtCore as qtc)
from PyQt5.QtCore import Qt

import math
from core import Image, Feature
from core.augments import AugmentType
from gui.augment_items import AugmentItem, BoxAugmentItem, ArrowAugmentItem, EllipseAugmentItem
from gui.feature_item import FeatureItem


@unique
class EntryEditorState(Enum):
    NONE = auto()
    SELECT_FEATURES = auto()
    INSERT_AUGMENT_ITEM = auto()
    INSERT_AUGMENT_TEXT = auto()


class EntryEditorScene(qt.QGraphicsScene):
    entry_changed = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.state: EntryEditorState = EntryEditorState.NONE
        self.entry: dict = None
        self.features: List[FeatureItem] = []
        self._selected_features: Set[FeatureItem] = set()
        self._clicked: List[FeatureItem] = []
        self._selection_rect: dict = None
        self._selection_rect_ui: qt.QGraphicsRectItem = None

        self.augments: Set[AugmentItem] = set()
        self.augment_type: AugmentType = None
        self._dragging: AugmentItem = None
        self._selected: AugmentItem = None
        self._item_start_point: Tuple[float, float] = None
        self._item: AugmentItem = None

        self.delete_act = qt.QAction('Delete', self)
        self.delete_act.setToolTip('Removes augment from scene')
        self.delete_act.triggered.connect(self.delete_augment)

    def load_entry(self, img: Image):
        self.state = EntryEditorState.NONE
        self.features.clear()
        self._selected = None
        self._dragging = None
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
        self._selected_features.clear()
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
        return [f.feature for f in self._selected_features]

    def delete_augment(self):
        if self._selected:
            self.augments.remove(self._selected)
            self.removeItem(self._selected)
            self._selected = None
            self.update()

    def contextMenuEvent(self, event: qt.QGraphicsSceneContextMenuEvent):
        item = self.itemAt(event.scenePos(), gui.QTransform())
        item = item if item and isinstance(item, AugmentItem) else self._selected
        if item:
            self._selected = item
            context_menu = qt.QMenu()
            context_menu.addAction(self.delete_act)
            context_menu.exec(event.screenPos())
            event.accept()
        else:
            event.ignore()

    def mousePressEvent(self, event: qt.QGraphicsSceneMouseEvent):
        if event.button() != Qt.LeftButton:
            return
        pos = event.scenePos()
        if self.state is EntryEditorState.SELECT_FEATURES:
            self._clicked = list(filter(lambda i: type(i) is FeatureItem, self.items(pos)))
            self._selection_rect = {'from': (pos.x(), pos.y()), 'to': (pos.x(), pos.y())}
        elif self.state is EntryEditorState.INSERT_AUGMENT_ITEM:
            self._item_start_point = (pos.x(), pos.y())
        elif self.state is EntryEditorState.NONE:
            item = self.itemAt(event.scenePos(), gui.QTransform())
            item = item if item and isinstance(item, AugmentItem) else None
            self._dragging = item
            if self._selected and item != self._selected:
                self._selected.selected = False
            self._selected = item
            if self._selected:
                self._selected.selected = True
            self.update()
        event.accept()

    def mouseReleaseEvent(self, event: qt.QGraphicsSceneMouseEvent):
        if (self.state is EntryEditorState.SELECT_FEATURES and
                self._selection_rect is not None):
            a, b = self._selection_rect['from'], self._selection_rect['to']
            top_left = qtc.QPointF(min(a[0], b[0]), min(a[1], b[1]))
            bottom_right = qtc.QPointF(max(a[0], b[0]), max(a[1], b[1]))
            rect = qtc.QRectF(top_left, bottom_right)
            in_selection = self.items(rect)
            in_selection.extend(self._clicked)
            self._clicked.clear()
            ctrl = event.modifiers() & Qt.ControlModifier
            shift = event.modifiers() & Qt.ShiftModifier
            if not ctrl:
                self.clear_selected_features()
            for item in in_selection:
                if type(item) is FeatureItem:
                    item.selected = not shift
                    if not shift:
                        self._selected_features.add(item)
                    else:
                        self._selected_features.discard(item)
            self._selection_rect = None
            self.removeItem(self._selection_rect_ui)
            self._selection_rect_ui = None
            self.update()
        elif self.state is EntryEditorState.INSERT_AUGMENT_ITEM:
            if self._item:
                self._item.drawing = False
                self.augments.add(self._item)
                self._item_start_point = None
                self._item = None
                self.update()
        elif self.state is EntryEditorState.NONE:
            if self._dragging:
                self._dragging.dragging = False
                self._dragging = None
                self.update()

        event.accept()

    def mouseMoveEvent(self, event: qt.QGraphicsSceneMouseEvent):
        if self.state is EntryEditorState.SELECT_FEATURES and self._selection_rect is not None:
            new_x, new_y = event.scenePos().x(), event.scenePos().y()
            self._selection_rect['to'] = (new_x, new_y)
            self.update_selection_rect()
        elif self.state is EntryEditorState.INSERT_AUGMENT_ITEM:
            if self.augment_type is AugmentType.BOX and self._item_start_point:
                if not self._item:
                    self._item = BoxAugmentItem(0, 0)
                    self._item.setPos(*self._item_start_point)
                    self._item.drawing = True
                    self.addItem(self._item)
                box = self._item
                box.width = event.scenePos().x() - self._item_start_point[0]
                box.height = event.scenePos().y() - self._item_start_point[1]
                self.update()
            elif self.augment_type is AugmentType.ARROW and self._item_start_point:
                if not self._item:
                    self._item = ArrowAugmentItem(0)
                    self._item.setPos(*self._item_start_point)
                    self._item.drawing = True
                    self.addItem(self._item)
                arrow = self._item
                vec = (event.scenePos().x() - self._item_start_point[0], event.scenePos().y() - self._item_start_point[1])
                arrow.length = math.sqrt(pow(vec[0], 2) +
                                         pow(vec[1], 2))
                arrow.setRotation(math.degrees(math.atan2(vec[1], vec[0])))
                self.update()
            elif self.augment_type is AugmentType.ELLIPSE and self._item_start_point:
                if not self._item:
                    self._item = EllipseAugmentItem(0, 0)
                    self._item.setPos(*self._item_start_point)
                    self._item.drawing = True
                    self.addItem(self._item)
                ellipse = self._item
                ellipse.width = event.scenePos().x() - self._item_start_point[0]
                ellipse.height = event.scenePos().y() - self._item_start_point[1]
                self.update()
        elif self.state is EntryEditorState.NONE and self._dragging is not None:
            curr = (event.scenePos().x(), event.scenePos().y())
            prev = (event.lastScenePos().x(), event.lastScenePos().y())
            delta = (curr[0] - prev[0], curr[1] - prev[1])
            self._dragging.dragging = True
            self._dragging.moveBy(*delta)
            self.update()
        event.accept()

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
                pen = gui.QPen(gui.QColor(255, 255, 255, 100), 1)
                self._selection_rect_ui.setPen(pen)
            else:
                self._selection_rect_ui.setRect(rect)

    def clear_selected_features(self):
        for f in self._selected_features:
            f.selected = False
        self._selected_features.clear()
