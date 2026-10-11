cmake_minimum_required(VERSION 3.20)
project(ccg_native LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "build type" FORCE)
endif()

# The interpreter the project runs under (pass -DPython_EXECUTABLE=...); nanobind from vcpkg.
find_package(Python 3.10 COMPONENTS Interpreter Development.Module REQUIRED)
find_package(nanobind CONFIG REQUIRED)

nanobind_add_module(_ccg_native NB_STATIC LTO src/module.cpp)
target_include_directories(_ccg_native PRIVATE src)
if(MSVC)
  target_compile_options(_ccg_native PRIVATE /utf-8 /W3 /EHsc)
endif()

# Install the module next to the Python package so that `import ccg._ccg_native` works.
set(CCG_PKG_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../ccg" CACHE PATH "destination package directory")
add_custom_command(TARGET _ccg_native POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:_ccg_native> "${CCG_PKG_DIR}/"
  COMMENT "copying $<TARGET_FILE_NAME:_ccg_native> to ${CCG_PKG_DIR}")

message(STATUS "Python: ${Python_EXECUTABLE} (${Python_VERSION})")
