import cv2 as cv
import numpy as np
from dipy.segment.mask import median_otsu
from pydicom import Dataset
from sklearn.cluster import estimate_bandwidth, MeanShift


class Plugin:

    def initialize(self):
        pass

    def process(self, img, **kwargs):
        quantile = kwargs.get('quantile', 0.1)
        n_samples = kwargs.get('n_samples', 100)
        numpass = kwargs.get('numpass', 5)
        median_radius = kwargs.get('median_radius', 10)
        high_intensity_threshold = kwargs.get('high_intensity_threshold', 0.1)
        blur_radius = kwargs.get('blur_radius', 9)
        dilation_radius = kwargs.get('dilation_radius', 5)
        dilation_iterations = kwargs.get('dilation_iterations', 1)
        if isinstance(img, Dataset):
            img = img.pixel_array
        img, _ = median_otsu(img, numpass=numpass, median_radius=median_radius)
        original_shape = img.shape
        img = (img - np.min(img)) / (np.max(img) - np.min(img))
        blurred = cv.blur(img, (15, 15))
        edges = np.clip(img - blurred, 0.0, 1.0)
        edges[edges > high_intensity_threshold] = 1.0
        edges[edges <= high_intensity_threshold] = 0.0
        edges = cv.dilate(edges, np.ones((3, 3)), iterations=1)
        img = np.clip(img - edges, 0.0, 1.0)
        img = cv.erode(img, np.ones((3, 3)), iterations=1)
        img = cv.blur(img, (blur_radius, blur_radius))
        # Flatten image.
        x = np.reshape(img, [-1, 1])
        bandwidth = estimate_bandwidth(x, quantile=quantile, n_samples=n_samples)
        mean_shift = MeanShift(bandwidth=bandwidth, bin_seeding=True)
        mean_shift.fit(x)
        # c_index = np.argmax(mean_shift.cluster_centers_.reshape((-1)))
        # flat = np.full(original_shape[0] * original_shape[1], 0, dtype=np.uint8)
        # flat[mean_shift.labels_ == c_index] = 1
        mask = mean_shift.labels_.reshape(original_shape)
        # mask = cv.dilate(mask, np.ones((dilation_radius, dilation_radius)), iterations=dilation_iterations)
        return mask

    def destroy(self):
        pass
