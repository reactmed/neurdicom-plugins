from ctypes import *
import platform
import numpy as np
import os
from pathlib import Path
from json import *

c_float_p = POINTER(c_float)
c_int_p = POINTER(c_int)

PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
print(PARENT_DIR)

SYSTEM = platform.system()
if SYSTEM == 'Darwin':
    LIB_PATH = '%s/extension/build/%s/libc_region_growing.dylib' % (PARENT_DIR, SYSTEM)
else:
    raise ValueError('Platform "%s" is not supported' % SYSTEM)


class Plugin:
    def __init__(self):
        self.lib = cdll.LoadLibrary(LIB_PATH)
        self.lib.Process.argtypes = [c_void_p, c_float_p, c_int, c_int, POINTER(c_char)]
        self.lib.Process.restype = c_int_p
        self.lib.DestroyPlugin.argtypes = [c_void_p]
        self.obj = self.lib.InitPlugin()

    def __enter__(self):
        return self

    def process(self, a: np.ndarray, seed_point, **kwargs):
        w = a.shape[1]
        h = a.shape[0]
        seed_point = seed_point or [0, 0]
        params = {
            'seedPointX': seed_point[0],
            'seedPointY': seed_point[1]
        }
        params.update(kwargs)
        params['threshold'] = params.get('threshold', 100.0) / 100.0
        params = create_string_buffer(str.encode(dumps(params)))
        a_min, a_max = np.min(a), np.max(a)
        a = (a - a_min) / (a_max - a_min)
        a = a.astype(np.float32)
        img = a.ctypes.data_as(c_float_p)
        cres = self.lib.Process(self.obj, img, w, h, params)
        return np.ctypeslib.as_array(cres, shape=(h, w))

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.lib.DestroyPlugin(self.obj)
        pass

