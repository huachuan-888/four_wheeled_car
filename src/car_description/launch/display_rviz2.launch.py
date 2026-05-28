import os
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    package_name = 'car_description'
    urdf_name = "car_robot.urdf.xacro"
    rviz_config_name = "tf_rviz.rviz"

    ld = LaunchDescription()
    pkg_share = FindPackageShare(package=package_name).find(package_name)

    # 1. 关键：用 xacro 命令把 .xacro 转成 urdf 字符串
    urdf_path = os.path.join(pkg_share, 'urdf', urdf_name)
    robot_description = Command(['xacro ', urdf_path])

    # 2. RViz 配置路径
    rviz_config_path = os.path.join(pkg_share, 'rviz', rviz_config_name)

    # 3. robot_state_publisher：通过参数传入 urdf，而不是传文件名
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}]  
    )

    # 4. RViz2
    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path]
    )

    ld.add_action(robot_state_publisher_node)
    ld.add_action(rviz2_node)

    return ld