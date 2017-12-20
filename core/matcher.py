from log import logger
from typing import Tuple, List, Iterator
import cv2
import numpy as np
from core.image import Image
from core.feature import Feature

FLANN_INDEX_KDTREE = 1
FLANN_INDEX_LSH = 6
MIN_MATCH_COUNT = 10


class Matcher:
    def __init__(self):
        # sift = cv2.xfeatures2d.SIFT_create()
        # surf = cv2.xfeatures2d.SURF_create(100)
        self.__orb = cv2.ORB_create(nfeatures=1000)

    def features(self, img: Image) -> List[Feature]:
        key_points, descriptors = self.__orb.detectAndCompute(img.src, None)
        final = []
        for kp, des in zip(key_points, descriptors):
            final.append(Feature(kp, des))
        return final

    def match(self, src_des: np.ndarray, target_des: np.ndarray):
        index_params = dict(algorithm=FLANN_INDEX_LSH)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(src_des, target_des, k=2)
        # store all the good matches as per Lowe's ratio test.
        good = []
        for m, n in filter(lambda match: len(match) == 2, matches):
            if m.distance < 0.7 * n.distance:
                good.append(m)
        return good

    @staticmethod
    def histogram_equalization(img: Image) -> Image:
        # create a CLAHE object (Arguments are optional).
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(2, 2))
        equalized = clahe.apply(img.grayscale)
        return Image(equalized)