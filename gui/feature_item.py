from log import logger
import typing
from PyQt5 import (QtWidgets as qt,
                   QtGui as gui,
                   QtCore as qtc)
from core import Feature


class FeatureItem(qt.QGraphicsItem):
    def __init__(self, feature: Feature, diameter=2.5):
        super().__init__()
        self.diameter = diameter
        self.feature: Feature = feature
        self.setFlag(qt.QGraphicsItem.ItemIsSelectable)
        self.setCursor(qtc.Qt.PointingHandCursor)

    @property
    def position(self) -> typing.Tuple[float, float]:
        return self.feature.position

    def paint(self, painter: gui.QPainter, option: qt.QStyleOptionGraphicsItem, widget: typing.Optional[qt.QWidget] = ...):
        color = qtc.Qt.darkRed
        if self.isSelected():
            color = qtc.Qt.green
        painter.setBrush(color)
        painter.drawEllipse(0, 0, self.diameter, self.diameter)

    def boundingRect(self) -> qtc.QRectF:
        return qtc.QRectF(-self.diameter/2, -self.diameter/2, self.diameter, self.diameter)
