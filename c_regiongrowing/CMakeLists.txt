cmake_minimum_required(VERSION 3.9)
project(c_regiongrowing)

set(CMAKE_CXX_STANDARD 11)

include_directories(include)
set(SRC library.h library.cpp Plugin.h Plugin.cpp)
add_library(c_regiongrowing SHARED ${SRC})