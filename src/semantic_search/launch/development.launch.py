"""Separate candidate layout/rig. Build a fresh map before navigation use."""
import json
import runpy
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction, RegisterEventHandler
from launch.event_handlers import OnShutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from semantic_search.development import build_world, rig_frames


def add_overview_camera(world):
    model = ET.SubElement(world, 'model', name='console_overview')
    ET.SubElement(model, 'static').text = 'true'
    ET.SubElement(model, 'pose').text = '0 -0.4 17.2 0 1.52 1.5708'
    link = ET.SubElement(model, 'link', name='mount')
    sensor = ET.SubElement(link, 'sensor', name='overview', type='camera')
    ET.SubElement(sensor, 'topic').text = '/gazebo/overview'
    ET.SubElement(sensor, 'always_on').text = 'true'
    ET.SubElement(sensor, 'update_rate').text = '4'
    camera = ET.SubElement(sensor, 'camera')
    ET.SubElement(camera, 'horizontal_fov').text = '1.15'
    image = ET.SubElement(camera, 'image')
    ET.SubElement(image, 'width').text = '800'
    ET.SubElement(image, 'height').text = '480'
    ET.SubElement(image, 'format').text = 'R8G8B8'
    clip = ET.SubElement(camera, 'clip')
    ET.SubElement(clip, 'near').text = '0.1'
    ET.SubElement(clip, 'far').text = '60'

