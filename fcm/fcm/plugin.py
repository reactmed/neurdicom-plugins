from skfuzzy.cluster import cmeans
from pydicom import Dataset
import numpy as np
import cv2 as cv


class Plugin:

    def initialize(self):
        pass

    def process(self, img, n_clusters=3, m=2, eps=0.01, max_it=1000, **kwargs):
        if isinstance(img, Dataset):
            img = img.pixel_array
        flat = img.reshape((1, -1))
        c, u, a1, a2, a3, a4, a5 = cmeans(flat, n_clusters, m, eps, max_it)
        tumor_index = np.argmax(c, axis=0)
        defuz = np.argmax(u, axis=0)
        mask = np.full(defuz.shape[0], 0)
        mask[defuz == tumor_index] = 1
        mask = mask.reshape(img.shape)
        k1 = np.ones((3, 3), np.uint16)
        k2 = np.ones((5, 5), np.uint16)
        mask = cv.erode(mask, k2, iterations=1)
        mask = cv.dilate(mask, k1, iterations=1)
        mask = cv.erode(mask, k2, iterations=2)
        mask = cv.dilate(mask, k1, iterations=5)
        return mask

    def destroy(self):
        pass
