from ctypes import *
import numpy as np
from json import dumps
from pydicom import read_file
from time import time
from collections import deque

from pydicom import Dataset
import cv2 as cv


def x(l):
    return l[0]


def y(l):
    return l[1]


def clamp(arg, min_v, max_v):
    return min(max(arg, min_v), max_v)


def set_coords(point, x_offset, y_offset, w, h):
    return [clamp(x(point) + x_offset, 0, w - 1), clamp(y(point) + y_offset, 0, h - 1)]


def is_below(img, p1, p2, th):
    return abs(img[x(p1), y(p1)] - img[x(p2), y(p2)]) <= th


def growing_region_8(img, seed_point, threshold):
    stack = [seed_point]
    w, h = img.shape[1], img.shape[0]
    mask = np.full(img.shape, False)
    while len(stack) > 0:
        current = stack.pop()
        top = set_coords(current, 0, -1, w, h)
        right = set_coords(current, 1, 0, w, h)
        down = set_coords(current, 0, 1, w, h)
        left = set_coords(current, -1, 0, w, h)
        top_right = set_coords(current, 1, -1, w, h)
        down_right = set_coords(current, 1, 1, w, h)
        down_left = set_coords(current, -1, 1, w, h)
        top_left = set_coords(current, -1, -1, w, h)

        if not mask[x(top), y(top)] and is_below(img, seed_point, top, threshold):
            mask[x(top), y(top)] = True
            stack.append(top)
        if not mask[x(right), y(right)] and is_below(img, seed_point, right, threshold):
            mask[x(right), y(right)] = True
            stack.append(right)
        if not mask[x(down), y(down)] and is_below(img, seed_point, down, threshold):
            mask[x(down), y(down)] = True
            stack.append(down)
        if not mask[x(left), y(left)] and is_below(img, seed_point, left, threshold):
            mask[x(left), y(left)] = True
            stack.append(left)

        if not mask[x(top_right), y(top_right)] and is_below(img, seed_point, top_right, threshold):
            mask[x(top_right), y(top_right)] = True
            stack.append(top_right)
        if not mask[x(down_right), y(down_right)] and is_below(img, seed_point, down_right, threshold):
            mask[x(down_right), y(down_right)] = True
            stack.append(down_right)
        if not mask[x(down_left), y(down_left)] and is_below(img, seed_point, down_left, threshold):
            mask[x(down_left), y(down_left)] = True
            stack.append(down_left)
        if not mask[x(top_left), y(top_left)] and is_below(img, seed_point, top_left, threshold):
            mask[x(top_left), y(top_left)] = True
            stack.append(top_left)
    mask = mask.astype(np.uint8)
    mask = cv.dilate(mask, np.ones((5, 5)), iterations=1)
    return mask


class Plugin:

    def initialize(self):
        pass

    def process(self, img, connectivity=8, threshold=1.0, seed_point_x=0, seed_point_y=0,
                **kwargs):
        seed_point_x = kwargs.get('seed_point_x', 0)
        seed_point_y = kwargs.get('seed_point_y', 0)
        seed_point = [seed_point_x, seed_point_y]
        if isinstance(img, Dataset):
            img = img.pixel_array
        w, h = img.shape[1], img.shape[0]
        stack = deque(maxlen=w*h)
        stack.appendleft(seed_point)
        mask = np.full(img.shape, False)
        while len(stack) > 0:
            current = stack.popleft()
            for i in range(3):
                for j in range(3):
                    pos = set_coords(current, i - 1, j - 1, w, h)
                    if not mask[x(pos), y(pos)] and is_below(img, seed_point, pos, threshold):
                        mask[x(pos), y(pos)] = True
                        stack.appendleft(pos)

        mask = mask.astype(np.uint8)
        return mask

    def destroy(self):
        pass


c_float_p = POINTER(c_float)
c_int_p = POINTER(c_int)

class NativePlugin:
    def __init__(self, path):
        self.lib = cdll.LoadLibrary(path)
        self.obj = self.lib.InitPlugin()
        self.lib.Process.argtypes = [c_void_p, c_float_p, c_int_p, c_int, POINTER(c_char)]
        self.lib.Process.restype = c_int_p

    def process(self, a: np.ndarray, **kwargs):
        images_count = 1
        if a.ndim == 2:
            w = a.shape[1]
            h = a.shape[0]
            IntArray = c_int * 2
            images_size = IntArray(w, h)
        else:
            images_count = a.shape[0]
            w = a.shape[2]
            h = a.shape[1]
            IntArray = c_int * (images_count * 2)
            images_size = IntArray(*list([w, h] * images_count))
        params = create_string_buffer(str.encode(dumps(kwargs)))
        img = a.ctypes.data_as(c_float_p)
        cres = self.lib.Process(self.obj, img, images_size, images_count, params)
        if images_count == 1:
            return np.ctypeslib.as_array(cres, shape=(h, w))
        else:
            return np.ctypeslib.as_array(cres, shape=(images_count, h, w))

plugin = NativePlugin('./cmake-build-debug/libc_region_growing.dylib')
# a = read_file('/Users/macbook/Desktop/brain.dcm').pixel_array
# a = (a - np.min(a)) / (np.max(a) - np.min(a))

a = np.random.rand(59, 512, 512)

start = time()
res = plugin.process(a.astype(np.float32), threshold=1.0, x=1, y=1)
end = time()
nativeTime = end - start
print('Native', nativeTime, 'secs')
print((res == 1).sum())

# plugin = Plugin()
# start = time()
# res = plugin.process(a, threshold=1.0, seed_point_x=1, seed_point_y=1)
# end = time()
# pythonTime = end - start
# print('Python', pythonTime, 'secs')
# print((res == True).sum())
# print('Speedup', pythonTime / nativeTime)