def setup(context):
    root = Path(LaunchConfiguration('project_root').perform(context)).resolve()
    depth_source=LaunchConfiguration('depth_cloud_source').perform(context)
    if depth_source not in ('native','image'):raise ValueError('Unsupported depth cloud source')
    share = Path(get_package_share_directory('semantic_search'))
    original = runpy.run_path(str(share/'launch/fortress.launch.py'))
    cache = tempfile.TemporaryDirectory(prefix='semantic_r0_')
    output = Path(cache.name)/'aws_house_r0_v1.sdf'
    height = float(LaunchConfiguration('camera_height').perform(context))
    pitch = float(LaunchConfiguration('camera_pitch').perform(context))
    width = int(LaunchConfiguration('image_width').perform(context))
    image_height = int(LaunchConfiguration('image_height').perform(context))
    hfov = float(LaunchConfiguration('camera_hfov').perform(context))
    layout_file = LaunchConfiguration('layout_file').perform(context)
    charging_file = LaunchConfiguration('charging_file').perform(context)
    truth = build_world(root, output, original['make_aws_world'], height, pitch, layout_file,
                        width,image_height,hfov,charging_file or None)
    truth['camera_rig'] = dict(height_m=height,pitch_rad=pitch,image_width=width,
                               image_height=image_height,horizontal_fov_rad=hfov)
    room_doors=LaunchConfiguration('room_doors').perform(context)=='true'
    overview = LaunchConfiguration('gazebo_preview').perform(context) == 'true'
    if room_doors or overview:
        document = ET.parse(output)
        world = document.getroot().find('world')
        if room_doors:
            from semantic_search.room_doors import DOORS, add_room_doors
            add_room_doors(world)
        if overview:
            add_overview_camera(world)
        document.write(output, encoding='utf-8', xml_declaration=True)
    # Calibration only: the sensor's own far clip, never scene object truth.
    far_clip=ET.parse(output).find(".//model[@name='waffle']/link[@name='camera_rgb_frame']/sensor/camera/clip/far")
    if far_clip is None:raise ValueError('Verified RGB-D far clip unavailable')
    clearing_max_depth=float(far_clip.text)
    evidence = root/LaunchConfiguration('evidence_dir').perform(context)
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence/'scene_truth.json').write_text(json.dumps(truth, indent=2)+'\n')
    description = ET.parse(share/'config/tb3_frames.urdf').getroot()
    rig_frames(description,height,pitch)
    bridge = [
        '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
        '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
        '/odom/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
        '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
        '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
        '/rgbd/image@sensor_msgs/msg/Image[ignition.msgs.Image',
        '/rgbd/depth_image@sensor_msgs/msg/Image[ignition.msgs.Image',
        '/rgbd/camera_info@sensor_msgs/msg/CameraInfo[ignition.msgs.CameraInfo',
        '/rgbd/points@sensor_msgs/msg/PointCloud2[ignition.msgs.PointCloudPacked',
        '/robot/contacts@ros_gz_interfaces/msg/Contacts[ignition.msgs.Contacts']
    velocity_topic = LaunchConfiguration('velocity_topic').perform(context)
    if velocity_topic not in ('/cmd_vel','/cmd_vel_safe'):
        raise ValueError('Unsupported simulator velocity topic')
    cloud_arguments=bridge[8:9]
    cloud_parameters={'qos_overrides./rgbd/points_raw.publisher.depth':1}
    if depth_source=='image':
        # In ros_gz_bridge0.244.26 the CLI lazy parameter is not assigned to
        # BridgeConfig. YAML does set it. Keep the native stream only for the
        # adapter's three independent startup calibration pairs.
        cloud_configuration=evidence/'cloud_bridge.yaml'
        cloud_configuration.write_text(json.dumps([dict(ros_topic_name='/rgbd/points_raw',
            gz_topic_name='/rgbd/points',ros_type_name='sensor_msgs/msg/PointCloud2',
            gz_type_name='ignition.msgs.PointCloudPacked',direction='GZ_TO_ROS',
            publisher_queue=1,subscriber_queue=1,lazy=True)],indent=2)+'\n')
        cloud_arguments=[]
        cloud_parameters['config_file']=str(cloud_configuration)
    # A stalled reliable bulk subscriber must not block clock/odometry or
    # the final zero-velocity command in the control bridge.
    bridges = [
        Node(package='ros_gz_bridge',executable='parameter_bridge',name='ros_gz_bridge',
             arguments=bridge[:5],remappings=[('/odom/tf','/tf'),('/cmd_vel',velocity_topic)],output='screen'),
        Node(package='ros_gz_bridge',executable='parameter_bridge',name='rgbd_bridge',
             arguments=bridge[5:8],parameters=[{
                 'qos_overrides./rgbd/image.publisher.depth':1,
                 'qos_overrides./rgbd/depth_image.publisher.depth':1,
                 'qos_overrides./rgbd/camera_info.publisher.depth':1}],output='screen'),
        Node(package='ros_gz_bridge',executable='parameter_bridge',name='cloud_bridge',
             arguments=cloud_arguments,remappings=[('/rgbd/points','/rgbd/points_raw')],
             parameters=[cloud_parameters],output='screen'),
        Node(package='ros_gz_bridge',executable='parameter_bridge',name='contact_bridge',
             arguments=bridge[9:],output='screen')]
    if room_doors:
        door_bridge=[]
        for name in DOORS:
            door_bridge += [f'/doors/{name}/command@std_msgs/msg/Float64]ignition.msgs.Double',
                            f'/doors/{name}/joint_state@sensor_msgs/msg/JointState[ignition.msgs.Model']
        bridges.append(Node(package='ros_gz_bridge',executable='parameter_bridge',
                            name='door_bridge',arguments=door_bridge,output='screen'))
    if overview:
        bridges.append(Node(package='ros_gz_bridge', executable='parameter_bridge',
            name='console_camera_bridge',
            arguments=['/gazebo/overview@sensor_msgs/msg/Image[ignition.msgs.Image'],
            parameters=[{'qos_overrides./gazebo/overview.publisher.depth': 1}],
            output='screen'))
    command = ['ign', 'gazebo', '-r', '-v', '3']
    if LaunchConfiguration('gui').perform(context).lower() != 'true':
        command.append('-s')
    command.append(str(output))
    return [RegisterEventHandler(OnShutdown(on_shutdown=[OpaqueFunction(function=lambda _: cache.cleanup())])),
            ExecuteProcess(cmd=command, output='screen'),
            Node(package='robot_state_publisher', executable='robot_state_publisher',
                 parameters=[{'use_sim_time': True, 'robot_description': ET.tostring(description, encoding='unicode')}]),
            *bridges,
            Node(package='semantic_search',executable='cloud_adapter',
                 parameters=[{'use_sim_time':True,
                     'input_reliability':'reliable',
                     'input_source':'depth_image'if depth_source=='image'else'native_cloud',
                     'min_period':.1,
                     'sampling_stride':width//160,
                     'clearing_max_depth':clearing_max_depth,
                     'compact_xyz':True}],output='screen')]


def generate_launch_description():
    return LaunchDescription([DeclareLaunchArgument('project_root'),
                              DeclareLaunchArgument('charging_file',default_value=''),
                              DeclareLaunchArgument('room_doors',default_value='false'),
                              DeclareLaunchArgument('gazebo_preview',default_value='false'),
                              DeclareLaunchArgument('depth_cloud_source',default_value='native'),
                              DeclareLaunchArgument('gui', default_value='false'),
                              DeclareLaunchArgument('camera_height', default_value='1.0'),
                              DeclareLaunchArgument('camera_pitch', default_value='0.25'),
                              DeclareLaunchArgument('image_width',default_value='640'),
                              DeclareLaunchArgument('image_height',default_value='480'),
                              DeclareLaunchArgument('camera_hfov',default_value='1.02974'),
                              DeclareLaunchArgument('velocity_topic',default_value='/cmd_vel'),
                              DeclareLaunchArgument('layout_file', default_value='scenes/aws_house/layout_r0_v1.json'),
                              DeclareLaunchArgument('evidence_dir', default_value='results/development/r0_v1'),
                              OpaqueFunction(function=setup)])
