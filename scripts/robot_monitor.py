#!/usr/bin/env python3
"""Read-only ROS telemetry for the local console; ROS imports are lazy.

The monitor owns only its node/context, and never sends a robot command. All
freshness calculations use monotonic receipt time plus the observed /clock.
"""
from copy import deepcopy
from io import BytesIO
import json
import math
import os
import threading
import time


TOPICS = ('/clock', '/odom', '/scan', '/rgbd/obstacles', '/rgbd/image',
          '/rgbd/depth_image', '/rgbd/camera_info', '/yolo/detections')
SIMULATION_TOPICS = ('/clock', '/odom', '/scan', '/rgbd/obstacles')
PERCEPTION_TOPICS = ('/rgbd/image', '/rgbd/depth_image', '/rgbd/camera_info',
                     '/yolo/detections')
STACK_NODES = {'amcl', 'bt_navigator', 'controller_server', 'planner_server',
               'semantic_search', 'course_detector', 'robot_state_publisher',
               'fortress_depth_cloud_adapter', 'slam_toolbox', 'mapping_motion'}


def stamp_seconds(stamp):
    return float(stamp.sec) + float(stamp.nanosec) / 1e9


def yaw_from_quaternion(rotation):
    x, y, z, w = (float(getattr(rotation, name)) for name in ('x', 'y', 'z', 'w'))
    norm = math.sqrt(x*x+y*y+z*z+w*w)
    if not math.isfinite(norm) or norm < 1e-12:
        raise ValueError('Invalid orientation quaternion')
    x, y, z, w = x/norm, y/norm, z/norm, w/norm
    return math.atan2(2*(w*z+x*y), 1-2*(y*y+z*z))


def transform_pose(message):
    translation = message.transform.translation
    x, y = float(translation.x), float(translation.y)
    if not (math.isfinite(x) and math.isfinite(y)):
        raise ValueError('Invalid map pose')
    return dict(x=x, y=y, yaw=yaw_from_quaternion(message.transform.rotation),
                frame_id=message.header.frame_id,
                stamp_seconds=stamp_seconds(message.header.stamp))


def map_payload(message):
    info = message.info
    width, height, resolution = int(info.width), int(info.height), float(info.resolution)
    if width <= 0 or height <= 0 or width*height != len(message.data):
        raise ValueError('Map dimensions and data length disagree')
    if not math.isfinite(resolution) or resolution <= 0:
        raise ValueError('Map resolution must be positive and finite')
    x, y = float(info.origin.position.x), float(info.origin.position.y)
    if not (math.isfinite(x) and math.isfinite(y)):
        raise ValueError('Invalid map origin')
    return dict(available=True, width=width, height=height, resolution=resolution,
                origin=dict(x=x, y=y, yaw=yaw_from_quaternion(info.origin.orientation)),
                data=[int(value) for value in message.data], frame_id=message.header.frame_id,
                stamp_seconds=stamp_seconds(message.header.stamp))


def scan_obstacles(message, transform, direction=1, rotating=False, map_transform=None):
    """Measured laser points, never obstacle labels or navigation decisions."""
    if (not message.header.frame_id or not math.isfinite(message.angle_increment)
            or message.angle_increment<=0 or len(message.ranges)<8):
        raise ValueError('Invalid laser geometry')
    def point(distance,angle,tf):
        x,y=distance*math.cos(angle),distance*math.sin(angle);q=tf.rotation;t=tf.translation
        return [t.x+(1-2*(q.y*q.y+q.z*q.z))*x+2*(q.x*q.y-q.z*q.w)*y,
                t.y+2*(q.x*q.y+q.z*q.w)*x+(1-2*(q.x*q.x+q.z*q.z))*y]
    points=[];nearest=None;valid=0
    for i,distance in enumerate(message.ranges):
        if distance==math.inf:valid+=1;continue
        if not math.isfinite(distance)or not message.range_min<=distance<=message.range_max:continue
        valid+=1;angle=message.angle_min+i*message.angle_increment
        x,y=point(distance,angle,transform);radius=math.hypot(x,y)
        if radius>2.5:continue
        mapped=point(distance,angle,map_transform)if map_transform is not None else None
        if mapped is not None:points.append(mapped)
        bearing=math.atan2(y,x)
        in_direction=rotating or direction*x>0 and abs(y)<=abs(x)*math.tan(math.pi/3)
        if in_direction and(nearest is None or radius<nearest['distance_m']):
            nearest=dict(distance_m=radius,bearing_degrees=math.degrees(bearing),base_xy=[x,y],map_xy=mapped)
    if valid/len(message.ranges)<.75:raise ValueError('Insufficient valid laser rays')
    return dict(source='/scan',stamp_seconds=stamp_seconds(message.header.stamp),frame_id='map',
                points=points[::max(1,math.ceil(len(points)/90))],nearest=nearest,
                sector='周围'if rotating else'前方'if direction>0 else'后方')


