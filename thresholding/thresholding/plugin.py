from dipy.segment.mask import median_otsu
from pydicom import Dataset
import numpy as np
import cv2 as cv


def find_threshold_cpu(img, max_it=100, eps=0.001):
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
        if it >= max_it or abs(t1 - t2) <= eps:
            return t
        else:
            p1 = img[img < t]
            p2 = img[img >= t]


class Plugin:

    def initialize(self):
        pass

    def process(self, img, **kwargs):
        threshold = kwargs.get('threshold', None)
        max_it = kwargs.get('max_it', 100)
        eps = kwargs.get('eps', 0.001)
        numpass = kwargs.get('numpass', 10)
        median_radius = kwargs.get('median_radius', 5)
        if isinstance(img, Dataset):
            img = img.pixel_array
        skull_stripped, _ = median_otsu(img, median_radius=median_radius, numpass=numpass, autocrop=True)
        t = threshold or find_threshold_cpu(skull_stripped, max_it=max_it, eps=eps)
        mask = (img > t).astype(np.int16)
        k1 = np.ones((3, 3), np.uint16)
        k2 = np.ones((5, 5), np.uint16)
        mask = cv.erode(mask, k2, iterations=1)
        mask = cv.dilate(mask, k1, iterations=1)
        mask = cv.erode(mask, k2, iterations=2)
        mask = cv.dilate(mask, k1, iterations=5)
        return mask

    def destroy(self):
        pass
