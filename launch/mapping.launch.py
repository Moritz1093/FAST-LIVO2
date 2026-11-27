"""FAST-LIVO2 (ROS2): generic launch file. The dataset launch files (mapping_*.launch.py) set the defaults.

Arguments:
  config_file     LiDAR/IMU/VIO parameter file (default: config/avia.yaml)
  camera_file     camera parameter file (default: config/camera_pinhole.yaml)
  rviz            start rviz2 (default: true)
  rviz_config     rviz2 config (default: rviz_cfg/fast_livo2.rviz)
  img_transport   override common.img_transport: raw | compressed (default: value from config_file)
  livox_msg_type  override common.livox_msg_type: livox_ros_driver | livox_interfaces | livox_ros_driver2
                  (default: value from config_file)
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _nodes(context):
    get = lambda name: LaunchConfiguration(name).perform(context)
    overrides = {}
    if get('img_transport'):
        overrides['common.img_transport'] = get('img_transport')
    if get('livox_msg_type'):
        overrides['common.livox_msg_type'] = get('livox_msg_type')
    parameters = [get('config_file'), get('camera_file')] + ([overrides] if overrides else [])
    return [
        Node(package='fast_livo', executable='fastlivo_mapping', name='laserMapping', output='screen',
             parameters=parameters),
        Node(package='rviz2', executable='rviz2', name='rviz', prefix='nice', output='screen',
             arguments=['-d', get('rviz_config')], condition=IfCondition(get('rviz'))),
    ]


def generate_launch_description():
    share = get_package_share_directory('fast_livo')
    return LaunchDescription([
        DeclareLaunchArgument('config_file', default_value=os.path.join(share, 'config', 'avia.yaml')),
        DeclareLaunchArgument('camera_file', default_value=os.path.join(share, 'config', 'camera_pinhole.yaml')),
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument('rviz_config', default_value=os.path.join(share, 'rviz_cfg', 'fast_livo2.rviz')),
        DeclareLaunchArgument('img_transport', default_value='', description='raw | compressed (empty: from config_file)'),
        DeclareLaunchArgument('livox_msg_type', default_value='',
                              description='livox_ros_driver | livox_interfaces | livox_ros_driver2 (empty: from config_file)'),
        OpaqueFunction(function=_nodes),
    ])
