import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    car_navigation2_dir = get_package_share_directory('car_navigation2')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    slam_toolbox_dir = get_package_share_directory('slam_toolbox')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    nav2_param_path = LaunchConfiguration('params_file', default=os.path.join(car_navigation2_dir, 'param', 'car_nav2.yaml'))
    rviz_config_dir = os.path.join(nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz')
    map_yaml_path = os.path.join(car_navigation2_dir, 'maps', 'car1_map.yaml')

    nav2_navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([nav2_bringup_dir, '/launch', '/navigation_launch.py']),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': nav2_param_path,
            'autostart': 'True',
            'use_composition': 'False',
            'use_respawn': 'False',
            'log_level': 'info'
        }.items(),
    )

    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'yaml_filename': map_yaml_path, 'use_sim_time': use_sim_time}],
        arguments=['--ros-args', '--log-level', 'info']
    )

    map_server_lifecycle = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': True,
            'node_names': ['map_server']
        }],
        arguments=['--ros-args', '--log-level', 'info']
    )
    

    slam_toolbox_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([slam_toolbox_dir, '/launch', '/localization_launch.py']),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam_params_file': nav2_param_path
        }.items(),
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_dir],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        map_server_node,
        map_server_lifecycle,
        slam_toolbox_launch,
        nav2_navigation_launch,
        rviz_node,
    ])