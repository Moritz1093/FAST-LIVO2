"""FAST-LIVO2 (ROS2): AVIACAM scanner (Livox Avia + compressed camera images).
All arguments of mapping.launch.py can be given, e.g. rviz:=false img_transport:=compressed."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    share = get_package_share_directory('fast_livo')
    defaults = {
        'config_file': os.path.join(share, 'config', 'aviacam.yaml'),
        'camera_file': os.path.join(share, 'config', 'camera_aviacam.yaml'),
        'rviz_config': os.path.join(share, 'rviz_cfg', 'fast_livo2.rviz'),
    }
    return LaunchDescription(
        [DeclareLaunchArgument(name, default_value=value) for name, value in defaults.items()] + [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(os.path.join(share, 'launch', 'mapping.launch.py')),
                launch_arguments={name: LaunchConfiguration(name) for name in defaults}.items()),
        ])