class ObstacleObservation:
    """Read-only, expiring UI/log evidence. Near range is not a safety verdict."""
    def __init__(self,now=time.monotonic):
        self.now=now;self.scan=None;self.received=None;self.velocity=None;self.command=None
        self.events=[];self.last_event=-math.inf;self.last_state=None

    def motion(self,v,w,*,command=False):
        if all(math.isfinite(value)for value in(v,w)):
            setattr(self,'command'if command else'velocity',(v,w,self.now()))

    def direction(self):
        now=self.now();motion=self.command if self.command and now-self.command[2]<=.35 else self.velocity
        if motion is None or now-motion[2]>.4:return 1,False
        return (-1 if motion[0]<-.015 else 1),abs(motion[0])<.015 and abs(motion[1])>.04

    def receive(self,value):
        self.scan=value;self.received=self.now()

    def snapshot(self,sim):
        now=self.now();fresh=bool(self.scan is not None and self.received is not None and now-self.received<=.4
            and sim is not None and -.1<=sim-self.scan['stamp_seconds']<=.4)
        motion_fresh=bool(self.velocity and now-self.velocity[2]<=.4)
        velocity=self.velocity[:2]if motion_fresh else None
        nearest=self.scan.get('nearest')if fresh else None
        near=bool(nearest and nearest['distance_m']<=.7)
        moving=bool(velocity and(abs(velocity[0])>.015 or abs(velocity[1])>.04))
        state='stale'if not fresh or not motion_fresh else'near_moving'if near and moving else'near_stopped'if near else'moving'if moving else'stationary'
        value=dict(self.scan or{},fresh=fresh,motion_fresh=motion_fresh,state=state,velocity=velocity,
                   near_threshold_m=.7,age_seconds=None if self.received is None else now-self.received,
                   limitation='激光观测，距离从机器人中心计算；运动状态不代表避障已成功，低矮/悬空障碍还依赖深度与导航。')
        if not fresh:value.update(points=[],nearest=None)
        return value

    def event(self,sim):
        value=self.snapshot(sim);state=value['state'];now=self.now()
        # No startup/idle spam; recovery is only a change in observed proximity.
        if state==self.last_state or now-self.last_event<2.5:return None
        previous=self.last_state;self.last_state=state
        if not state.startswith('near_')and not(previous and previous.startswith('near_')):return None
        self.last_event=now;nearest=value.get('nearest')or{}
        event=dict(stamp_seconds=sim,state=state,sector=value.get('sector'),**nearest)
        self.events.append(event);self.events=self.events[-30:];return event


