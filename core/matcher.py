from typing import Tuple, List

import cv2
import numpy as np

from core.feature import Feature
from core.image import Image

FLANN_INDEX_KDTREE = 1
FLANN_INDEX_LSH = 6
MIN_MATCH_COUNT = 10


class Matcher:
    def __init__(self):
        # sift = cv2.xfeatures2d.SIFT_create()
        # surf = cv2.xfeatures2d.SURF_create(100)
        self.__orb = cv2.ORB_create(nfeatures=1000)
        self.__surf = cv2.xfeatures2d.SURF_create(300)

    def features_raw(self, img: Image) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        # return self.__orb.detectAndCompute(img.src, None)
        return self.__surf.detectAndCompute(img.src, None)

    def features(self, img: Image) -> List[Feature]:
        key_points, descriptors = self.features_raw(img)
        final = []
        for kp, des in zip(key_points, descriptors):
            final.append(Feature(kp, des))
        return final

    def match(self, src_des: np.ndarray, target_des: np.ndarray):
        # index_params = dict(algorithm=FLANN_INDEX_LSH)
        # search_params = dict(checks=50)
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(src_des, target_des, k=2)
        # store all the good matches as per Lowe's ratio test.
        good = []
        for m, n in filter(lambda match: len(match) == 2, matches):
            if m.distance < 0.85 * n.distance:
                good.append(m)
        return good

    @staticmethod
    def highpass_filter(image: Image, freq=10) -> Image:
        f = np.fft.fft2(image.src)
        f_shift = np.fft.fftshift(f)
        rows, cols = image.dimensions
        crow, ccol = int(rows / 2), int(cols / 2)
        f_shift[crow - freq:crow + freq, ccol - freq:ccol + freq] = 0
        f_ishift = np.fft.ifftshift(f_shift)
        img_back = np.fft.ifft2(f_ishift)
        img_back = np.abs(img_back)
        return Image(np.uint8(img_back))

    @staticmethod
    def laplacian_gradient(image: Image):
        tmp = cv2.Laplacian(image.src, cv2.CV_64F)
        tmp = np.absolute(tmp)
        return Image(np.uint8(tmp))

    @staticmethod
    def histogram_equalization(img: Image) -> Image:
        # create a CLAHE object (Arguments are optional).
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(2, 2))
        equalized = clahe.apply(img.grayscale)
        return Image(equalized)
