cmake_minimum_required(VERSION 3.16)
project(cicd_showcase_backend VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Compiler warnings — mirrors what CI enforces
if(MSVC)
  add_compile_options(/W4)
else()
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Main executable
add_executable(backend main.cpp)

# Test executable
add_executable(backend_tests tests.cpp)

# CTest integration
enable_testing()
add_test(NAME BackendUnitTests COMMAND backend_tests)
