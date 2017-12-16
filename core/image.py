import cv2
import os
import numpy as np


class Image:
    def __init__(self, data):
        assert type(data) is np.ndarray, 'Data must be a numpy compatible array'
        self.src = data
        self.__grayscale = None
        self.__rgb = None

    @classmethod
    def from_file(cls, path):
        return cls(cv2.imread(path))

    @property
    def dimensions(self):
        return np.shape(self.src)

    @property
    def grayscale(self):
        if self.__grayscale is None:
            self.__grayscale = cv2.cvtColor(self.src, cv2.COLOR_BGR2GRAY)
        return self.__grayscale

    @property
    def rgb(self):
        if self.__rgb is None:
            self.__rgb = cv2.cvtColor(self.src, cv2.COLOR_BGR2RGB)
        return self.__rgb