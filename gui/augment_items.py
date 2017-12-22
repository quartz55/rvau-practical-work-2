from log import logger
from typing import Optional
from PyQt5 import (QtWidgets as qt,
                   QtGui as gui,
                   QtCore as qtc)
from PyQt5.QtCore import Qt
from core.augments import AugmentType, Augment, BoxAugment


class AugmentItem(qt.QGraphicsItem):
    def __init__(self, type: AugmentType):
        super().__init__()
        self.type: AugmentType = type
        self._dragging: bool = False
        self._selected: bool = False

        self.setCursor(Qt.PointingHandCursor)

    def augment(self) -> Augment:
        raise NotImplementedError

    @property
    def dragging(self) -> bool:
        return self._dragging

    @dragging.setter
    def dragging(self, value: bool):
        self.setCursor(Qt.ClosedHandCursor if value else Qt.PointingHandCursor)
        self._dragging = value

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool):
        self._selected = value


class BoxAugmentItem(AugmentItem):
    def __init__(self, width: int = 100, height: int = 100):
        super().__init__(AugmentType.BOX)
        self.width = width
        self.height = height

    def boundingRect(self) -> qtc.QRectF:
        return qtc.QRectF(0, 0, self.width, self.height)

    def paint(self, painter: gui.QPainter, option: qt.QStyleOptionGraphicsItem, widget: Optional[qt.QWidget] = ...):
        color = gui.QColor(255, 0, 0, 255)
        if self.dragging:
            color.setAlphaF(0.7)
        if self._selected:
            color.setGreen(200)
        pen = gui.QPen()
        pen.setColor(color)
        pen.setWidth(5)
        painter.setPen(pen)
        painter.drawRect(self.boundingRect())

    def augment(self):
        return BoxAugment(self.x(), self.y(), self.width, self.height)
