cmake_minimum_required(VERSION 3.9)
project(gauss_kernel_kmeans)

set(CMAKE_CXX_STANDARD 11)

include_directories(include)
set(SRC library.h library.cpp Plugin.h Plugin.cpp)
add_library(gauss_kernel_kmeans SHARED ${SRC})