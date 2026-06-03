cmake_minimum_required(VERSION 3.16)
project(zero_pool_loader VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find liburing
find_package(PkgConfig REQUIRED)
pkg_check_modules(URING REQUIRED liburing)

# Executable
add_executable(zero_pool_loader src/main.cpp)

# Link libraries
target_link_libraries(zero_pool_loader ${URING_LIBRARIES} pthread)
target_include_directories(zero_pool_loader PRIVATE ${URING_INCLUDE_DIRS})
target_compile_options(zero_pool_loader PRIVATE ${URING_CFLAGS_OTHER})

# Install
install(TARGETS zero_pool_loader DESTINATION bin)
