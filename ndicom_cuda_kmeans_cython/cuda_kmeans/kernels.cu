#ifdef __JETBRAINS_IDE__
#define __host__
#define __device__
#define __shared__
#define __constant__
#define __global__

// This is slightly mental, but gets it to properly index device function calls like __popc and whatever.
#define __CUDACC__

#include <device_functions.h>

// These headers are all implicitly present when you compile CUDA with clang. Clion doesn't know that, so
// we include them explicitly to make the indexer happy. Doing this when you actually build is, obviously,
// a terrible idea :D
#include <__clang_cuda_builtin_vars.h>
#include <__clang_cuda_intrinsics.h>
#include <__clang_cuda_math_forward_declares.h>
#include <__clang_cuda_complex_builtins.h>
#include <__clang_cuda_cmath.h>

#endif // __JETBRAINS_IDE__

#define BLOCKDIM 1024

struct Cluster {
    float sum;
    int count;
};

__device__ Cluster clusters_d[(N + BLOCKDIM - 1) / BLOCKDIM];

__device__ float euclidianDist(const float a, const float b) {
    float dist = a - b;
    return hypotf(dist, dist);
}

__global__ void relabel(const float *src, const float *clusters, int n, int nClusters, int *labels) {
    int pos = threadIdx.x + blockIdx.x * blockDim.x;
    if (pos < n) {
        float minDist = 1.0f;
        int clusterIndex = 0;
        for (int c = 0; c < nClusters; c++) {
            float dist = euclidianDist(src[pos], clusters[c]);
            if (dist <= minDist) {
                clusterIndex = c;
                minDist = dist;
            }
        }
        labels[pos] = clusterIndex;
    }
}

__global__ void calculateClusters(const float *src, const int *labels, int n, int clusterIndex) {
    extern __shared__ Cluster
    _clusters[];
    int pos = threadIdx.x + blockIdx.x * blockDim.x;
    int tid = threadIdx.x;
    _clusters[tid] = Cluster();
    _clusters[tid].sum = 0.0f;
    _clusters[tid].count = 0;
    if (pos < n && labels[pos] == clusterIndex) {
        _clusters[tid].sum = src[pos];
        _clusters[tid].count = 1;
    }
    __syncthreads();
    for (unsigned int stride = blockDim.x / 2; stride > 0; stride /= 2) {
        if (threadIdx.x < stride) {
            _clusters[tid].sum += _clusters[tid + stride].sum;
        }
        __syncthreads();
        if (threadIdx.x < stride) {
            _clusters[tid].count += _clusters[tid + stride].count;
        }
        __syncthreads();
    }
    __syncthreads();
    if (threadIdx.x == 0) {
        clusters_d[blockIdx.x].sum = _clusters[0].sum;
        clusters_d[blockIdx.x].count = _clusters[0].count;
    }
}

__global__ void findCenters(int n, int clusterIndex, float *dst) {
    extern __shared__ Cluster
    _clusters[];
    int pos = threadIdx.x + blockIdx.x * blockDim.x;
    int tid = threadIdx.x;
    _clusters[tid] = clusters_d[pos];
    __syncthreads();
    for (unsigned int stride = blockDim.x / 2; stride > 0; stride /= 2) {
        if (tid < stride) {
            _clusters[tid].sum += _clusters[tid + stride].sum;
        }
        __syncthreads();
        if (tid < stride) {
            _clusters[tid].count += _clusters[tid + stride].count;
        }
        __syncthreads();
    }
    __syncthreads();
    if (tid == 0) {
        dst[clusterIndex] = _clusters[0].count > 0 ? _clusters[0].sum / (_clusters[0].count * 1.0f) : 0.0f;
    }
}