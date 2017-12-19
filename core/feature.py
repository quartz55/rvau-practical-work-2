from typing import Tuple
import cv2
import numpy as np


class Feature:
    def __init__(self, key_point: cv2.KeyPoint, descriptor: np.ndarray):
        self.descriptor: np.ndarray = descriptor
        self.key_point: cv2.KeyPoint = key_point

    @property
    def angle(self) -> float:
        return self.key_point.angle

    @property
    def position(self) -> Tuple[float, float]:
        return self.key_point.pt
