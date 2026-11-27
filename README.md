# FAST-LIVO2

> **Fork note (Moritz1093/FAST-LIVO2):** `main` is a **ROS2 (Jazzy) port**. The last ROS1 (Noetic) version is
> the tag [`ros1-final`](https://github.com/Moritz1093/FAST-LIVO2/tree/ros1-final) (maintenance branch `ros1-fixes`).
> Compared with [hku-mars/FAST-LIVO2](https://github.com/hku-mars/FAST-LIVO2) the fork adds support for
> **compressed camera images**, a config for the AVIACAM scanner and selected bug fixes from upstream pull
> requests (see below). The algorithm is unchanged.
>
> ### ROS2 port
>
> The ROS interface was ported; parameters, topics, frames and defaults are the same as in ROS1
> (`common/lid_topic` in ROS1 is `common.lid_topic` in ROS2). Time stamps are converted exactly as in ROS1.
> Configs are ROS2 parameter files, launch files are Python (`ros2 launch fast_livo mapping_avia.launch.py`).
> All launch files take the arguments `rviz`, `config_file`, `camera_file`, `rviz_config`, `img_transport` and
> `livox_msg_type`, e.g. `ros2 launch fast_livo mapping_avia.launch.py rviz:=false img_transport:=compressed`.
>
> **LiDAR input.** `preprocess.lidar_type` selects the input as before: Livox (`1`) uses Livox `CustomMsg`,
> all other LiDARs `sensor_msgs/msg/PointCloud2`. The Livox `CustomMsg` exists under three type names with the
> same fields; `common.livox_msg_type` selects it:
>
> | `livox_msg_type` | Message type | Source |
> |---|---|---|
> | `livox_ros_driver` (default) | `livox_ros_driver/msg/CustomMsg` | ROS1 bags converted to ROS2 (message package `livox_ros_driver`, see 2.5) |
> | `livox_interfaces` | `livox_interfaces/msg/CustomMsg` | [livox_ros2_driver](https://github.com/Livox-SDK/livox_ros2_driver) (Livox SDK1, e.g. Avia) |
> | `livox_ros_driver2` | `livox_ros_driver2/msg/CustomMsg` | [livox_ros_driver2](https://github.com/Livox-SDK/livox_ros_driver2) (Livox SDK2, e.g. Mid-360) |
>
> `livox_interfaces` and `livox_ros_driver2` are built in only if their package is found when `fast_livo` is
> built (build or source it first). If the LiDAR topic is published with another type than configured, the node
> prints a warning with the setting to use.
>
> **Camera input.** The image is subscribed via `image_transport`; `common.img_transport` selects how:
>
> | `img_transport` | `img_topic` (base topic) | Subscribed topic | Message type |
> |---|---|---|---|
> | `raw` (default, same as upstream) | `/camera/image_raw` | `/camera/image_raw` | `sensor_msgs/msg/Image` |
> | `compressed` | `/camera/image` | `/camera/image/compressed` | `sensor_msgs/msg/CompressedImage` |
>
> For `compressed`, set `img_topic` to the topic **without** the `/compressed` suffix; image_transport appends it.
> Requires `compressed_image_transport` (`sudo apt install ros-jazzy-image-transport-plugins`). The ROS1
> `republish` node is not needed. Other plugins (e.g. `theora`) work the same way if installed.
>
> **Live sensors (QoS).** The node subscribes to LiDAR, IMU and camera as *reliable*. A driver that publishes
> *best effort* (e.g. many camera drivers, `SensorDataQoS`) does not connect: no data arrives, ROS2 only prints
> an incompatible-QoS warning. Publish reliable, with a deep history for the IMU (e.g. 1000 messages), so that
> nothing is dropped when the node falls behind for a moment. Bags recorded with ROS2 store this QoS and play
> back with it; for bags converted from ROS1 see `config/play_qos.yaml` in section 4.
>
> Config for the AVIACAM scanner (Livox Avia + hardware-synced camera, compressed images):
> `ros2 launch fast_livo mapping_aviacam.launch.py` (`config/aviacam.yaml`, `config/camera_aviacam.yaml`).
>
> **Bug fixes** (cherry-picked, original authors kept):
> [#90](https://github.com/hku-mars/FAST-LIVO2/pull/90) (NaN/zero IMU dt),
> [#465](https://github.com/hku-mars/FAST-LIVO2/pull/465) (first-point undistortion, VIO leak/uninitialized
> memory/out-of-bounds reads, per-point mutex removed),
> [#455](https://github.com/hku-mars/FAST-LIVO2/pull/455) (VIO no longer waits on the LiDAR buffer; lower latency live),
> plus IMU/images buffered before the first LiDAR frame for a deterministic start
> (ported from [samuelyhsu/FAST-LIVO2@018258d](https://github.com/samuelyhsu/FAST-LIVO2/commit/018258d)).
> Own fix, found during the ROS2 port: the VIO update sums the patch errors in a fixed order (the OpenMP float
> reduction made runs differ slightly from run to run).
>
> Tested on ROS1 Noetic, tag `ros1-final` (`rosbag play -d 2`, all messages received; no crashes or dropped frames in any run):
>
> | Test | `main` (upstream) | with fixes |
> |---|---|---|
> | FAST-LIVO2-Dataset (Retail_Street, CBD_Building_01, Bright_Screen_Wall), 5 runs each: time per frame | 14.1–40.0 ms | **15–21 % less** |
> | same: run-to-run difference | ~0.4 cm | **0.00 cm** (identical) |
> | NTU-VIRAL eee_01, 3 runs: error vs. ground truth (APE RMSE) | 2.51 cm | 2.50 cm |
> | same: time per frame | 23.0 ms | 21.8 ms (−5 %) |
>
> Tested on ROS2 Jazzy, `main` against `ros1-final` (same bags converted to mcap, `ros2 bag play --delay 5` with the
> player's QoS history raised so that no message is dropped; all messages received, no crashes or dropped frames):
>
> | Test | ROS1 `ros1-final` | ROS2 `main` |
> |---|---|---|
> | FAST-LIVO2-Dataset (Retail_Street, CBD_Building_01, Bright_Screen_Wall), 5 runs each: time per frame | 11.8–32.9 ms | 11.8–31.6 ms (0–4 % less) |
> | same: run-to-run difference | 0.00 cm | **0.00 cm** (identical) |
> | same: difference ROS1 ↔ ROS2 (APE RMSE) | – | 0.55–0.58 cm (rounding) |
> | same: memory at the end (RSS) | 439–865 MB | 1–9 % less |
> | NTU-VIRAL eee_01, 3 runs: error vs. ground truth (APE RMSE) | 2.50 cm | 2.50 cm |
> | same: time per frame | 21.5 ms | 21.2 ms (−1 %) |
>
> Known issue: on NTU-VIRAL the runs still differ slightly from run to run, in ROS1 as well (median 0.5 cm in ROS1,
> 2.7 cm in ROS2, 3 runs each; all images and LiDAR scans received); the cause is not found yet. The error vs.
> ground truth stays at 2.49–2.51 cm in every run.
>
> **Not included:** [#311](https://github.com/hku-mars/FAST-LIVO2/pull/311) (covariance with attitude/extrinsics)
> gave no measurable accuracy gain on NTU-VIRAL (2.50 cm) at +3–5 % time per frame;
> [#466](https://github.com/hku-mars/FAST-LIVO2/pull/466) (scan spanning several images) gave no accuracy gain
> and made runs timing-dependent (one NTU run off by 4.5 cm).

## FAST-LIVO2: Fast, Direct LiDAR-Inertial-Visual Odometry

### 📢 News

- 🔓 **2025-01-23**: Code released!  
- 🎉 **2024-10-01**: Accepted by **T-RO '24**!  
- 🚀 **2024-07-02**: Conditionally accepted.

### 📬 Contact

For further inquiries or assistance, please contact [zhengcr@connect.hku.hk](mailto:zhengcr@connect.hku.hk).

## 1. Introduction

FAST-LIVO2 is an efficient and accurate LiDAR-inertial-visual fusion localization and mapping system, demonstrating significant potential for real-time 3D reconstruction and onboard robotic localization in severely degraded environments.

**Developer**: [Chunran Zheng 郑纯然](https://github.com/xuankuzcr)

<div align="center">
    <img src="pics/Framework.png" width = 100% >
</div>

### 1.1 Related video

Our accompanying video is now available on [**Bilibili**](https://www.bilibili.com/video/BV1Ezxge7EEi) and [**YouTube**](https://youtu.be/6dF2DzgbtlY).

### 1.2 Related paper

[FAST-LIVO2: Fast, Direct LiDAR-Inertial-Visual Odometry](https://arxiv.org/pdf/2408.14035)  

[FAST-LIVO2 on Resource-Constrained Platforms](https://arxiv.org/pdf/2501.13876)  

[FAST-LIVO: Fast and Tightly-coupled Sparse-Direct LiDAR-Inertial-Visual Odometry](https://arxiv.org/pdf/2203.00893)

[FAST-Calib: LiDAR-Camera Extrinsic Calibration in One Second](https://www.arxiv.org/pdf/2507.17210)

### 1.3 Our hard-synchronized equipment

We open-source our handheld device, including CAD files, synchronization scheme, STM32 source code, wiring instructions, and sensor ROS driver. Access these resources at this repository: [**LIV_handhold**](https://github.com/xuankuzcr/LIV_handhold).

### 1.4 Our associate dataset: FAST-LIVO2-Dataset
Our associate dataset [**FAST-LIVO2-Dataset**](https://connecthkuhk-my.sharepoint.com/:f:/g/personal/zhengcr_connect_hku_hk/ErdFNQtjMxZOorYKDTtK4ugBkogXfq1OfDm90GECouuIQA?e=KngY9Z) used for evaluation is also available online.

### 1.5 Our LiDAR-camera calibration method
The [**FAST-Calib**](https://github.com/hku-mars/FAST-Calib) toolkit is recommended. Its output extrinsic parameters can be directly filled into the YAML file. 

## 2. Prerequisited

### 2.1 Ubuntu and ROS2

Ubuntu 24.04, ROS2 Jazzy. [ROS2 Installation](https://docs.ros.org/en/jazzy/Installation.html).
For ROS1 (Ubuntu 18.04~20.04) use the tag `ros1-final`.

### 2.2 PCL && Eigen && OpenCV && ROS packages

From Ubuntu/ROS2 packages (tested: PCL 1.14, Eigen 3.4, OpenCV 4.6):

```bash
sudo apt install libpcl-dev libeigen3-dev libopencv-dev python3-colcon-common-extensions \
  ros-jazzy-pcl-ros ros-jazzy-pcl-conversions ros-jazzy-cv-bridge ros-jazzy-image-transport \
  ros-jazzy-image-transport-plugins ros-jazzy-tf2-ros ros-jazzy-rosbag2-storage-mcap
```

### 2.3 Sophus

Sophus Installation for the non-templated/double-only version.

```bash
git clone https://github.com/strasdat/Sophus.git
cd Sophus
git checkout a621ff
sed -i 's/unit_complex_.real() = 1.;/unit_complex_ = std::complex<double>(1, 0);/' sophus/so2.cpp
sed -i 's/unit_complex_.imag() = 0.;//' sophus/so2.cpp
mkdir build && cd build && cmake ..
make
sudo make install
sudo ldconfig
```

(The two `sed` lines are needed with newer compilers.)

### 2.4 Vikit

Vikit contains camera models, some math and interpolation functions that we need. Use the ROS2 version
(ament packages `vikit_common`, `vikit_ros`):

```bash
cd ~/ros2_ws/src
git clone -b ros2 https://github.com/Moritz1093/rpg_vikit.git
```

### 2.5 Livox message package

The ROS2 message package `livox_ros_driver` (only `CustomMsg`/`CustomPoint`, no driver, no Livox SDK) keeps
the type name of ROS1 Livox bags:

```bash
cd ~/ros2_ws/src
git clone https://github.com/Moritz1093/livox_ros_driver_msgs.git
```

(The repository is named `livox_ros_driver_msgs`; the ROS2 package inside is `livox_ros_driver`.)

## 3. Build

Clone the repository and build with colcon:

```
cd ~/ros2_ws/src
git clone https://github.com/Moritz1093/FAST-LIVO2
cd ..
colcon build --packages-up-to fast_livo
source install/setup.bash
```

### 3.1 Docker (optional)

`docker/Dockerfile` builds an image with all dependencies of section 2.2 and 2.3 (tested setup). The sources
stay on the host in a workspace that is mounted into the container:

```
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
git clone -b ros2 https://github.com/Moritz1093/rpg_vikit.git
git clone https://github.com/Moritz1093/livox_ros_driver_msgs.git
git clone https://github.com/Moritz1093/FAST-LIVO2
docker build -t fast_livo2_ros2:jazzy FAST-LIVO2/docker
xhost +local:   # only for rviz2
docker run -it --name fast_livo2_ros2 --net host -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v ~/ros2_ws:/root/ros2_ws -v ~/bags:/bags fast_livo2_ros2:jazzy
# in the container:
colcon build --packages-up-to fast_livo && source install/setup.bash
```

## 4. Run our examples

Download FAST-LIVO2-Dataset from [Global-LVBA](https://github.com/xuankuzcr/Global-LVBA) Section IV.
The dataset is recorded with ROS1; convert the bags to ROS2 (mcap) first with
[rosbags](https://gitlab.com/ternaris/rosbags) (no ROS1 installation needed):

```
pip install rosbags
rosbags-convert --src Retail_Street.bag --dst Retail_Street --dst-storage mcap
```

Message contents and time stamps stay the same; Livox messages keep the type `livox_ros_driver/msg/CustomMsg`
(default `livox_msg_type`). `--include-topic` keeps only the given topics (e.g. to leave out unused topics of
large bags).

```
ros2 launch fast_livo mapping_avia.launch.py
ros2 bag play --delay 2 --qos-profile-overrides-path config/play_qos.yaml Retail_Street
```

`--delay 2` gives the node time to connect; without it the first messages of the bag can be lost.
`config/play_qos.yaml` (path relative to this source folder) gives the player a deep message history:
converted bags carry no QoS profiles, so the player would keep only 10 messages per topic, and under CPU load
IMU messages are lost before they reach the node (results then differ from run to run). For other topics, add
them to the file in the same way.
For bags with compressed images (e.g. Bright_Screen_Wall) add `img_transport:=compressed` to the launch command.

Results (poses with `evo.pose_output_en`, point clouds with `pcd_save.pcd_save_en`) are written to `Log/`
in the source folder, as in ROS1.

## 5. License

The source code of this package is released under the [**GPLv2**](http://www.gnu.org/licenses/) license. For commercial use, please contact me at <zhengcr@connect.hku.hk> and Prof. Fu Zhang at <fuzhang@hku.hk> to discuss an alternative license.
