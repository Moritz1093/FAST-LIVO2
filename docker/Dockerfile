# FAST-LIVO2 (ROS2 Jazzy): image with all dependencies (README sections 2.2 and 2.3).
# FAST-LIVO2, vikit and the Livox message package are not part of the image; clone them into the
# mounted workspace and build with colcon (README sections 2.4, 2.5 and 3).
FROM osrf/ros:jazzy-desktop@sha256:2f520187e84304fffb60d19c9a7d8e2e79d563a6e579a090427e5994eb1b8c45
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git \
    libpcl-dev libeigen3-dev libopencv-dev \
    python3-colcon-common-extensions \
    ros-jazzy-pcl-ros ros-jazzy-pcl-conversions \
    ros-jazzy-cv-bridge ros-jazzy-image-transport \
    ros-jazzy-image-transport-plugins \
    ros-jazzy-tf2-ros ros-jazzy-tf2-geometry-msgs \
    ros-jazzy-rosbag2-storage-mcap \
 && rm -rf /var/lib/apt/lists/*

# Sophus a621ff (non-templated); so2.cpp patch for newer compilers
WORKDIR /opt
RUN git clone https://github.com/strasdat/Sophus.git && cd Sophus \
 && git checkout a621ff \
 && sed -i 's/unit_complex_.real() = 1.;/unit_complex_ = std::complex<double>(1, 0);/' sophus/so2.cpp \
 && sed -i 's/unit_complex_.imag() = 0.;//' sophus/so2.cpp \
 && mkdir build && cd build && cmake .. && make -j"$(nproc)" && make install \
 && ldconfig

RUN echo 'source /opt/ros/jazzy/setup.bash' >> /root/.bashrc \
 && echo '[ -f /root/ros2_ws/install/setup.bash ] && source /root/ros2_ws/install/setup.bash' >> /root/.bashrc
WORKDIR /root/ros2_ws
