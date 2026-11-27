cmake_minimum_required(VERSION 3.8)
project(fast_livo)

set(CMAKE_BUILD_TYPE "Release")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Set common compile options
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread -fexceptions")

# Specific settings for Debug build
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -O0 -g")

# Detect CPU architecture
message(STATUS "Current CPU architecture: ${CMAKE_SYSTEM_PROCESSOR}")

# Specific settings for Release build
if(CMAKE_SYSTEM_PROCESSOR MATCHES "^(arm|aarch64|ARM|AARCH64)")
  if(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64")
    # 64-bit ARM optimizations (e.g., RK3588 and Jetson Orin NX)
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -mcpu=native -mtune=native -ffast-math")
    message(STATUS "Using 64-bit ARM optimizations: -O3 -mcpu=native -mtune=native -ffast-math")
  else()
    # 32-bit ARM optimizations with NEON support
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -mcpu=native -mtune=native -mfpu=neon -ffast-math")
    message(STATUS "Using 32-bit ARM optimizations: -O3 -mcpu=native -mtune=native -mfpu=neon -ffast-math")
  endif()
  add_definitions(-DARM_ARCH)
else()
  # x86-64 (Intel/AMD) optimizations
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -march=native -mtune=native -funroll-loops") #-flto
  message(STATUS "Using general x86 optimizations: -O3 -march=native -mtune=native -funroll-loops") 
  add_definitions(-DX86_ARCH)
endif()

# Define project root directory
add_definitions(-DROOT_DIR=\"${CMAKE_CURRENT_SOURCE_DIR}/\")

# Detect CPU core count for potential multithreading optimization
include(ProcessorCount)
ProcessorCount(N)
message(STATUS "Processor count: ${N}")

# Set the number of cores for multithreading
if(N GREATER 4)
  math(EXPR PROC_NUM "4")
  add_definitions(-DMP_EN -DMP_PROC_NUM=${PROC_NUM})
  message(STATUS "Multithreading enabled. Cores: ${PROC_NUM}")
elseif(N GREATER 1)
  math(EXPR PROC_NUM "${N}")
  add_definitions(-DMP_EN -DMP_PROC_NUM=${PROC_NUM})
  message(STATUS "Multithreading enabled. Cores: ${PROC_NUM}")
else()
  add_definitions(-DMP_PROC_NUM=1)
  message(STATUS "Single core detected. Multithreading disabled.")
endif()

# Check for OpenMP support
find_package(OpenMP QUIET)
if(OpenMP_CXX_FOUND)
  message(STATUS "OpenMP found")
  add_compile_options(${OpenMP_CXX_FLAGS})
else()
  message(STATUS "OpenMP not found, proceeding without it")
endif()

# Check for mimalloc support
find_package(mimalloc QUIET)
if(mimalloc_FOUND)
  message(STATUS "mimalloc found")
else()
  message(STATUS "mimalloc not found, proceeding without it")
endif()

# Find ament and required ROS2 dependencies
find_package(ament_cmake REQUIRED)
set(ros_dependencies
  rclcpp
  builtin_interfaces
  std_msgs
  geometry_msgs
  nav_msgs
  sensor_msgs
  visualization_msgs
  tf2
  tf2_ros
  pcl_conversions
  cv_bridge
  image_transport
  vikit_common
  vikit_ros
  livox_ros_driver
)
foreach(dep ${ros_dependencies})
  find_package(${dep} REQUIRED)
endforeach()

# Optional: Livox CustomMsg types of the ROS2 drivers (same fields, other type name).
# Built in only if the message package is found (build or source it before fast_livo).
find_package(livox_interfaces QUIET)   # livox_ros2_driver (Livox SDK1, e.g. Avia)
if(livox_interfaces_FOUND)
  list(APPEND ros_dependencies livox_interfaces)
  add_definitions(-DFASTLIVO_HAVE_LIVOX_INTERFACES)
  message(STATUS "livox_interfaces found: livox_msg_type livox_interfaces supported")
else()
  message(STATUS "livox_interfaces not found: livox_msg_type livox_interfaces not supported")
endif()
find_package(livox_ros_driver2 QUIET)  # livox_ros_driver2 (Livox SDK2, e.g. Mid-360)
if(livox_ros_driver2_FOUND)
  list(APPEND ros_dependencies livox_ros_driver2)
  add_definitions(-DFASTLIVO_HAVE_LIVOX_ROS_DRIVER2)
  message(STATUS "livox_ros_driver2 found: livox_msg_type livox_ros_driver2 supported")
else()
  message(STATUS "livox_ros_driver2 not found: livox_msg_type livox_ros_driver2 not supported")
endif()

find_package(Eigen3 REQUIRED)
find_package(PCL REQUIRED)
find_package(OpenCV REQUIRED)
find_package(Sophus REQUIRED)
find_package(Boost REQUIRED COMPONENTS thread)

set(Sophus_LIBRARIES libSophus.so)

# Include directories for dependencies
include_directories(
  ${EIGEN3_INCLUDE_DIR}
  ${PCL_INCLUDE_DIRS}
  ${OpenCV_INCLUDE_DIRS}
  ${Sophus_INCLUDE_DIRS}
  include
)

# Add libraries (shared, as catkin built them in ROS1)
add_library(vio SHARED src/vio.cpp src/frame.cpp src/visual_point.cpp)
add_library(lio SHARED src/voxel_map.cpp)
add_library(pre SHARED src/preprocess.cpp)
add_library(imu_proc SHARED src/IMU_Processing.cpp)
add_library(laser_mapping SHARED src/LIVMapper.cpp)
foreach(lib vio lio pre imu_proc laser_mapping)
  ament_target_dependencies(${lib} ${ros_dependencies})
endforeach()

# Add the main executable
add_executable(fastlivo_mapping src/main.cpp)
ament_target_dependencies(fastlivo_mapping ${ros_dependencies})

# Link libraries to the executable
target_link_libraries(fastlivo_mapping
  laser_mapping
  vio
  lio
  pre
  imu_proc
  ${PCL_LIBRARIES}
  ${OpenCV_LIBRARIES}
  ${Sophus_LIBRARIES}
  ${Boost_LIBRARIES}
)

# Link mimalloc if found
if(mimalloc_FOUND)
  target_link_libraries(fastlivo_mapping mimalloc)
endif()

# Install
install(TARGETS vio lio pre imu_proc laser_mapping LIBRARY DESTINATION lib)
install(TARGETS fastlivo_mapping DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY config launch rviz_cfg DESTINATION share/${PROJECT_NAME})

ament_package()
