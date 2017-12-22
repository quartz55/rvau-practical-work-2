from log import logger
from typing import Optional
from PyQt5 import (QtWidgets as qt,
                   QtGui as gui,
                   QtCore as qtc)
from PyQt5.QtCore import Qt
from core.augments import AugmentType


class AugmentItem(qt.QGraphicsItem):
    def __init__(self, type: AugmentType):
        super().__init__()
        self.type: AugmentType = type
        self._dragging: bool = False

        self.setCursor(Qt.PointingHandCursor)

    @property
    def dragging(self) -> bool:
        return self._dragging

    @dragging.setter
    def dragging(self, value: bool):
        self.setCursor(Qt.ClosedHandCursor if value else Qt.PointingHandCursor)


class BoxAugmentItem(AugmentItem):
    def __init__(self, width: int = 100, height: int = 100):
        super().__init__(AugmentType.BOX)
        self.width = width
        self.height = height

    def boundingRect(self) -> qtc.QRectF:
        return qtc.QRectF(0, 0, self.width, self.height)

    def paint(self, painter: gui.QPainter, option: qt.QStyleOptionGraphicsItem, widget: Optional[qt.QWidget] = ...):
        color = qtc.Qt.cyan
        painter.setPen(color)
        painter.drawRect(self.boundingRect())
