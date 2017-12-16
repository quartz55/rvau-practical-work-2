from log import logger
from PyQt5 import (QtWidgets as qt,
                   QtGui as gui,
                   QtCore as qtc)

from core import Image, Matcher


class EntryEditor(qt.QWidget):
    entry_changed = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.entry: dict = None
        self.__matcher: Matcher = Matcher()
        self.__scene = qt.QGraphicsScene()
        self.__view = qt.QGraphicsView(self.__scene)

        v_layout = qt.QVBoxLayout()
        v_layout.addWidget(self.__view)

        self.setLayout(v_layout)

    def load_entry(self, img: Image):
        assert type(img) is Image
        h, w, d = img.dimensions
        q_image = gui.QImage(img.rgb, w, h, w * d, gui.QImage.Format_RGB888)
        self.__scene.addPixmap(gui.QPixmap(q_image))
        self.__scene.update()
        self.__view.fitInView(qtc.QRectF(0, 0, w, h), qtc.Qt.KeepAspectRatio)
        self.entry = dict(img=img,
                          id=None)
        self.entry_changed.emit()

    def calculate_features(self):
        if self.entry is not None:
            img = self.entry.get('img')
            processed = self.__matcher.histogram_equalization(img)
            kp, des = self.__matcher.features(processed)
            logger.info('Found %d features', len(kp))
            for keypoint in kp:
                
