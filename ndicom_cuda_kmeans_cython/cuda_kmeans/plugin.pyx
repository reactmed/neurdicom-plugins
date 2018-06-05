import numpy as np
cimport numpy as np

assert sizeof(int) == sizeof(np.int32_t)

cdef extern from "plugin.h":
    cdef cppclass C_Plugin "Plugin":
        C_Plugin(np.int32_t*, int)
        void increment()
        void retreive()
        void retreive_to(np.int32_t*, int)

cdef class Plugin:
    cdef C_Plugin*g
    cdef int dim1

    def __cinit__(self, np.ndarray[ndim=2, dtype=np.int32_t] arr):
        self.dim1 = len(arr)
        self.g = new C_Plugin(&arr[0], self.dim1)

    def increment(self):
        self.g.increment()

    def retreive_inplace(self):
        self.g.retreive()

    def retreive(self):
        cdef np.ndarray[ndim=1, dtype=np.int32_t] a = np.zeros(self.dim1, dtype=np.int32)

        self.g.retreive_to(&a[0], self.dim1)

        return a
