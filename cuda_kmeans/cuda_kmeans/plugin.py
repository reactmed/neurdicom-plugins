import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule

import cv2 as cv
import numpy as np
from dipy.segment.mask import median_otsu
from pydicom import Dataset

from jinja2 import Template
import numpy as np

BLOCKDIM = 1024

SRC = '''
    #define N {{N}}
    #define BLOCKDIM 1024
    
    struct Cluster{
        float sum;
        int count;
    };
    
    __device__ Cluster clusters_d[(N + BLOCKDIM - 1) / BLOCKDIM];
    
    __device__ float euclidian_dist(const float a, const float b){
        float dist = a - b;
        return hypotf(dist, dist);
    }
    
    __global__ void relabel(const float* src, const float* clusters, int n, int nClusters, int* labels){
        int pos = threadIdx.x + blockIdx.x * blockDim.x;
        if(pos < n){
            float minDist = 1.0f;
            int clusterIndex = 0;
            for(int c = 0; c < nClusters; c++){
                float dist = euclidian_dist(src[pos], clusters[c]);
                if(dist <= minDist){
                    clusterIndex = c;
                    minDist = dist;
                }
            }
            labels[pos] = clusterIndex;
        }
    }
    
    __global__ void calculateClusters(const float* src, const int* labels, int n, int clusterIndex){
        extern __shared__ Cluster _clusters[];
        int pos = threadIdx.x + blockIdx.x * blockDim.x;
        int tid = threadIdx.x;
        _clusters[tid] = Cluster();
        _clusters[tid].sum = 0.0f;
        _clusters[tid].count = 0;
        if(pos < n && labels[pos] == clusterIndex){
            _clusters[tid].sum = src[pos];
            _clusters[tid].count = 1;
        }
        __syncthreads();
        for(unsigned int stride = blockDim.x / 2; stride > 0; stride /= 2){
            if(threadIdx.x < stride){
                _clusters[tid].sum += _clusters[tid + stride].sum;
            }
            __syncthreads();
            if(threadIdx.x < stride){
                _clusters[tid].count += _clusters[tid + stride].count;
            }
            __syncthreads();
        }
        __syncthreads();
        if(threadIdx.x == 0){
            clusters_d[blockIdx.x].sum = _clusters[0].sum;
            clusters_d[blockIdx.x].count = _clusters[0].count;
        }
    }
    
    __global__ void findCenters(int n, int clusterIndex, float* dst){
        extern __shared__ Cluster _clusters[];
        int pos = threadIdx.x + blockIdx.x * blockDim.x;
        int tid = threadIdx.x;
        _clusters[tid] = clusters_d[pos];
        __syncthreads();
        for(unsigned int stride = blockDim.x / 2; stride > 0; stride /= 2){
            if(tid < stride){
                _clusters[tid].sum += _clusters[tid + stride].sum;
            }
            __syncthreads();
            if(tid < stride){
                _clusters[tid].count += _clusters[tid + stride].count;
            }
            __syncthreads();
        }
        __syncthreads();
        if(tid == 0){
            dst[clusterIndex] = _clusters[0].count > 0 ? _clusters[0].sum / (_clusters[0].count * 1.0f) : 0.0f;
        }
    }
'''


class Plugin:

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def process(self, img, **kwargs):
        if isinstance(img, Dataset):
            img = img.pixel_array
        w = img.shape[1]
        h = img.shape[0]
        n = w * h

        all_segments = kwargs.get('all_segments', True)
        max_it = kwargs.get('max_it', 100)
        if not isinstance(max_it, int) or max_it <= 0:
            raise ValueError('Number of iterations should not be negative')
        n_clusters = kwargs.get('n_clusters', 2)
        if not isinstance(n_clusters, int) or n_clusters <= 0:
            raise ValueError('Number of clusters should not be less than 1')

        numpass = kwargs.get('numpass', 5)
        median_radius = kwargs.get('median_radius', 10)
        high_intensity_threshold = kwargs.get('high_intensity_threshold', 0.1)
        blur_radius = kwargs.get('blur_radius', 5)

        img, _ = median_otsu(img, numpass=numpass, median_radius=median_radius)
        img = (img - np.min(img)) / (np.max(img) - np.min(img))
        blurred = cv.blur(img, (15, 15))
        edges = np.clip(img - blurred, 0.0, 1.0)
        edges[edges > high_intensity_threshold] = 1.0
        edges[edges <= high_intensity_threshold] = 0.0
        edges = cv.dilate(edges, np.ones((3, 3)), iterations=1)
        img = np.clip(img - edges, 0.0, 1.0)
        img = cv.erode(img, np.ones((3, 3)), iterations=1)
        img = cv.blur(img, (blur_radius, blur_radius))

        # src = (img - np.min(img)) / (np.max(img) - np.min(img))
        src = img.astype(np.float32)
        src = src.reshape((-1))

        centers = np.random.rand(n_clusters).astype(np.float32)

        # Image
        src_gpu = cuda.mem_alloc(src.nbytes)
        cuda.memcpy_htod(src_gpu, src)

        # Cluster centers

        centers_gpu = cuda.mem_alloc(centers.nbytes)
        cuda.memcpy_htod(centers_gpu, centers)

        # Labels
        labels = np.empty_like(src).astype(np.int32)
        labels_gpu = cuda.mem_alloc(labels.nbytes)
        cuda.memcpy_htod(labels_gpu, labels)

        module = SourceModule(Template(SRC).render(N=n))
        relabel = module.get_function('relabel')
        calculate_clusters = module.get_function('calculateClusters')
        find_centers = module.get_function('findCenters')

        for it in range(max_it):
            relabel(src_gpu, centers_gpu, np.int32(n), np.int32(n_clusters), labels_gpu,
                    block=(BLOCKDIM, 1, 1), grid=((n + BLOCKDIM - 1) // BLOCKDIM, 1))
            for c in range(n_clusters):
                calculate_clusters(src_gpu, labels_gpu, np.int32(n), np.int32(c),
                                   block=(BLOCKDIM, 1, 1), grid=((n + BLOCKDIM - 1) // BLOCKDIM, 1),
                                   shared=8 * BLOCKDIM)
                find_centers(np.int32(n), np.int32(c), centers_gpu,
                             block=((n + BLOCKDIM - 1) // BLOCKDIM, 1, 1), grid=((1, 1)),
                             shared=8 * (n + BLOCKDIM - 1) // BLOCKDIM)

        cuda.memcpy_dtoh(labels, labels_gpu)
        cuda.memcpy_dtoh(centers, centers_gpu)

        labels = labels.reshape((-1))
        if not all_segments:
            c_index = np.argmax(centers)
            flat = np.full(n, 0, dtype=np.uint8)
            flat[labels == c_index] = 1
            mask = flat.reshape((h, w))

            return mask
        else:
            return labels.reshape((h, w))

    def __exit__(self, exc_type, exc_val, exc_traceback):
        return self
