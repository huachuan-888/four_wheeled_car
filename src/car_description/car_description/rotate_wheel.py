#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import threading
import time
import sys
import termios
import tty

#这个文件实现了一个ROS2节点，名为RotateWheelNode，用于控制四轮车的轮子旋转。
#通过键盘输入（i、k、j、l、空格）来控制车的前进、后退、左转、右转和停止。
#节点会发布JointState消息，更新四个轮子的速度和位置，从而在RViz中显示轮子的运动效果。

class RotateWheelNode(Node):
    def __init__(self,name):
        super().__init__(name)
        self.get_logger().info(f"node {name} init..")
        self.get_logger().info("===== 键盘控制 =====")
        self.get_logger().info("i：前进   k：后退   j：左转   l：右转   空格：停止")

        # 创建发布者
        self.joint_states_publisher_ = self.create_publisher(JointState,"joint_states", 10) 
        
        # 初始化关节数据（4个轮子）
        self._init_joint_states()
        self.pub_rate = self.create_rate(30)
        
        # 速度控制
        self.wheel_speed = 0.0
        
        # 发布线程
        self.thread_ = threading.Thread(target=self._thread_pub)
        self.thread_.start()

    def _init_joint_states(self):
        self.joint_states = JointState()
        self.joint_states.header.stamp = self.get_clock().now().to_msg()
        self.joint_states.header.frame_id = ""
        
        # 【关键】你的四个轮子关节名
        self.joint_states.name = [
            'left_front_wheel_joint',
            'right_front_wheel_joint',
            'left_back_wheel_joint',
            'right_back_wheel_joint'
        ]
        
        self.joint_states.position = [0.0, 0.0, 0.0, 0.0]
        self.joint_states.velocity = [0.0, 0.0, 0.0, 0.0]
        self.joint_states.effort = []

    # 速度：左两轮，右两轮
    def update_speed(self, left_speed, right_speed):
        self.joint_states.velocity[0] = left_speed   # 左前
        self.joint_states.velocity[1] = right_speed  # 右前
        self.joint_states.velocity[2] = left_speed   # 左后
        self.joint_states.velocity[3] = right_speed  # 右后

    def _thread_pub(self):
        last_update_time = time.time()
        while rclpy.ok():
            delta_time = time.time() - last_update_time
            last_update_time = time.time()

            # 更新4个轮子的位置
            self.joint_states.position[0] += delta_time * self.joint_states.velocity[0]
            self.joint_states.position[1] += delta_time * self.joint_states.velocity[1]
            self.joint_states.position[2] += delta_time * self.joint_states.velocity[2]
            self.joint_states.position[3] += delta_time * self.joint_states.velocity[3]

            self.joint_states.header.stamp = self.get_clock().now().to_msg()
            self.joint_states_publisher_.publish(self.joint_states)
            self.pub_rate.sleep()

# 键盘控制
def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key

def main(args=None):
    rclpy.init(args=args)
    node = RotateWheelNode("four_wheel_controller")
    
    # 键盘控制线程
    def key_thread():
        while rclpy.ok():
            key = get_key()
            if key == 'i':
                node.update_speed(15.0, 15.0)
                node.get_logger().info("前进")
            elif key == 'k':
                node.update_speed(-15.0, -15.0)
                node.get_logger().info("后退")
            elif key == 'j':
                node.update_speed(-10.0, 10.0)
                node.get_logger().info("左转")
            elif key == 'l':
                node.update_speed(10.0, -10.0)
                node.get_logger().info("右转")
            elif key == ' ':
                node.update_speed(0.0, 0.0)
                node.get_logger().info("停止")

    thread = threading.Thread(target=key_thread, daemon=True)
    thread.start()

    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()