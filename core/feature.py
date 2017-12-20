from typing import Tuple
import cv2
import numpy as np


class Feature:
    def __init__(self, key_point: cv2.KeyPoint, descriptor: np.ndarray):
        self.descriptor: np.ndarray = descriptor
        self._key_point: dict = {
            'x': key_point.pt[0],
            'y': key_point.pt[1],
            'angle': key_point.angle,
            'response': key_point.response,
            'octave': key_point.octave,
            'class_id': key_point.class_id
        }

    @property
    def key_point(self) -> cv2.KeyPoint:
        kp = self._key_point
        return cv2.KeyPoint(kp['x'], kp['y'],
                            kp['angle'],
                            kp['response'],
                            kp['octave'],
                            kp['class_id'])

    @property
    def angle(self) -> float:
        return self.key_point.angle

    @property
    def position(self) -> Tuple[float, float]:
        return self.key_point.pt
