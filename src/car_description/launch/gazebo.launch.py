import os
from launch import LaunchDescription
from launch.substitutions import Command
# 新增：启动顺序、延时、仿真时间相关模块
from launch.actions import ExecuteProcess, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessStart
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
    # RViz 配置文件路径（新增）
    rviz_config_path = os.path.join(pkg_share, 'rviz/ld_depth.rviz')
    # 自定义world路径 hello1.world
    world_file = os.path.join(pkg_share, 'world/hello2.world')


    # 1. 启动 Gazebo 空环境
    gazebo_node = ExecuteProcess(
        cmd=['gazebo', '--verbose', world_file,'-s', 'libgazebo_ros_factory.so'],
        output='screen'
    )

    # 2. 机器人状态发布 + 【修改点1】开启仿真时间 use_sim_time
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description},
                    {'use_sim_time': True}  # 新增：同步Gazebo仿真时间，必加
                ]
    )

    # 3. 将机器人 spawn 到 Gazebo 中
    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'carbot', '-topic', 'robot_description', '-x', '0.0', '-y', '0.0', '-z', '0.15'],
        output='screen'
    )

     # ========== 【修改：带配置文件的 RViz2 节点】 ==========
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_path],  # 自动加载你的 rviz
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    # ===================== 【修改点2】添加启动顺序约束（关键） =====================
    # 逻辑： 启动顺序：Gazebo → RSP → Spawn → RViz
    # 1. 先添加Gazebo
    ld.add_action(gazebo_node)
     # 2. Gazebo启动后，延时1秒再启动robot_state_publisher
    delay_after_gazebo = TimerAction(
        period=1.0,
        actions=[robot_state_publisher_node]
    )
    ld.add_action(delay_after_gazebo)

    # 3. robot_state_publisher 启动后，再延时1秒生成模型
    spawn_after_rsp = RegisterEventHandler(
        OnProcessStart(
            target_action=robot_state_publisher_node,
            on_start=[TimerAction(period=1.0, actions=[spawn_entity_node])]
        )
    )
    ld.add_action(spawn_after_rsp)

    # 模型生成完成后，再延时1秒启动 RViz
    rviz_after_spawn = RegisterEventHandler(
        OnProcessStart(
            target_action=spawn_entity_node,
            on_start=[TimerAction(period=1.0, actions=[rviz_node])]
        )
    )
    # ld.add_action(rviz_after_spawn)  # 在使用nav时 不需要启动

    return ld