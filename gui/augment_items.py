from log import logger
from typing import Optional
from PyQt5 import (QtWidgets as qt,
                   QtGui as gui,
                   QtCore as qtc)
from PyQt5.QtCore import Qt
import math
from core.augments import AugmentType, Augment, BoxAugment, ArrowAugment, EllipseAugment


class AugmentItem(qt.QGraphicsItem):
    def __init__(self, type: AugmentType):
        super().__init__()
        self.type: AugmentType = type
        self._dragging: bool = False
        self._selected: bool = False
        self._drawing: bool = False
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

    @property
    def drawing(self) -> bool:
        return self._drawing

    @drawing.setter
    def drawing(self, value: bool):
        self._drawing = value


class BoxAugmentItem(AugmentItem):
    def __init__(self, width: float = 100, height: float = 100):
        super().__init__(AugmentType.BOX)
        self._width: float = width
        self._height: float = height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width: float):
        self.prepareGeometryChange()
        self._width = width

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height: float):
        self.prepareGeometryChange()
        self._height = height

    def boundingRect(self) -> qtc.QRectF:
        return qtc.QRectF(0, 0, self.width + 5, self.height + 5)

    def paint(self, painter: gui.QPainter, option: qt.QStyleOptionGraphicsItem, widget: Optional[qt.QWidget] = ...):
        color = gui.QColor(255, 0, 0, 255)
        if self.dragging:
            color.setAlphaF(0.7)
        if self._selected:
            color.setGreen(200)
        if self._drawing:
            color = gui.QColor(120, 32, 32, 100)
        pen = gui.QPen()
        pen.setColor(color)
        pen.setWidth(5)
        painter.setPen(pen)
        painter.drawRect(2, 2, int(self.width), int(self.height))

    def augment(self):
        return BoxAugment(self.x(), self.y(), self.width, self.height)


class EllipseAugmentItem(AugmentItem):
    def __init__(self, width: float = 100, height: float = 100):
        super().__init__(AugmentType.BOX)
        self._width: float = width
        self._height: float = height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width: float):
        self.prepareGeometryChange()
        self._width = width

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height: float):
        self.prepareGeometryChange()
        self._height = height

    def boundingRect(self) -> qtc.QRectF:
        return qtc.QRectF(0, 0, self.width + 5, self.height + 5)

    def paint(self, painter: gui.QPainter, option: qt.QStyleOptionGraphicsItem, widget: Optional[qt.QWidget] = ...):
        color = gui.QColor(255, 0, 0, 255)
        if self.dragging:
            color.setAlphaF(0.7)
        if self._selected:
            color.setGreen(200)
        if self._drawing:
            color = gui.QColor(120, 32, 32, 100)
        pen = gui.QPen()
        pen.setColor(color)
        pen.setWidth(5)
        painter.setPen(pen)
        painter.drawEllipse(3, 3, int(self.width), int(self.height))

    def augment(self):
        return EllipseAugment(self.x(), self.y(), self.width, self.height)


class ArrowAugmentItem(AugmentItem):
    def __init__(self, length: float = 100):
        super().__init__(AugmentType.BOX)
        self._length: float = length
        self._pen = gui.QPen(Qt.black, 5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, length):
        self.prepareGeometryChange()
        self._length = length

    def boundingRect(self) -> qtc.QRectF:
        return qtc.QRectF(-5, -25, self.length + 5, 40 + 5)

    def paint(self, painter: gui.QPainter, option: qt.QStyleOptionGraphicsItem, widget: Optional[qt.QWidget] = ...):
        color = gui.QColor(255, 0, 0, 255)
        if self.dragging:
            color.setAlphaF(0.7)
        if self._selected:
            color.setGreen(200)
        if self._drawing:
            color = gui.QColor(120, 32, 32, 100)
        self._pen.setColor(color)
        painter.setPen(self._pen)

        arrow = gui.QPolygonF()
        arrow.append(qtc.QPointF(0, 10))
        arrow.append(qtc.QPointF(0, -10))
        arrow.append(qtc.QPointF(self.length - 50, -10))
        arrow.append(qtc.QPointF(self.length - 50, -20))
        arrow.append(qtc.QPointF(self.length, 0))
        arrow.append(qtc.QPointF(self.length - 50, 20))
        arrow.append(qtc.QPointF(self.length - 50, 10))
        arrow.append(qtc.QPointF(0, 10))
        painter.drawPolyline(arrow)

    def augment(self) -> Augment:
        return ArrowAugment(self.x(), self.y(), self.length, self.rotation())
