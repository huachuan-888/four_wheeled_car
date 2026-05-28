import os
from launch import LaunchDescription
from launch.substitutions import Command
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    package_name = 'car_description'
    urdf_name = "car_robot.urdf.xacro"

    ld = LaunchDescription()
    pkg_share = FindPackageShare(package=package_name).find(package_name) 

    # 关键：xacro 转成 URDF 字符串
    urdf_path = os.path.join(pkg_share, f'urdf/{urdf_name}')
    robot_description = Command(['xacro ', urdf_path])

    # 1. 启动 Gazebo 空环境
    gazebo_node = ExecuteProcess(
        cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so'],
        output='screen'
    )

    # 2. 机器人状态发布
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}]
    )

    # 3. 将机器人 spawn 到 Gazebo 中
    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'carbot', '-topic', 'robot_description', '-x', '0.0', '-y', '0.0', '-z', '0.15'],
        output='screen'
    )

    ld.add_action(gazebo_node)
    ld.add_action(robot_state_publisher_node)
    ld.add_action(spawn_entity_node)

    return ld