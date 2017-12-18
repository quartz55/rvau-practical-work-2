from log import logger
from PyQt5 import (QtWidgets as qt,
                   QtGui as gui,
                   QtCore as qtc)

from core import Image, Matcher
import cv2


class EntryEditorScene(qt.QGraphicsScene):
    entry_changed = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.entry: dict = None
        self.__matcher: Matcher = Matcher()

    def load_entry(self, img: Image):
        assert type(img) is Image
        h, w, d = img.dimensions
        q_image = gui.QImage(img.rgb, w, h, w * d, gui.QImage.Format_RGB888)
        self.__scene.clear()
        self.__scene.addPixmap(gui.QPixmap(q_image))
        self.__scene.update()
        self.__view.fitInView(self.__scene.itemsBoundingRect(), qtc.Qt.KeepAspectRatio)
        self.entry = {'img': img, 'id': None}
        self.entry_changed.emit()

    def calculate_features(self):
        if self.entry is not None:
            img = self.entry.get('img')
            processed = self.__matcher.histogram_equalization(img)
            kp, des = self.__matcher.features(processed)
            logger.info('Found %d features', len(kp))
            for keypoint in kp:
                x, y = keypoint.pt
                self.__scene.addEllipse(x, y, 5, 5, qtc.Qt.darkRed)

            self.__scene.update()

    def resizeEvent(self, event: gui.QResizeEvent):
        self.__view.fitInView(self.__scene.itemsBoundingRect(), qtc.Qt.KeepAspectRatio)