class TelemetryStore:
    """Thread-safe data model also exercised without starting ROS or Gazebo."""
    def __init__(self, now=time.monotonic, freshness_seconds=3.0):
        self.now = now
        self.freshness_seconds = freshness_seconds
        self.lock = threading.RLock()
        self.started_wall = now()
        self.running = False
        self.error = None
        self.topics = {name: dict(messages=0, received=None, stamp=None) for name in TOPICS}
        self.clock_seconds = None
        self.clock_advanced_wall = None
        self.pose = None
        self.pose_received = None
        self.map = None
        self.map_received = None
        self.lifecycle = {}
        self.graph_wall = None
        self.graph_polls = 0
        self.nodes = []
        self.foreign_publishers = {}
        self.control_publishers = {}
        self.command_subscribers = 0
        self.search_progress = None
        self.mapping_motion = None
        self.mapping_received = None
        self.safety = None
        self.safety_received = None
        self.obstacle=ObstacleObservation(now)
        self.navigation_path=None
        self.path_received=None
        self.costmap=None
        self.costmap_received=None
        self.costmap_error=None

    def receive_safety(self, message):
        try:
            value = json.loads(message)
        except ValueError:
            return
        if (isinstance(value,dict) and type(value.get('ready')) is bool
            and isinstance(value.get('stamp_seconds'),(int,float)) and math.isfinite(value['stamp_seconds'])):
            with self.lock:
                self.safety,self.safety_received = value,self.now()

    def receive_mapping_motion(self, message):
        try:
            value = json.loads(message)
        except ValueError:
            return
        if isinstance(value,dict) and isinstance(value.get('status'),str):
            with self.lock:
                self.mapping_motion = value
                self.mapping_received = self.now()

    def clear_localization(self):
        with self.lock:
            self.map = self.map_received = self.pose = self.pose_received = None
            self.mapping_motion = self.mapping_received = None
            self.lifecycle.clear()
            self.obstacle=ObstacleObservation(self.now)
            self.navigation_path=self.path_received=None
            self.costmap=self.costmap_received=None

    def receive_search_progress(self, message):
        try:
            event = json.loads(message)
        except ValueError:
            return
        if (isinstance(event, dict) and event.get('version') == 1
                and isinstance(event.get('request_id'), str)
                and isinstance(event.get('task_id'), str)
                and event.get('stage') in ('navigating', 'observing', 'waiting_for_data',
                                           'canceling', 'saving', 'finished')):
            with self.lock:
                self.search_progress = event

    def receive(self, topic, stamp):
        now = self.now()
        if not math.isfinite(stamp):
            return
        with self.lock:
            entry = self.topics[topic]
            entry.update(messages=entry['messages']+1, received=now, stamp=stamp)
            if topic == '/clock':
                if self.clock_seconds is not None and stamp > self.clock_seconds:
                    self.clock_advanced_wall = now
                elif self.clock_seconds is not None and stamp < self.clock_seconds:
                    self.clock_advanced_wall = None
                self.clock_seconds = stamp

    def receive_pose(self, pose):
        with self.lock:
            self.pose = pose
            self.pose_received = self.now()

    def receive_map(self, payload):
        with self.lock:
            self.map = payload
            self.map_received = self.now()

    def receive_lifecycle(self, name, state_id, label):
        with self.lock:
            self.lifecycle[name] = dict(id=int(state_id), label=label, received=self.now())

    def receive_graph(self, nodes, publishers, subscribers, control_publishers=None):
        with self.lock:
            self.nodes = sorted(nodes)
            self.foreign_publishers = publishers
            self.control_publishers = control_publishers or {}
            self.command_subscribers = subscribers
            self.graph_wall = self.now()
            self.graph_polls += 1

    def _age(self, when, now):
        return None if when is None else max(0.0, now-when)

    def snapshot(self):
        with self.lock:
            now = self.now()
            topics = {}
            for name, row in self.topics.items():
                age = self._age(row['received'], now)
                stamp_age = (None if self.clock_seconds is None or row['stamp'] is None
                             else self.clock_seconds-row['stamp'])
                topics[name] = dict(age_seconds=age, messages=row['messages'],
                                    stamp_seconds=row['stamp'], stamp_age_seconds=stamp_age,
                                    fresh=(age is not None and age <= self.freshness_seconds
                                           and (name == '/clock' or stamp_age is not None
                                                and -.5 <= stamp_age <= self.freshness_seconds)))
            clock_age = self._age(self.clock_advanced_wall, now)
            clock_advancing = clock_age is not None and clock_age <= self.freshness_seconds
            graph_age = self._age(self.graph_wall, now)
            graph_fresh = graph_age is not None and graph_age <= self.freshness_seconds
            simulation_ready = (self.running and clock_advancing
                                and all(topics[name]['fresh'] for name in SIMULATION_TOPICS))
            pose = deepcopy(self.pose)
            pose_age = self._age(self.pose_received, now)
            pose_stamp_age = (None if pose is None or self.clock_seconds is None
                              else self.clock_seconds-pose['stamp_seconds'])
            pose_fresh = (pose is not None and pose_age is not None and pose_age <= 1.5
                          and pose['frame_id'] == 'map' and pose_stamp_age is not None
                          and -1.5 <= pose_stamp_age <= self.freshness_seconds)
            lifecycle = {}
            for name in ('amcl', 'bt_navigator'):
                row = self.lifecycle.get(name)
                age = self._age(row['received'], now) if row else None
                lifecycle[name] = dict(id=row['id'] if row else None,
                                       label=row['label'] if row else 'unavailable',
                                       age_seconds=age,
                                       active=bool(row and row['id'] == 3 and age <= 5))
            navigation_ready = (simulation_ready and pose_fresh
                                and all(row['active'] for row in lifecycle.values()))
            map_owners = self.control_publishers.get('/map', [])
            velocity_owners = self.control_publishers.get('/cmd_vel', [])
            # Several behaviors expose their own velocity endpoints under a
            # single Nav2 node. Check their owners, not the endpoint total.
            navigation_control_ready = (graph_fresh and map_owners == ['/map_server']
                                        and set(velocity_owners) == {
                                            '/behavior_server', '/velocity_smoother'})
            mapping_ready = (simulation_ready and pose_fresh and graph_fresh
                             and self.map is not None and map_owners == ['/slam_toolbox']
                             and velocity_owners == ['/mapping_motion']
                             and '/slam_toolbox' in self.nodes and '/amcl' not in self.nodes
                             and self.mapping_received is not None and now-self.mapping_received<=1.5)
            perception_ready = (simulation_ready and graph_fresh and self.command_subscribers > 0
                                and all(topics[name]['fresh'] for name in PERCEPTION_TOPICS))
            foreign_nodes = [name for name in self.nodes if name.rsplit('/', 1)[-1] in STACK_NODES]
            foreign = bool(foreign_nodes or any(self.foreign_publishers.values())
                           or self.command_subscribers)
            safety = deepcopy(self.safety) if self.safety is not None else dict(ready=False)
            safety['fresh'] = (self.safety_received is not None and now-self.safety_received<=.75
                and self.clock_seconds is not None and -.1<=self.clock_seconds-safety['stamp_seconds']<=.75)
            safety['ready'] = safety['ready'] and safety['fresh']
            obstacle=self.obstacle.snapshot(self.clock_seconds)
            obstacle['events']=deepcopy(self.obstacle.events)
            path=deepcopy(self.navigation_path)
            if path is not None:
                path['fresh']=bool(self.path_received is not None and now-self.path_received<=2.5 and self.clock_seconds is not None
                    and -.1<=self.clock_seconds-path['stamp_seconds']<=2.5)
                if not path['fresh']:path['points']=[]
            return dict(connected=bool(self.running and graph_fresh
                                       and any(row['fresh'] for row in topics.values())),
                        monitor_running=self.running, error=self.error,
                        discovery_ready=bool(graph_fresh and self.graph_polls >= 2
                                             and now-self.started_wall >= 2),
                        simulation_ready=simulation_ready, navigation_ready=navigation_ready,
                        safety=safety,
                        obstacle=obstacle,navigation_path=path,
                        navigation_control_ready=navigation_control_ready,
                        control_publishers=deepcopy(self.control_publishers),
                        mapping_ready=mapping_ready,mapping_motion=deepcopy(self.mapping_motion),
                        perception_ready=perception_ready, clock_advancing=clock_advancing,
                        clock_seconds=self.clock_seconds, topics=topics,
                        pose=pose if pose_fresh else None, pose_fresh=pose_fresh,
                        pose_age_seconds=pose_age, pose_stamp_age_seconds=pose_stamp_age,
                        lifecycle=lifecycle, command_subscribers=self.command_subscribers,
                        discovered_nodes=list(self.nodes), foreign_stack=foreign,
                        foreign_nodes=foreign_nodes,
                        foreign_publishers=dict(self.foreign_publishers),
                        search_progress=deepcopy(self.search_progress))

    def map_snapshot(self):
        with self.lock:
            if self.map is None:
                return dict(available=False, age_seconds=None)
            result = deepcopy(self.map)
            result['age_seconds'] = self._age(self.map_received, self.now())
            # A static map is intentionally latched; its age alone is not failure.
            result['source'] = '/map'
            return result

    def receive_costmap(self,payload):
        with self.lock:
            self.costmap=payload;self.costmap_received=self.now();self.costmap_error=None

    def costmap_snapshot(self):
        with self.lock:
            if self.costmap is None:return dict(available=False,fresh=False,error=self.costmap_error)
            value=deepcopy(self.costmap);age=self.now()-self.costmap_received
            value.update(source='/global_costmap/costmap',age_seconds=age,
                fresh=bool(age<=2.5 and self.clock_seconds is not None and -.1<=self.clock_seconds-value['stamp_seconds']<=2.5))
            if not value['fresh']:value['data']=[]
            return value


