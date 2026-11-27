# FAST-LIVO2 (ROS1 Noetic): image with all dependencies (Sophus, Livox SDK, ROS packages).
# FAST-LIVO2, vikit and livox_ros_driver are not part of the image; clone them into the mounted
# catkin workspace and build with catkin (README section 3.1).
FROM osrf/ros:noetic-desktop
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git \
    libpcl-dev libeigen3-dev libopencv-dev \
    ros-noetic-pcl-ros ros-noetic-pcl-conversions \
    ros-noetic-cv-bridge ros-noetic-image-transport \
    ros-noetic-image-transport-plugins \
    python3-catkin-tools \
 && rm -rf /var/lib/apt/lists/*

# Sophus a621ff (non-templated); so2.cpp patch needed with GCC 9 (Noetic)
WORKDIR /opt
RUN git clone https://github.com/strasdat/Sophus.git && cd Sophus \
 && git checkout a621ff \
 && sed -i 's/unit_complex_.real() = 1.;/unit_complex_ = std::complex<double>(1, 0);/' sophus/so2.cpp \
 && sed -i 's/unit_complex_.imag() = 0.;//' sophus/so2.cpp \
 && mkdir build && cd build && cmake .. && make -j"$(nproc)" && make install

# Livox SDK v1 (needed by livox_ros_driver), pinned to master 9306596
RUN git clone https://github.com/Livox-SDK/Livox-SDK.git && cd Livox-SDK \
 && git checkout 9306596 \
 && cd build && cmake .. && make -j"$(nproc)" && make install

RUN echo 'source /opt/ros/noetic/setup.bash' >> /root/.bashrc \
 && echo '[ -f /root/catkin_ws/devel/setup.bash ] && source /root/catkin_ws/devel/setup.bash' >> /root/.bashrc
WORKDIR /root/catkin_ws
