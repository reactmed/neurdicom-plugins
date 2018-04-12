from dipy.segment.mask import median_otsu
from pydicom import Dataset
import numpy as np
import cv2 as cv


def find_threshold_cpu(img, k=100, eps=0.001):
    cols = img.shape[1]

    mid = cols // 2
    p1 = img[:, :mid].reshape((-1))
    p2 = img[:, mid:].reshape((-1))
    img = img.reshape((-1))

    it = -1
    while True:
        t1 = np.mean(p1)
        t2 = np.mean(p2)

        t = (t1 + t2) / 2.0
        it += 1
        if it >= k or abs(t1 - t2) <= eps:
            return t
        else:
            p1 = img[img < t]
            p2 = img[img >= t]


def process_cpu(img, threshold=None):
    t = threshold or find_threshold_cpu(img, eps=0.000001)
    mask = (img > t).astype(np.int16)
    k1 = np.ones((3, 3), np.uint16)
    k2 = np.ones((5, 5), np.uint16)
    mask = cv.erode(mask, k2, iterations=1)
    mask = cv.dilate(mask, k1, iterations=1)
    mask = cv.erode(mask, k2, iterations=2)
    mask = cv.dilate(mask, k1, iterations=5)
    return mask


class Plugin:

    def initialize(self):
        pass

    def process(self, img, mode: str = 'CPU', threshold=None, **kwargs):
        if isinstance(img, Dataset):
            img = img.pixel_array
        img, _ = median_otsu(img, 5, 10)
        if mode == 'CPU':
            return process_cpu(img, threshold=threshold)
        return None

    def destroy(self):
        pass
