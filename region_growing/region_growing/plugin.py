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

    def process(self, img, threshold, connectivity=6, dilation_radius=5, dilation_iterations=1, seed_point=None,
                **kwargs):
        if isinstance(img, Dataset):
            img = img.pixel_array
        stack = [seed_point]
        w, h = img.shape[1], img.shape[0]
        mask = np.full(img.shape, False)
        neighbours = (
            # Top
            (0, -1),
            # Right
            (1, 0),
            # Down
            (0, 1),
            # Left
            (-1, 0),
            # Top-Right
            (1, -1),
            # Down-Right
            (1, 1),
            # Down-Left
            (-1, 1),
            # Top-Left
            (-1, -1)
        )
        while len(stack) > 0:
            current = stack.pop()
            for neighbour in neighbours[:connectivity]:
                pos = set_coords(current, neighbour[0], neighbour[1], w, h)
                if not mask[x(pos), y(pos)] and is_below(img, seed_point, pos, threshold):
                    mask[x(pos), y(pos)] = True
                    stack.append(pos)
        mask = mask.astype(np.uint8)
        mask = cv.dilate(mask, np.ones((dilation_radius, dilation_radius)), iterations=dilation_iterations)
        return mask

    def destroy(self):
        pass
