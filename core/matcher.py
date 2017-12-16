import cv2
import numpy as np
from core.image import Image
from log import logger

FLANN_INDEX_KDTREE = 1
FLANN_INDEX_LSH = 6
MIN_MATCH_COUNT = 10


class Matcher:
    def __init__(self):
        # sift = cv2.xfeatures2d.SIFT_create()
        # surf = cv2.xfeatures2d.SURF_create(100)
        self.__orb = cv2.ORB_create(nfeatures=1000)

    def features(self, img):
        assert type(img) is Image
        return self.__orb.detectAndCompute(img.src, None)

    @staticmethod
    def histogram_equalization(img):
        # create a CLAHE object (Arguments are optional).
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(2, 2))
        equalized = clahe.apply(img.grayscale)
        return Image(equalized)

# def match_features(src_des, target_des):
#     index_params = dict(algorithm=FLANN_INDEX_LSH)
#     search_params = dict(checks=50)
#     flann = cv2.FlannBasedMatcher(index_params, search_params)
#     matches = flann.knnMatch(src_des, target_des, k=2)
#     # store all the good matches as per Lowe's ratio test.
#     good = []
#     for m, n in filter(lambda match: len(match) == 2, matches):
#         if m.distance < 0.7 * n.distance:
#             good.append(m)
#
#     return good
#
#
# def draw_matches(src_img, dest_img, src_kp, dest_kp, matches):
#     src_pts = np.float32([src_kp[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
#     dest_pts = np.float32([dest_kp[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
#     matrix, mask = cv2.findHomography(src_pts, dest_pts, cv2.RANSAC, 5.0)
#     matches_mask = mask.ravel().tolist()
#     h, w, d = src_img.shape
#     pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
#     dst = cv2.perspectiveTransform(pts, matrix)
#     dest_outline = cv2.polylines(dest_img, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
#     draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
#                        singlePointColor=None,
#                        matchesMask=matches_mask,  # draw only inliers
#                        flags=2)
#     return cv2.drawMatches(src_img, src_kp, dest_outline, dest_kp, matches, None, **draw_params)
#
# def match_image(img):
#     kp, des = orb.detectAndCompute(img, None)
#     matches = match_features(des_mark, des)
#
#     if len(matches) >= MIN_MATCH_COUNT:
#         matches_img = draw_matches(mark, img, kp_mark, kp, matches)
#         plt.imshow(matches_img, 'gray')
#         plt.show()
#     else:
#         print("Not enough matches are found - %d/%d" % (len(matches), MIN_MATCH_COUNT))