class Monitor:
    def __init__(self):
        self.store = TelemetryStore()
        self._stop = threading.Event()
        self._thread = None
        self._thread_lock = threading.Lock()
        self._keyboard_lock = threading.Lock()
        self._keyboard_pending = None
        self._camera_lock = threading.Lock()
        self._camera_requests = {}
        self._camera_messages = {}
        self._camera_jpegs = {}

    def _receive_camera(self, view, message):
        now = time.monotonic()
        with self._camera_lock:
            previous = self._camera_messages.get(view)
            if (now - self._camera_requests.get(view, -math.inf) <= 2.
                    and (previous is None or now - previous[0] >= .23)):
                self._camera_messages[view] = (now, message)

    def camera_frame(self, view):
        from PIL import Image

        now = time.monotonic()
        with self._camera_lock:
            self._camera_requests[view] = now
            sample = self._camera_messages.get(view)
            if sample is None or now - sample[0] > 2.:
                return None
            receipt, message = sample
            cached = self._camera_jpegs.get(view)
            if cached is not None and cached[0] == receipt:
                return cached[1]
            formats = {'rgb8': ('RGB', 3), 'bgr8': ('BGR', 3),
                       'rgba8': ('RGBA', 4), 'bgra8': ('BGRA', 4)}
            pixel_format = formats.get(message.encoding.lower())
            if pixel_format is None or not (0 < message.width <= 2048 and 0 < message.height <= 2048):
                return None
            encoding, channels = pixel_format
            if message.step < channels * message.width or len(message.data) != message.step * message.height:
                return None
            mode = 'RGBA' if channels == 4 else 'RGB'
            frame = Image.frombytes(mode, (message.width, message.height),
                                    bytes(message.data), 'raw', encoding, message.step, 1)
            frame.thumbnail((960, 600))
            output = BytesIO()
            frame.convert('RGB').save(output, format='JPEG', quality=76)
            result = output.getvalue()
            self._camera_jpegs[view] = (receipt, result)
            return result


    def start(self):
        with self._thread_lock:
            if self._thread is not None:
                raise RuntimeError('Monitor has already started')
            self.store.started_wall = time.monotonic()
            self._thread = threading.Thread(target=self._run, name='robot-telemetry', daemon=True)
            self._thread.start()
        return self

    def snapshot(self):
        return self.store.snapshot()

    def map_snapshot(self):
        return self.store.map_snapshot()

    def costmap_snapshot(self):
        return self.store.costmap_snapshot()

    def clear_localization(self):
        self.store.clear_localization()

    def foreign_stack_present(self):
        return self.snapshot()['foreign_stack']

    def send_keyboard(self,linear,angular):
        with self._keyboard_lock:
            self._keyboard_pending=(time.monotonic(),linear,angular)

    def close(self):
        self._stop.set()
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join(timeout=5)
            if self._thread.is_alive():
                raise RuntimeError('ROS telemetry thread did not stop')

    def _run(self):
        context = node = executor = None
        try:
            import rclpy
            from geometry_msgs.msg import Twist
            from lifecycle_msgs.srv import GetState
            from nav_msgs.msg import OccupancyGrid, Odometry
            from nav_msgs.msg import Path
            from geometry_msgs.msg import Twist
            from rclpy.context import Context
            from rclpy.executors import SingleThreadedExecutor
            from rclpy.node import Node
            from rclpy.parameter import Parameter
            from rclpy.qos import DurabilityPolicy, QoSProfile
            from rclpy.signals import SignalHandlerOptions
            from rclpy.time import Time
            from rosgraph_msgs.msg import Clock
            from sensor_msgs.msg import CameraInfo, Image, LaserScan, PointCloud2
            from std_msgs.msg import String
            from semantic_search.sensor_qos import sensor_qos_profile
            from tf2_ros import Buffer, TransformException, TransformListener
            from yolo_msgs.msg import DetectionArray

            context = Context()
            rclpy.init(context=context, signal_handler_options=SignalHandlerOptions.NO)
            node = Node('robot_console_monitor_'+str(os.getpid()), context=context,
                        parameter_overrides=[Parameter('use_sim_time', value=True)])
            executor = SingleThreadedExecutor(context=context)
            executor.add_node(node)
            keyboard=node.create_publisher(Twist,'/mapping/keyboard',1)
            buffer = Buffer()
            listener = TransformListener(buffer, node)
            reliable = sensor_qos_profile('reliable')
            best_effort = sensor_qos_profile('best_effort')
            subscriptions = []
            last_scan=[-math.inf]
            def observe_scan(message):
                now=time.monotonic()
                if now-last_scan[0]<.2:return
                last_scan[0]=now
                try:
                    stamp=Time.from_msg(message.header.stamp)
                    base=buffer.lookup_transform('base_link',message.header.frame_id,stamp).transform
                    try:mapped=buffer.lookup_transform('map',message.header.frame_id,stamp).transform
                    except TransformException:mapped=None
                    with self.store.lock:
                        direction,rotating=self.store.obstacle.direction()
                        self.store.obstacle.receive(scan_obstacles(message,base,direction,rotating,mapped))
                        event=self.store.obstacle.event(self.store.clock_seconds)
                    if event:
                        labels={'near_moving':'检测到近障，机器人正在移动','near_stopped':'检测到近障，机器人已停稳',
                                'moving':'近障提示解除，机器人正在移动','stationary':'近障提示解除，机器人已停稳','stale':'观测数据过期'}
                        details=(f"，中心距离{event['distance_m']:.2f}m，方位{event['bearing_degrees']:.0f}°"if'distance_m'in event else'')
                        print('[避障观察] '+labels[event['state']]+details+'（激光观测）',flush=True)
                except (TransformException,ValueError):pass
            for topic, kind in [('/clock', Clock), ('/odom', Odometry), ('/scan', LaserScan),
                                ('/rgbd/obstacles', PointCloud2), ('/rgbd/image', Image),
                                ('/rgbd/depth_image', Image), ('/rgbd/camera_info', CameraInfo),
                                ('/yolo/detections', DetectionArray)]:
                def receive(message, name=topic):
                    stamp = message.clock if name == '/clock' else message.header.stamp
                    self.store.receive(name, stamp_seconds(stamp))
                    if name == '/rgbd/image': self._receive_camera('robot', message)
                    elif name=='/scan':observe_scan(message)
                    elif name=='/odom':
                        with self.store.lock:self.store.obstacle.motion(message.twist.twist.linear.x,message.twist.twist.angular.z)
                # The adapter publishes obstacles BEST_EFFORT; all image bridge
                # outputs and detector results in this candidate are RELIABLE.
                qos = best_effort if topic == '/rgbd/obstacles' else reliable
                subscriptions.append(node.create_subscription(kind, topic, receive, qos))
            subscriptions.append(node.create_subscription(
                Image, '/gazebo/overview', lambda message: self._receive_camera('overview', message),
                best_effort))
            def receive_command(message):
                with self.store.lock:self.store.obstacle.motion(message.linear.x,message.angular.z,command=True)
            subscriptions.append(node.create_subscription(Twist,'/cmd_vel',receive_command,best_effort))
            def receive_path(message):
                if message.header.frame_id!='map':return
                points=[[p.pose.position.x,p.pose.position.y]for p in message.poses]
                if not all(math.isfinite(v)for p in points for v in p):return
                with self.store.lock:
                    self.store.navigation_path=dict(frame_id='map',stamp_seconds=stamp_seconds(message.header.stamp),
                        points=points[::max(1,math.ceil(len(points)/300))],source='/plan')
                    self.store.path_received=time.monotonic()
            subscriptions.append(node.create_subscription(Path,'/plan',receive_path,reliable))

            def receive_map(message):
                try:
                    self.store.receive_map(map_payload(message))
                except ValueError as error:
                    with self.store.lock:
                        self.store.error = 'map: '+str(error)
            subscriptions.append(node.create_subscription(
                OccupancyGrid, '/map', receive_map,
                QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)))
            def receive_costmap(message):
                try:
                    if message.header.frame_id!='map':raise ValueError('Global costmap is not in map frame')
                    self.store.receive_costmap(map_payload(message))
                except ValueError as error:
                    with self.store.lock:
                        self.store.costmap=None;self.store.costmap_error=str(error)
            subscriptions.append(node.create_subscription(OccupancyGrid,'/global_costmap/costmap',receive_costmap,
                QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL)))
            subscriptions.append(node.create_subscription(String, '/search/progress',
                lambda msg: self.store.receive_search_progress(msg.data), 10))
            subscriptions.append(node.create_subscription(String, '/mapping/state',
                lambda msg: self.store.receive_mapping_motion(msg.data), 10))
            subscriptions.append(node.create_subscription(String, '/safety/state',
                lambda msg: self.store.receive_safety(msg.data), 10))
            services = {name: node.create_client(GetState, '/'+name+'/get_state')
                        for name in ('amcl', 'bt_navigator')}
            pending = {}
            last_graph = last_pose = last_services = -math.inf
            with self.store.lock:
                self.store.running = True
            while not self._stop.is_set() and context.ok():
                executor.spin_once(timeout_sec=.05)
                now = time.monotonic()
                with self._keyboard_lock:
                    pending_keys,self._keyboard_pending=self._keyboard_pending,None
                if pending_keys is not None:
                    at,linear,angular=pending_keys
                    msg=Twist()
                    if now-at<.35:
                        msg.linear.x,msg.angular.z=linear,angular
                    keyboard.publish(msg)
                if now-last_graph >= .5:
                    names = [('/'+namespace.strip('/')+'/'+name).replace('//', '/')
                             for name, namespace in node.get_node_names_and_namespaces()
                             if name != node.get_name() and not name.startswith('transform_listener_impl_')]
                    publishers = {topic: node.count_publishers(topic)
                                  for topic in ('/clock', '/odom', '/scan', '/rgbd/image',
                                                '/yolo/detections', '/search/result')}
                    controls = {topic: [info.node_namespace.rstrip('/')+'/'+info.node_name
                                        for info in node.get_publishers_info_by_topic(topic)]
                                for topic in ('/map','/cmd_vel')}
                    publishers.update({topic: len(owners) for topic, owners in controls.items()})
                    self.store.receive_graph(names, publishers, node.count_subscribers('/search/command'),
                                             controls)
                    last_graph = now
                if now-last_pose >= .2:
                    try:
                        self.store.receive_pose(transform_pose(
                            buffer.lookup_transform('map', 'base_link', Time())))
                    except (TransformException, ValueError):
                        pass  # Existing pose expires; stale pose never satisfies readiness.
                    last_pose = now
                for name, (future, sent) in list(pending.items()):
                    if future.done():
                        try:
                            response = future.result().current_state
                            self.store.receive_lifecycle(name, response.id, response.label)
                        except Exception:
                            pass  # State expires if a response fails or a service disappears.
                        del pending[name]
                    elif now-sent >= 2:
                        future.cancel()
                        del pending[name]
                if now-last_services >= 1:
                    for name, client in services.items():
                        if name not in pending and client.service_is_ready():
                            pending[name] = (client.call_async(GetState.Request()), now)
                    last_services = now
        except Exception as error:
            with self.store.lock:
                self.store.error = f'{type(error).__name__}: {error}'
        finally:
            with self.store.lock:
                self.store.running = False
            if executor is not None:
                executor.shutdown(timeout_sec=1)
            if node is not None:
                node.destroy_node()
            if context is not None and context.ok():
                context.try_shutdown()
