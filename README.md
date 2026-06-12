# 项目名称
一个基于两轮差速器的四轮差速小车 长度75cm 宽度9cm  带深度相机 激光雷达 可实现在排水管道进行作业 巡检等 
## 功能特性
- 核心功能1 完成基于两轮差速器的四轮差速小车 长度75cm 宽度9cm 带深度相机 激光雷达
- 核心功能2 可依靠cartograph进行实时定位与建图(2D)
- 核心功能3 依靠carto建造的图使用nav2去实时导航 给予目标点 靠近目标点 基于nav2默认的amcl

## 环境依赖
列出运行代码需要的依赖包/软件版本（比如）：
- Ubuntu22.04
- ROS 2 Humble
- Gazebo 11.x
- Python3.10
## 快速开始
### 1. 安装依赖
car_description（URDF+Gazebo 仿真）
依赖：xacro、robot_state_publisher、gazebo_ros2_control、diff_drive_controller
car_navigation2（Nav2+AMCL + 代价地图）
依赖：nav2_bringup、nav2_amcl、nav2_costmap_2d、tf2_ros
car_cartographer（建图包）
依赖：cartographer_ros、laser_geometry
###2.Gazebo 仿真 + 机器人 URDF 依赖
# Gazebo仿真、ros2控制插件
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros2-control
# 差速底盘控制器、硬件接口
sudo apt install ros-humble-ros2-control ros-humble-ros2-controllers
# URDF、xacro解析工具
sudo apt install ros-humble-xacro ros-humble-robot-state-publisher
# 激光雷达消息、坐标变换
sudo apt install ros-humble-laser-geometry ros-humble-tf2-tools ros-humble-tf2-ros
###3.RViz 可视化、调试工具
sudo apt install ros-humble-rviz2 ros-humble-rqt*
建图配套（Cartographer/SLAM，你工程里有 car_cartographer 包）
sudo apt install ros-humble-cartographer ros-humble-cartographer-ros
4. Python 编译 & ament 工具链（launch 文件运行必需）
sudo apt install python3-colcon-common-extensions python3-pip
sudo apt install python3-ament-index-python


=========================================
一、✅ 已正常可用的基础功能
1. 仿真硬件层
Gazebo 仿真环境正常启动，四轮小车模型完整加载；
URDF+xacro 解析正常，robot_state_publisher 无报错；
底盘差速驱动插件生效，/odom 里程计话题持续稳定发布；
激光雷达正常工作，/scan 话题稳定 7~8Hz 输出点云数据；
TF 坐标树完整闭环：map → odom → base_footprint → base_link → 车轮/雷达/相机，所有坐标变换持续广播，无丢帧、无缺失。
2. 定位与地图层
map_server 可以加载你自制 hello2/car1_map.yaml 静态地图，/map 话题正常发布；
AMCL 粒子滤波定位节点成功启动，完成 map 与 odom 坐标系绑定；
RViz 可加载自定义保存的配置文件，机器人模型、激光雷达、全局静态地图均可正常可视化。
3. 导航框架部署
Nav2 Bringup 整套启动流程可正常拉起，生命周期管理容器、控制器服务器、规划服务器、行为树导航节点全部启动；
支持手动 2D Pose Estimate 给定小车初始定位位姿；
支持下发 2D Nav Goal 单点自主导航指令。
二、❌ 当前阻塞待修复功能
局部代价地图（膨胀层）无法发布：/local_costmap/costmap 无话题输出，障碍物膨胀安全区看不到，局部路径规划缺少实时障碍物检测；
无法直观在 RViz 查看障碍物膨胀缓冲区，局部避障逻辑无法验证；
全局代价地图同步无法可视化校验。
三、🚗 完整可用后能实现的全部小车功能
基础运动功能
键盘 / 速度话题 /cmd_vel 手动遥控小车前后、转向行驶；
里程计实时解算小车位置，可记录运动轨迹。
自主导航功能
AMCL 静态地图精准定位，任意初始位置自动校正位姿；
全局路径规划：从起点到目标点规划最优全局路径；
局部动态避障：依靠激光雷达 + 局部代价地图，躲避仿真内新增障碍物；
多目标点连续巡航、循迹导航。
拓展传感器功能
深度相机、IMU 数据接入，后续可升级 3D 代价地图、融合 IMU 提升定位鲁棒性。
=========================================




