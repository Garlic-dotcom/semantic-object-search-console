"""The only velocity source during the console's SLAM mode."""
import json
import math
import signal
import time

from geometry_msgs.msg import Twist
from nav_msgs.msg import OccupancyGrid, Odometry
import rclpy
from rclpy.clock import Clock, ClockType
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import DurabilityPolicy, QoSProfile, qos_profile_sensor_data
from rclpy.signals import SignalHandlerOptions
from rclpy.time import Time
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
from tf2_ros import Buffer, TransformException, TransformListener

from .mapping_control import (COMMANDS, MAX_SPEED, MAX_TURN, PULSE_SECONDS,
                              angle_difference, obstacle, short_detour)


def planar(transform):
    p, q = transform.translation, transform.rotation
    yaw = math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
    return p.x, p.y, yaw


class MappingMotion(Node):
    def __init__(self):
        super().__init__('mapping_motion', parameter_overrides=[Parameter('use_sim_time', value=True)])
        self.velocity = self.create_publisher(Twist, '/cmd_vel', 10)
        self.results = self.create_publisher(String, '/mapping/result', 10)
        self.states = self.create_publisher(String, '/mapping/state', 10)
        self.tf = Buffer()
        self.listener = TransformListener(self.tf, self)
        self.scan = self.scan_received = self.odom_received = self.map = None
        self.scan_stamp = None
        self.speed = .12
        self.active = None
        self.keyboard_latched = False
        self.blocked_heading = None
        self.last_state = dict(status='idle', message='等待运动指令。')
        self.next_state = 0.
        self.create_subscription(LaserScan, '/scan', self.receive_scan, qos_profile_sensor_data)
        self.create_subscription(Odometry, '/odom', self.receive_odom, qos_profile_sensor_data)
        self.create_subscription(OccupancyGrid, '/map', self.receive_map,
                                 QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL))
        self.create_subscription(String, '/mapping/command', self.receive_command, 10)
        self.create_subscription(Twist, '/mapping/keyboard', self.receive_keyboard, 10)
        self.wall_clock = Clock(clock_type=ClockType.STEADY_TIME)
        self.create_timer(.05, self.step, clock=self.wall_clock)

    def receive_scan(self, message):
        stamp = Time.from_msg(message.header.stamp).nanoseconds
        if self.scan_stamp is None or stamp > self.scan_stamp:
            self.scan,self.scan_stamp,self.scan_received = message,stamp,time.monotonic()

    def receive_map(self, message):
        self.map = message

    def receive_odom(self, message):
        self.odom_received = time.monotonic()

    def pose(self):
        transform = self.tf.lookup_transform('map', 'base_footprint', Time())
        stamp = Time.from_msg(transform.header.stamp).nanoseconds
        age = self.get_clock().now().nanoseconds-stamp
        if not -500_000_000 <= age <= 850_000_000:
            raise ValueError('定位数据已过期。')
        return planar(transform.transform)

    def points(self):
        now = time.monotonic()
        if (self.scan_received is None or self.odom_received is None
                or now-self.scan_received > .65 or now-self.odom_received > .65):
            raise ValueError('雷达或里程计数据过期。')
        scan = self.scan
        # Fresh receipt guards against a publisher re-sending the same old scan.
        age = self.get_clock().now().nanoseconds-Time.from_msg(scan.header.stamp).nanoseconds
        if not -100_000_000 <= age <= 650_000_000:
            raise ValueError('雷达时间戳无效。')
        if (len(scan.ranges)*scan.angle_increment < 6.0
                or not 0 < scan.range_min < scan.range_max):
            raise ValueError('雷达覆盖不足。')
        tf = self.tf.lookup_transform('base_footprint', scan.header.frame_id, Time())
        x,y,yaw = planar(tf.transform)
        points = []
        unknown = 0
        largest_gap = gap = prefix_gap = 0
        seen_clear = False
        for index,distance in enumerate(scan.ranges):
            valid = (distance == math.inf or math.isfinite(distance)
                     and scan.range_min <= distance <= scan.range_max)
            if not valid:
                unknown += 1
                gap += 1
                if not seen_clear:
                    prefix_gap += 1
                largest_gap = max(largest_gap,gap)
                continue
            seen_clear = True
            gap = 0
            if distance == math.inf:
                continue
            angle = scan.angle_min+index*scan.angle_increment+yaw
            points.append((x+distance*math.cos(angle),y+distance*math.sin(angle)))
        if unknown > len(scan.ranges)*.25 or max(largest_gap,gap+prefix_gap)*scan.angle_increment > .25:
            raise ValueError('雷达存在连续的无效量测，已停车。')
        return points

    def twist(self, linear=0., angular=0.):
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = float(angular)
        self.velocity.publish(msg)

    def event(self, command, status, message, **detail):
        result = dict(request_id=command.get('id'), command=command.get('mode'),
                      source=command.get('source'), status=status, message=message,
                      speed_m_s=max(.22,self.speed) if command.get('source')=='keyboard' else self.speed, **detail)
        self.last_state = result
        self.states.publish(String(data=json.dumps(result,ensure_ascii=False)))
        if status != 'moving':
            self.get_logger().info(message)
            if command.get('id'):
                self.results.publish(String(data=json.dumps(result,ensure_ascii=False)))

    def finish(self, status, message, **details):
        operation = self.active
        self.active = None
        self.twist()
        if operation:
            if operation['source']=='keyboard':
                self.keyboard_latched = status in ('blocked','rejected')
            self.event(operation,status,message,**details)

    def receive_command(self, message):
        try:
            command = json.loads(message.data)
            if not isinstance(command,dict) or not isinstance(command.get('id'),str):
                return
            mode = command['mode']
            if mode not in COMMANDS:
                raise ValueError('运动指令未识别。')
            if mode == 'stop':
                target = command.get('target')
                if self.active and (target is None or self.active['id']==target):
                    self.finish('canceled','已停车，请重新下达指令。')
                self.event(command,'completed','停止请求已处理。')
                return
            if self.active:
                self.event(command,'rejected','正在执行另一条运动指令，请先停止。')
                return
            if mode in ('faster','slower'):
                self.speed = min(MAX_SPEED,max(.06,self.speed+(.03 if mode=='faster' else -.03)))
                self.event(command,'completed',f'行进速度已设为 {self.speed:.2f} m/s。')
                return
            route = None
            if mode == 'detour':
                if self.blocked_heading is None or self.map is None or self.map.header.frame_id!='map':
                    raise ValueError('没有可用于绕行的受阻方向或地图。请重新下达指令。')
                points = self.points()
                x,y,yaw = self.pose()
                c,s = math.cos(yaw),math.sin(yaw)
                mapped = [(x+c*u-s*v,y+s*u+c*v) for u,v in points]
                route = short_detour(self.map,(x,y),self.blocked_heading,mapped)
                if not route:
                    raise ValueError('已探索区域内没有足够宽的绕行路线。请重新下达指令。')
            command.update(deadline=time.monotonic()+(55 if route else PULSE_SECONDS),route=route)
            if not route:
                self.blocked_heading = None
            self.active = command
            self.event(command,'moving','正在执行绕行。' if route else '正在执行短时运动。')
        except (KeyError,TypeError,ValueError,TransformException) as error:
            if isinstance(locals().get('command'),dict):
                self.event(command,'rejected',str(error))

    def receive_keyboard(self, message):
        linear,angular=message.linear.x,message.angular.z
        if not (math.isfinite(linear) and math.isfinite(angular)):
            return
        if not linear and not angular:
            if self.active and self.active['source']=='keyboard':
                self.finish('canceled','键盘已松开，机器人已停车。')
            self.keyboard_latched=False
            return
        if self.keyboard_latched or (self.active and self.active['source']!='keyboard'):
            return
        mode=('forward' if linear>0 else 'backward') if linear else ('left' if angular>0 else 'right')
        deadline=time.monotonic()+.7
        if self.active:
            self.active.update(mode=mode,deadline=deadline)
            return
        self.active=dict(id=None,mode=mode,source='keyboard',route=None,deadline=deadline)
        self.event(self.active,'moving','正在执行键盘运动。')

    def step(self):
        now = time.monotonic()
        if now >= self.next_state:
            self.states.publish(String(data=json.dumps(self.last_state,ensure_ascii=False)))
            self.next_state = now+.5
        job = self.active
        if job is None:
            self.twist()
            return
        mode = job['mode']
        if now>=job['deadline']:
            if job['source']=='keyboard':
                self.finish('canceled','键盘信号已停止，机器人已停车。')
                return
            detour = mode=='detour'
            self.finish('failed' if detour else 'completed',
                        '绕行超时，已停车。' if detour else '本次短时运动结束，已停车。')
            return
        try:
            points = self.points()
            if self.count_publishers('/cmd_vel') != 1:
                raise ValueError('检测到其他速度发布者，已停车。')
            x,y,yaw = self.pose()
            if mode == 'detour':
                route = job['route']
                while route and math.dist((x,y),route[0])<=.075:
                    route.pop(0)
                if not route:
                    self.blocked_heading = None
                    self.finish('completed','绕行完成，已停车。请重新下达指令。')
                    return
                u,v = route[0]
                error = angle_difference(math.atan2(v-y,u-x),yaw)
                linear = .12 if abs(error)<.18 else 0.
                angular = min(MAX_TURN,max(-MAX_TURN,1.4*error))
            else:
                speed = max(self.speed,.22) if job['source']=='keyboard' else self.speed
                linear = {'forward':speed,'backward':-speed}.get(mode,0.)
                angular = {'left':.55,'right':-.55}.get(mode,0.)
            distance = obstacle(points,linear,angular)
            if distance is not None:
                self.blocked_heading = yaw+(math.pi if linear<0 else 0) if linear else None
                self.finish('blocked',f'检测到 {distance:.2f} m 的障碍，已停车。请重新下达指令。',
                            obstacle_distance_m=round(distance,3))
                return
            self.twist(linear,angular)
        except (ValueError,TransformException) as error:
            self.finish('rejected',str(error)+' 请重新下达指令。')


def main():
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    stopped = []
    for sig in (signal.SIGINT,signal.SIGTERM):
        signal.signal(sig,lambda signum, frame:stopped.append(signum))
    node = MappingMotion()
    try:
        while not stopped and rclpy.ok():
            rclpy.spin_once(node,timeout_sec=.05)
    finally:
        node.finish('canceled','建图运动节点退出，已停车。')
        for _ in range(3):
            node.twist()
            time.sleep(.05)
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
