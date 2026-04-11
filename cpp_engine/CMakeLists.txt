cmake_minimum_required(VERSION 3.15)
project(cpp_engine)

# Searching Pybind11
find_package(pybind11 REQUIRED)

# Creating cpp_linker from the two source files
pybind11_add_module(cpp_linker smart_linker.cpp bindings.cpp)

set_target_properties(cpp_linker PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/../src"
    LIBRARY_OUTPUT_DIRECTORY_RELEASE "${CMAKE_SOURCE_DIR}/../src"
    LIBRARY_OUTPUT_DIRECTORY_DEBUG "${CMAKE_SOURCE_DIR}/../src"
)

# Optimization for performance while parsing text
target_compile_options(cpp_linker PRIVATE -O3 -std=c++17)