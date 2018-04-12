from pydicom import Dataset
import numpy as np
import cv2 as cv


def x(l):
    return l[0]


def y(l):
    return l[1]


def clamp(arg, min_v, max_v):
    return min(max(arg, min_v), max_v)


def set_coords(point, x_offset, y_offset, w, h):
    return [clamp(x(point) + x_offset, 0, w), clamp(y(point) + y_offset, 0, h)]


def is_below(img, p1, p2, th):
    return abs(img[x(p1), y(p1)] - img[x(p2), y(p2)]) <= th


def growing_region_6(img, seed_point, threshold):
    stack = [seed_point]
    w, h = img.shape[1], img.shape[0]
    mask = np.full(img.shape, False)
    while len(stack) > 0:
        current = stack.pop()
        top = set_coords(current, 0, -1, w, h)
        right = set_coords(current, 1, 0, w, h)
        bottom = set_coords(current, 0, 1, w, h)
        left = set_coords(current, -1, 0, w, h)
        if not mask[x(top), y(top)] and is_below(img, current, top, threshold):
            mask[x(top), y(top)] = True
            stack.append(top)
        if not mask[x(right), y(right)] and is_below(img, current, right, threshold):
            mask[x(right), y(right)] = True
            stack.append(right)
        if not mask[x(bottom), y(bottom)] and is_below(img, current, bottom, threshold):
            mask[x(bottom), y(bottom)] = True
            stack.append(bottom)
        if not mask[x(left), y(left)] and is_below(img, current, left, threshold):
            mask[x(left), y(left)] = True
            stack.append(left)
    mask = mask.astype(np.uint8)
    mask = cv.dilate(mask, np.ones(5, 5), iterations=1)
    return mask


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

        if not mask[x(top), y(top)] and is_below(img, current, top, threshold):
            mask[x(top), y(top)] = True
            stack.append(top)
        if not mask[x(right), y(right)] and is_below(img, current, right, threshold):
            mask[x(right), y(right)] = True
            stack.append(right)
        if not mask[x(down), y(down)] and is_below(img, current, down, threshold):
            mask[x(down), y(down)] = True
            stack.append(down)
        if not mask[x(left), y(left)] and is_below(img, current, left, threshold):
            mask[x(left), y(left)] = True
            stack.append(left)

        if not mask[x(top_right), y(top_right)] and is_below(img, current, top_right, threshold):
            mask[x(top_right), y(top_right)] = True
            stack.append(top_right)
        if not mask[x(down_right), y(down_right)] and is_below(img, current, down_right, threshold):
            mask[x(down_right), y(down_right)] = True
            stack.append(down_right)
        if not mask[x(down_left), y(down_left)] and is_below(img, current, down_left, threshold):
            mask[x(down_left), y(down_left)] = True
            stack.append(down_left)
        if not mask[x(top_left), y(top_left)] and is_below(img, current, top_left, threshold):
            mask[x(top_left), y(top_left)] = True
            stack.append(top_left)
    mask = mask.astype(np.uint8)
    mask = cv.dilate(mask, np.ones(5, 5), iterations=1)
    return mask


class Plugin:

    def initialize(self):
        pass

    def process(self, img, threshold, connectivity='CON_6', seed_point=None, **kwargs):
        if isinstance(img, Dataset):
            img = img.pixel_array
        if connectivity == 'CON_6':
            return growing_region_6(img, seed_point, threshold)
        if connectivity == 'CON_8':
            return growing_region_8(img, seed_point, threshold)
        return None

    def destroy(self):
        pass
