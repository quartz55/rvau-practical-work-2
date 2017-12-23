import numpy as np
from core.image import Image
from PyQt5 import QtGui as gui


def qimage_to_numpy(image: gui.QImage):
    ptr = image.bits()
    w, h, d = image.width(), image.height(), image.depth()
    ptr.setsize(w * h * 4)
    return np.array(ptr).reshape(h, w, 4)


def numpy_to_qimage(src: np.array):
    shape = src.shape
    h, w = shape[0], shape[1]
    d = 1
    if len(shape) == 3:
        d = shape[2]
    return gui.QImage(src, w, h, w * d, gui.QImage.Format_RGB888 if d != 1 else gui.QImage.Format_Grayscale8)


def image_to_qimage(image: Image):
    return numpy_to_qimage(image.rgb)