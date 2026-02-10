cmake_minimum_required(VERSION 3.10)
project(DisasterBackend LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Build shared library (.dll on Windows, .so on Linux)
add_library(backend SHARED
    graph.cpp
    dijkstra.cpp
    resources.cpp
    wrapper.cpp
)

# On Windows, output as backend.dll
set_target_properties(backend PROPERTIES
    PREFIX ""
    OUTPUT_NAME "backend"
)
