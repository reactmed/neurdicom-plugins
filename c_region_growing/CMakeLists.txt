cmake_minimum_required(VERSION 3.9)
project(c_region_growing)

set(CMAKE_CXX_STANDARD 11)

include_directories(include)
set(SRC library.h library.cpp Plugin.h Plugin.cpp)
add_library(c_region_growing SHARED ${SRC})