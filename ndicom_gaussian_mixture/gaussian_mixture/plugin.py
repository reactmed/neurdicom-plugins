import cv2 as cv
import numpy as np
from dipy.segment.mask import median_otsu
from pydicom import Dataset
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture


class Plugin:

    def __enter__(self):
        print('Gaussian Mixture: plugin is starting')

    def process(self, img, **kwargs):
        n_components = kwargs.get('n_components', 3)
        numpass = kwargs.get('numpass', 5)
        median_radius = kwargs.get('median_radius', 10)
        if isinstance(img, Dataset):
            img = img.pixel_array
        w, h = img.shape[1], img.shape[0]
        img, _ = median_otsu(img, numpass=numpass, median_radius=median_radius)
        img = (img - np.min(img)) / (np.max(img) - np.min(img))
        x = img.reshape((-1, 1))
        model = GaussianMixture(n_components=n_components, covariance_type='spherical')
        model.fit(x)
        labels = model.predict(x)
        # c_index = np.argmax(k_means.cluster_centers_.reshape((-1)))
        # flat = np.full(img.shape[0] * img.shape[1], 0, dtype=np.uint8)
        # flat[k_means.labels_ == c_index] = 1
        # mask = flat.reshape(img.shape)
        # k1 = np.ones((3, 3), np.uint16)
        # k2 = np.ones((5, 5), np.uint16)
        # mask = cv.erode(mask, k2, iterations=1)
        # mask = cv.dilate(mask, k1, iterations=1)
        # mask = cv.erode(mask, k2, iterations=2)
        # mask = cv.dilate(mask, k1, iterations=5)
        return labels.reshape((h, w))

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('KMeans: plugin destroys context')
