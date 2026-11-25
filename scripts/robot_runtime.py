#!/usr/bin/env python3
"""Own and supervise one local robot session; ROS readiness is checked elsewhere.

The supervisor never sends a system-wide kill or trusts a stale PID. Descendants
inherit a unique ownership marker, including Nav2's separate setsid session, and
are signalled through pidfds after UID, marker and process-start verification.
"""
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import threading
import time
from uuid import uuid4


COMPONENTS = ('simulation', 'navigation', 'detector', 'search', 'rviz', 'slam', 'motion', 'safety')
OWNER_VARIABLE = 'SEMANTIC_RUNTIME_OWNER'
ROLE_VARIABLE = 'SEMANTIC_RUNTIME_ROLE'


def _save(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def _identity(pid, marker, role=None):
    """Return a matching live process identity, without exposing its environment."""
    path = Path('/proc') / str(pid)
    try:
        if path.stat().st_uid != os.getuid():
            return None
        environment = (path / 'environ').read_bytes().split(b'\0')
        if marker not in environment or role is not None and role not in environment:
            return None
        # Everything after the final ')' begins at /proc stat field 3.
        fields = (path / 'stat').read_text().rpartition(')')[2].split()
        if fields[0] == 'Z':
            return None
        return dict(pid=int(pid), start_ticks=int(fields[19]), state=fields[0])
    except (OSError, ValueError, IndexError):
        return None


def _owned(marker, role=None):
    rows = []
    for path in Path('/proc').iterdir():
        if path.name.isdigit():
            row = _identity(int(path.name), marker, role)
            if row is not None:
                rows.append(row)
    return rows


def _signal(identity, marker, sig, role=None):
    """Pin the process first, then verify its identity before sending a signal."""
    try:
        descriptor = os.pidfd_open(identity['pid'])
    except (ProcessLookupError, PermissionError):
        return False
    try:
        current = _identity(identity['pid'], marker, role)
        if current is None or current['start_ticks'] != identity['start_ticks']:
            return False
        signal.pidfd_send_signal(descriptor, sig)
        return True
    except (ProcessLookupError, PermissionError):
        return False
    finally:
        os.close(descriptor)


class Runtime:
    """Pure-Python lifecycle owner used by robot_console.py.

    ``check_dependencies=False`` is for isolated subprocess tests. It does not
    bypass locks or ownership checks. It must not be exposed as a UI control.
    """

    def __init__(self, root, domain=66, headless=False, session_dir=None, env=None,
                 check_dependencies=True, rooms_file=None, layout_file=None, device='cuda:0',
                 candidate_categories=None, camera_height=1.0, camera_pitch=.25,
                 active_observation=False, image_size=640, navigation_safety=False,model='yolov8n-seg.pt',
                 camera_resolution='640x480',camera_fov=1.02974,cleaning_position_goals=False,
                 cleaning_local_recovery=False, charging_station=True, cleaning_budget_selection=False,
                 memory_guidance=False,ball_model=None,auxiliary_model=None,auxiliary_categories=None,
                 body_footprint=False,depth_cloud_source='native',precision_docking=False,memory_safe_approach=False,room_doors=False,astar=False,gazebo_preview=False):
        if depth_cloud_source not in ('native','image'):
            raise ValueError('导航点云来源必须为native或image。')
        if (camera_resolution not in ('640x480','1280x960') or type(camera_fov) not in (int,float)
                or not math.isfinite(camera_fov) or not .8<=camera_fov<=1.6):
            raise ValueError('相机分辨率支持640x480/1280x960，水平视场0.8–1.6 rad。')
        if model not in ('yolov8n-seg.pt','yolov8s-seg.pt'):
            raise ValueError('视觉模型必须为锁定的n或s分割权重。')
        self.model = model
        if ball_model not in (None,'yoloe-11s-seg-pf.pt'):
            raise ValueError('球辅助模型必须使用锁定的YOLOE免提示分割权重。')
        self.ball_model=ball_model
        if auxiliary_model not in (None,'yoloe-11s-seg.pt') or (auxiliary_model and ball_model):
            raise ValueError('辅助模型需显式选择锁定的文本YOLOE，且不能同时选择旧球辅助。')
        if auxiliary_categories is not None and not auxiliary_model:
            raise ValueError('辅助类别需要同时指定辅助模型。')
        scope=(['book','sports ball'] if auxiliary_categories is None else auxiliary_categories) if auxiliary_model else ['sports ball']
        if not isinstance(scope,(list,tuple)) or not scope or any(c not in ('book','sports ball') for c in scope):
            raise ValueError('当前辅助候选仅支持书与球。')
        self.auxiliary_model=auxiliary_model or ball_model
        self.auxiliary_categories=list(dict.fromkeys(scope)) if self.auxiliary_model else []
        self.auxiliary_prompts='resources/ball_prompts_v1.npz' if auxiliary_model else None
        if body_footprint and navigation_safety:
            raise ValueError('真实轮廓与防碰撞候选尚未组合验证，请分别启用。')
        self.body_footprint = bool(body_footprint)
        self.navigation_safety = bool(navigation_safety)
        self.navigation_file = ('src/semantic_search/config/nav2_safety.yaml' if self.navigation_safety
                                else 'src/semantic_search/config/nav2_body_footprint.yaml' if self.body_footprint
                                else 'src/semantic_search/config/nav2_depth.yaml')
        if type(image_size) is not int or image_size not in (640,960,1280):
            raise ValueError('视觉输入尺寸必须为640、960或1280。')
        if (any(type(value) not in (int,float) or not math.isfinite(value)
                for value in (camera_height,camera_pitch))
                or not .3 <= camera_height <= 1.3 or not 0 <= camera_pitch <= .6):
            raise ValueError('相机高度范围为 0.3–1.3 m，俯仰范围为 0–0.6 rad。')
        from semantic_search.objects import admitted_aliases, validate_categories
        self.target_categories = validate_categories(list(admitted_aliases())+list(candidate_categories or []))
        if device not in ('cpu', 'cuda:0'):
            raise ValueError('device必须为cpu或cuda:0')
        self.device = device
        self.room_doors=room_doors
        self.gazebo_preview = gazebo_preview
        self.charging_station = None
        self.charging_station_file = None
        if type(domain) is not int or not 0 <= domain <= 232:
            raise ValueError('ROS domain must be an integer from 0 to 232')
        if not hasattr(os, 'pidfd_open') or not hasattr(signal, 'pidfd_send_signal'):
            raise RuntimeError('Linux pidfd support is required for safe process cleanup')
        self.root = Path(root).resolve()
        self.map_resource = None
        self.domain = domain
        self.headless = bool(headless)
        self.env = dict(os.environ if env is None else env)
        self.env.pop('SEMANTIC_CHARGING_CONFIG',None)
        self.token = uuid4().hex
        self.marker = (OWNER_VARIABLE + '=' + self.token).encode()
        self._locks = []
        self._processes = {}
        self._mutex = threading.RLock()
        self._closed = False
        self._receipt = None
        self.session_dir = None
        created_session = False
        try:
            self._acquire_lock(self.root / 'results' / '.robot-runtime.lock')
            self._acquire_lock(Path('/tmp') / f'semantic_robot_{os.getuid()}_domain_{domain}.lock')
            if not self.headless and not self.env.get('DISPLAY'):
                raise RuntimeError('没有可用 DISPLAY；在桌面终端运行，或使用 --headless 关闭 Gazebo/RViz 窗口')
            if check_dependencies:
                self._check_dependencies()
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
            self.session_dir = (Path(session_dir).resolve() if session_dir is not None
                                else self.root / 'results' / 'sessions' / (stamp + '_' + self.token[:8]))
            self.session_dir.mkdir(parents=True, exist_ok=False)
            created_session = True
            self.logs_dir = self.session_dir / 'logs'
            self.logs_dir.mkdir()
            self.task_output_dir = self.session_dir / 'tasks'
            self.task_output_dir.mkdir()
            self.env.update(SEMANTIC_ROS_DOMAIN_ID=str(domain), ROS_DOMAIN_ID=str(domain),
                            ROS_LOCALHOST_ONLY='1', SEMANTIC_USE_SYSTEM_DDS='0',
                            IGN_PARTITION='semantic_session_' + self.token,
                            PYTHONUNBUFFERED='1')
            self.env[OWNER_VARIABLE] = self.token
            self.env['SEMANTIC_DETECTOR_DEVICE'] = device
            # env.sh preserves these explicit selectors. Do not inherit a
            # workstation's remote discovery configuration into the console.
            for key in ('ROS_DISCOVERY_SERVER', 'FASTRTPS_DEFAULT_PROFILES_FILE',
                        'FASTDDS_DEFAULT_PROFILES_FILE'):
                self.env.pop(key, None)
            self.config = dict(domain=domain, ign_partition=self.env['IGN_PARTITION'],
                               target_categories=list(self.target_categories),
                               candidate_categories=[c for c in self.target_categories if c not in admitted_aliases()],
                               headless=self.headless, scene_id='aws_house_console_' + self.token[:8],
                               layout='scenes/aws_house/layout_service_surfaces_v2.json',
                               rooms='src/semantic_search/config/rooms_aws_house_v6.json',
                               navigation=self.navigation_file,
                               sensor_reliability='reliable', model=model,ball_model=ball_model,
                               depth_cloud_source=depth_cloud_source,
                               auxiliary_model=self.auxiliary_model,auxiliary_categories=self.auxiliary_categories,
                               auxiliary_prompts=self.auxiliary_prompts,
                               reject_clipped_detections=True,
                               validate_object_size=True,
                               camera_height=float(camera_height), camera_pitch=float(camera_pitch),
                               camera_resolution=camera_resolution,camera_horizontal_fov=float(camera_fov),
                               active_observation=bool(active_observation),
                               memory_guidance=bool(memory_guidance),
                               memory_safe_approach=bool(memory_safe_approach),
                               precision_docking=bool(precision_docking),
                               navigation_safety=bool(navigation_safety),body_footprint=self.body_footprint,
                               cleaning_position_goals=bool(cleaning_position_goals),
                               cleaning_local_recovery=bool(cleaning_local_recovery),
                               cleaning_budget_selection=bool(cleaning_budget_selection),
                               search=dict(min_hits=2,merge_radius=.30,min_score=.35),
                               detector=dict(device=device, python_env='.venv-gpu' if device=='cuda:0' else '.venv',
                                             image_size=image_size, confidence=.35, iou=.30, half=False,
                                             ball_model=ball_model,ball_max_rate_hz=2. if ball_model else None,
                                             auxiliary_model=self.auxiliary_model,
                                             auxiliary_categories=self.auxiliary_categories,
                                             auxiliary_max_rate_hz=2. if self.auxiliary_model else None))
            from semantic_search.map_resources import canonical_map_yaml, map_receipt
            self.config['map_id']='aws_house_v1'
            self.config['map']=str(canonical_map_yaml(self.root,map_id=self.config['map_id']).relative_to(self.root))
            if self.room_doors:
                from semantic_search.room_doors import create_door_map
                from semantic_search.map_resources import resolve_map
                door_map=self.session_dir/'door_map'/'house.yaml'
                create_door_map(self.root/self.config['map'],door_map)
                self.map_resource=resolve_map(self.root,yaml_path=door_map)
                self.config['map']=str(door_map.relative_to(self.root))
                self.config['map_id']='room_doors'
            self.config['global_planner'] = 'astar_with_dijkstra_fallback' if astar else 'baseline'
            if astar:
                import yaml
                params = yaml.safe_load((self.root / self.navigation_file).read_text())
                planner = params['planner_server']['ros__parameters']['GridBased']
                planner.update(plugin='service_navfn/CellCenteredNavfn', use_astar=True)
                effective = self.session_dir / 'configuration' / 'nav2_astar.yaml'
                effective.parent.mkdir(exist_ok=True)
                contents = yaml.safe_dump(params, sort_keys=False).encode()
                effective.write_bytes(contents)
                self.config['navigation_effective'] = str(effective.relative_to(self.session_dir))
                self.config['navigation_effective_sha256'] = hashlib.sha256(contents).hexdigest()
            self.config['room_doors']=self.room_doors
            if gazebo_preview:
                self.config['gazebo_preview'] = True
            self.config['map_resource']=map_receipt(self.map_resource,self.root) if self.map_resource else None
            station_name=('src/semantic_search/config/charging_station_precision.json' if precision_docking
                          else 'src/semantic_search/config/charging_station.json')
            if self.room_doors and charging_station:
                station=json.loads((self.root/station_name).read_text())
                station['map_yaml']=self.config['map']
                station['map_sha256']=dict(yaml=self.map_resource['yaml_sha256'],
                                          image=self.map_resource['image_sha256'])
                path=self.session_dir/'door_map'/'charging_station.json'
                _save(path,station)
                station_name=str(path.relative_to(self.root))
            if charging_station and (self.root/station_name).is_file():
                from semantic_search.docking import load_station
                self.charging_station=load_station(self.root/station_name,self.root,active_map=self.map_resource)
            self.config['charging_station']=station_name if self.charging_station else None
            self.config['charging_station_enabled']=self.charging_station is not None
            # Explicit startup-only selectors make historical and new fixtures
            # reproducible without changing the daily defaults or live state.
            for key, supplied in (('rooms', rooms_file), ('layout', layout_file)):
                if supplied is None:
                    continue
                path = (self.root / supplied).resolve()
                if not path.is_file() or not path.is_relative_to(self.root):
                    raise ValueError(f'{key}必须是项目内已存在的JSON文件')
                data = json.loads(path.read_text())
                if key == 'rooms':
                    from semantic_search.rooms import validate_rooms
                    validate_rooms(data)
                    if (any(room.get('cleaning_transit_clearance_m',.32)<.32 or
                            room.get('cleaning_connector_alignment',False) or
                            room.get('cleaning_turning_radius_m')is not None for room in data.values())
                            and not self.body_footprint):
                        raise ValueError('窄区连接候选必须同时显式启用--body-footprint。')
                elif not isinstance(data, dict) or not isinstance(data.get('targets'), list):
                    raise ValueError('layout缺少targets列表')
                self.config[key] = str(path.relative_to(self.root))
            fingerprints = {}
            snapshots = {}
            source_snapshots = {}
            frozen_configs = {self.config['layout'],self.config['rooms'],self.config['navigation'],
                              'src/semantic_search/config/map_resources.json',self.config['map'],
                              'src/semantic_search/config/navigate_cleaning_lane.xml',
                              'src/semantic_search/config/navigate_cleaning_connector.xml',
                              'src/semantic_search/config/navigate_service.xml',
                              'src/semantic_search/config/navigate_docking.xml',
                              'src/semantic_search/config/navigate_service_through_poses.xml',
                              'scenes/aws_house/spatial_v4.json'}
            if self.navigation_safety:
                frozen_configs.add('src/semantic_search/config/collision_monitor.yaml')
            if self.charging_station:
                frozen_configs.add(station_name)
            if self.auxiliary_prompts:
                frozen_configs.update((self.auxiliary_prompts,'resources/vision_prompts_v1.json','resources/runtime.lock.json'))
            for name in (self.config['layout'], self.config['rooms'], self.config['navigation'],
                         self.config['model'], *([self.auxiliary_model] if self.auxiliary_model else []),
                         *([self.auxiliary_prompts,'resources/vision_prompts_v1.json','resources/runtime.lock.json'] if self.auxiliary_prompts else []),
                         'src/semantic_search/semantic_search/search_node.py',
                         'src/semantic_search/semantic_search/detector.py',
                         'src/semantic_search/semantic_search/ball_geometry.py',
                         'src/semantic_search/semantic_search/detection_fusion.py',
                         'src/semantic_search/semantic_search/sensor_qos.py',
                         'src/semantic_search/semantic_search/depth.py',
                         'src/semantic_search/semantic_search/rooms.py',
                         'src/semantic_search/semantic_search/semantic_map.py',
                         'src/semantic_search/semantic_search/map_export.py',
                         'src/semantic_search/semantic_search/view_export.py',
                         'src/semantic_search/semantic_search/objects.py',
                         'src/semantic_search/semantic_search/semantic_memory.py',
                         'src/semantic_search/semantic_search/memory_guidance.py',
                         'src/semantic_search/semantic_search/memory_approach.py',
                         'scripts/validation/memory_guidance_trials.py',
                         'scripts/validation/target_stability.py',
                         'src/semantic_search/semantic_search/scene_graph.py', 'requirements-semantic.txt',
                         'src/semantic_search/semantic_search/active_observation.py',
                         'src/semantic_search/semantic_search/visibility.py',
                         'src/semantic_search/semantic_search/velocity_guard.py',
                         'src/semantic_search/semantic_search/lifecycle_startup.py',
                         'src/semantic_search/semantic_search/cloud_adapter.py',
                         'src/semantic_search/semantic_search/cloud_projection.py',
                         'src/semantic_search/semantic_search/clouds.py',
                         'src/semantic_search/config/collision_monitor.yaml',
                         'src/semantic_search/launch/navigation_safety.launch.py',
                         'src/semantic_search/semantic_search/development.py',
                         'src/semantic_search/launch/development.launch.py', 'resources/assets.lock.json',
                         'src/semantic_search/semantic_search/mapping_control.py',
                         'src/semantic_search/semantic_search/mapping_motion.py',
                         'src/semantic_search/semantic_search/cleaning.py',
                         'src/semantic_search/semantic_search/cleaning_repairs.py', 'scenes/aws_house/spatial_v4.json',
                         'src/semantic_search/semantic_search/map_resources.py',
                         'src/semantic_search/semantic_search/scenes.py',
                         'src/semantic_search/config/map_resources.json',self.config['map'],
                         'src/semantic_search/config/navigate_cleaning_lane.xml',
                         'src/semantic_search/config/navigate_cleaning_connector.xml',
                         'src/semantic_search/config/navigate_service.xml',
                         'src/semantic_search/config/navigate_docking.xml',
                         'src/semantic_search/config/navigate_service_through_poses.xml',
                         'src/semantic_search/launch/navigation.launch.py',
                         'scripts/development_navigation.sh','scripts/navigation.sh','scripts/save_map.sh',
                         station_name,
                         'src/semantic_search/semantic_search/docking.py',
                         'scripts/navigation_client.py', 'scripts/run_return.py', 'scripts/start_navigation.py',
                         'scripts/start_robot.sh', 'scripts/robot_console.py',
                         'scripts/initialize_sim_amcl.py',
                         'scripts/robot_runtime.py', 'scripts/robot_monitor.py',
                         'src/service_navfn/src/planner.cpp','src/service_navfn/include/service_navfn/planner.hpp',
                         'src/service_navfn/src/odom_memory.cpp','src/service_navfn/include/service_navfn/odom_memory.hpp',
                         'src/service_navfn/obstacle_plugins.xml',
                         'src/service_navfn/plugins.xml','src/service_navfn/package.xml','src/service_navfn/CMakeLists.txt',
                         'scripts/run_mapping_motion.py','scripts/run_cleaning.py','scripts/save_map.sh',
                         'scripts/development_detector.sh',
                         'requirements-vision-ubuntu-gpu.txt' if device=='cuda:0' else 'requirements-vision-ubuntu-cpu.txt',
                         'ui/index.html', 'ui/app.js', 'ui/style.css'):
                path = self.root / name
                if path.is_file():
                    contents = path.read_bytes()
                    fingerprints[name] = hashlib.sha256(contents).hexdigest()
                    if name in frozen_configs:
                        destination = self.session_dir/'configuration'/name
                        destination.parent.mkdir(parents=True,exist_ok=True)
                        destination.write_bytes(contents)
                        snapshots[name] = str(destination.relative_to(self.session_dir))
                    elif path.suffix!='.pt':
                        destination = self.session_dir/'sources'/name
                        destination.parent.mkdir(parents=True,exist_ok=True)
                        destination.write_bytes(contents)
                        source_snapshots[name] = str(destination.relative_to(self.session_dir))
            if self.map_resource:
                name=str(self.map_resource['image'].relative_to(self.root))
                contents=self.map_resource['image'].read_bytes()
                fingerprints[name]=hashlib.sha256(contents).hexdigest()
                destination=self.session_dir/'configuration'/name
                destination.parent.mkdir(parents=True,exist_ok=True)
                destination.write_bytes(contents)
                snapshots[name]=str(destination.relative_to(self.session_dir))
            if self.charging_station:
                self.charging_station_file=self.session_dir/snapshots[station_name]
                self.env['SEMANTIC_CHARGING_CONFIG']=str(self.charging_station_file)
            _save(self.session_dir / 'session.json', dict(
                started_utc=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
                root=str(self.root), session_dir=str(self.session_dir), config=self.config,
                source_sha256=fingerprints, configuration_snapshots=snapshots,
                source_snapshots=source_snapshots,
                note='Process running is not a sensor/localization/navigation readiness claim.'))
        except BaseException as error:
            try:
                if created_session:
                    _save(self.session_dir / 'startup_failure.json', dict(
                        error=f'{type(error).__name__}: {error}',
                        at_utc=datetime.now(timezone.utc).isoformat()))
            finally:
                self._release_locks()
            raise

    def _check_dependencies(self):
        from semantic_search.map_resources import canonical_map_yaml, resolve_map
        map_name=str(canonical_map_yaml(self.root,map_id='aws_house_v1').relative_to(self.root))
        required = ('scripts/development.sh', 'scripts/development_navigation.sh',
                    'scripts/development_detector.sh', 'scripts/development_search.sh',
                    'scripts/rviz.sh', 'install/setup.bash', '.venv/bin/python', self.model,
                    'scenes/aws_house/layout_service_surfaces_v2.json',
                    'src/semantic_search/config/rooms_aws_house_v6.json',
                    self.navigation_file,map_name,'src/semantic_search/config/map_resources.json')
        if self.navigation_safety:
            required += ('src/semantic_search/config/collision_monitor.yaml',
                         'src/semantic_search/launch/navigation_safety.launch.py')
        if self.device=='cuda:0':
            required += ('.venv-gpu/bin/python',)
        if self.auxiliary_model:
            required += (self.auxiliary_model,'resources/runtime.lock.json')
        if self.auxiliary_prompts:
            required += (self.auxiliary_prompts,'resources/vision_prompts_v1.json')
        missing = [name for name in required if not (self.root / name).is_file()]
        if missing:
            raise RuntimeError('运行资源缺失：' + ', '.join(missing)
                               + '。请按部署说明准备资源，并执行 bash scripts/build.sh'
                               + ('；GPU环境使用 bash scripts/prepare_gpu.sh 安装，或加 --device cpu' if self.device=='cuda:0' else ''))
        if self.auxiliary_model:
            lock=json.loads((self.root/'resources/runtime.lock.json').read_text())
            expected=lock['candidate_vision_models'][self.auxiliary_model]['sha256']
            if hashlib.sha256((self.root/self.auxiliary_model).read_bytes()).hexdigest()!=expected:
                raise RuntimeError('辅助权重与资源锁不一致。')
            if self.auxiliary_prompts:
                spec=lock['vision_prompt_embeddings'][self.auxiliary_model]
                if (spec['path']!=self.auxiliary_prompts or
                        hashlib.sha256((self.root/self.auxiliary_prompts).read_bytes()).hexdigest()!=spec['sha256']):
                    raise RuntimeError('辅助提示嵌入与资源锁不一致。')
        self.map_resource=resolve_map(self.root,map_id='aws_house_v1')

    def _acquire_lock(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(descriptor)
            raise RuntimeError(f'已有一键运行实例占用项目或 ROS 域 {self.domain}，请先退出已有实例') from None
        self._locks.append(descriptor)
        os.ftruncate(descriptor, 0)
        os.write(descriptor, json.dumps(dict(pid=os.getpid(), root=str(self.root), domain=self.domain)).encode())

    def _release_locks(self):
        for descriptor in reversed(self._locks):
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)
        self._locks.clear()

    def command(self, name):
        """Return argv only. No user text is ever interpolated into a shell."""
        paths = self.config
        if name == 'simulation':
            return ['bash', str(self.root / 'scripts/development.sh'),
                    'gui:=' + ('false' if self.headless else 'true'),
                    'room_doors:='+str(self.room_doors).lower(),
                    *(['gazebo_preview:=true'] if paths.get('gazebo_preview') else []),
                    'layout_file:=' + paths['layout'],
                    'depth_cloud_source:='+paths.get('depth_cloud_source','native'),
                    'camera_height:='+str(paths['camera_height']), 'camera_pitch:='+str(paths['camera_pitch']),
                    'image_width:='+paths['camera_resolution'].split('x')[0],
                    'image_height:='+paths['camera_resolution'].split('x')[1],
                    'camera_hfov:='+str(paths['camera_horizontal_fov']),
                    'velocity_topic:='+('/cmd_vel_safe' if paths['navigation_safety'] else '/cmd_vel'),
                    'charging_file:='+(str(self.charging_station_file) if self.charging_station_file else ''),
                    'evidence_dir:=' + str(self.session_dir / 'scene')]
        if name == 'safety':
            return ['ros2','launch','semantic_search','navigation_safety.launch.py']
        if name == 'navigation':
            effective = paths.get('navigation_effective')
            navigation = self.session_dir / effective if effective else self.root / paths['navigation']
            return ['bash', str(self.root / 'scripts/development_navigation.sh'),
                    'map:='+str(self.root/paths['map']),
                    'params_file:='+str(navigation)]
        if name == 'slam':
            return ['bash', str(self.root / 'scripts/mapping.sh'), 'scene:=aws_house']
        if name == 'motion':
            return ['/usr/bin/python3', '-m', 'semantic_search.mapping_motion']
        if name == 'detector':
            command=['bash', str(self.root / 'scripts/development_detector.sh'),
                    '-p', 'sensor_reliability:=reliable', '-p', 'device:='+self.device,
                    '-p', 'image_size:='+str(paths['detector']['image_size']),
                    '-p', 'model:='+str(self.root/paths['model'])]
            if self.auxiliary_model:
                parameter='ball_model' if self.ball_model else 'auxiliary_model'
                command+=['-p',parameter+':='+str(self.root/self.auxiliary_model),
                          '-p','auxiliary_categories:='+json.dumps(self.auxiliary_categories)]
            if self.auxiliary_prompts:
                command+=['-p','auxiliary_prompts:='+str(self.root/self.auxiliary_prompts)]
            return command
        if name == 'search':
            return ['bash', str(self.root / 'scripts/development_search.sh'),
                    '-p', 'rooms_file:=' + str(self.root / paths['rooms']),
                    '-p', 'scene_id:=' + paths['scene_id'],
                    '-p', 'target_categories:=' + json.dumps(paths['target_categories']),
                    '-p', 'active_observation:='+str(paths['active_observation']).lower(),
                    '-p', 'memory_guidance:='+str(paths['memory_guidance']).lower(),
                    '-p', 'memory_safe_approach:='+str(paths['memory_safe_approach']).lower(),
                    '-p', 'memory_database:='+str(self.root/'results/semantic_memory.sqlite3'),
                    '-p', 'memory_horizontal_fov:='+str(paths['camera_horizontal_fov']),
                    '-p', 'min_hits:='+str(paths['search']['min_hits']),
                    '-p', 'merge_radius:='+str(paths['search']['merge_radius']),
                    '-p', 'min_score:='+str(paths['search']['min_score']),
                    '-p', 'output_dir:=' + str(self.task_output_dir),
                    '-p', 'reject_clipped_detections:=true',
                    '-p', 'validate_object_size:=true',
                    '-p', 'sensor_reliability:=reliable']
        if name == 'rviz':
            if self.headless:
                raise ValueError('RViz is disabled in --headless mode')
            return ['bash', str(self.root / 'scripts/rviz.sh'), 'scene:=aws_house']
        raise ValueError('Unknown robot component: ' + str(name))

    def start_component(self, name):
        return self.start_process(name, self.command(name), restart=True)

    def start_process(self, name, argv, *, restart=False):
        """Register a trusted argv child, including a task client or checker."""
        if not re.fullmatch(r'[a-z][a-z0-9_-]{0,95}', name):
            raise ValueError('Invalid process name')
        if not isinstance(argv, (list, tuple)) or not argv or not all(isinstance(x, str) for x in argv):
            raise ValueError('argv must be a nonempty sequence of strings')
        with self._mutex:
            if self._closed:
                raise RuntimeError('Robot runtime is already closed')
            old = self._processes.get(name)
            if old is not None and (not restart or old['process'].poll() is None
                                    or _owned(self.marker,old['role'])):
                raise RuntimeError('Process name already used in this session: ' + name)
            generation = 1 if old is None else old['generation']+1
            label = name if generation==1 else f'{name}_{generation}'
            role = f'{ROLE_VARIABLE}={label}'.encode()
            path = self.logs_dir / (label + '.log')
            with path.open('xb') as output:
                process = subprocess.Popen(list(argv), cwd=self.root,
                                           env={**self.env,ROLE_VARIABLE:label},
                                           stdin=subprocess.DEVNULL, stdout=output,
                                           stderr=subprocess.STDOUT, start_new_session=True,
                                           close_fds=True)
            # A child may finish immediately; retain it and its exit code either way.
            row = dict(process=process, argv=list(argv), log=path,
                       identity=_identity(process.pid, self.marker), started_wall=time.time(),
                       generation=generation,role=role)
            self._processes[name] = row
            # /proc/environ may briefly lag exec immediately after Popen. Keep
            # the first verified identity so later cancellation stays pinned to
            # this child; do not turn a transient lookup miss into permanent
            # inability to send the client's graceful cancellation signal.
            deadline = time.monotonic() + .2
            while (row['identity'] is None and process.poll() is None
                   and time.monotonic() < deadline):
                time.sleep(.005)
                self._process_identity(row)
            try:
                self._write_processes()
            except BaseException:
                # The child may already have detached descendants or sent a
                # command. Close this owned session before reporting failure;
                # otherwise callers could retry alongside an untracked client.
                try:
                    self.close(graceful_seconds=1.0)
                except Exception:
                    pass  # Preserve the original registration error.
                raise
            return process

    def stop_component(self, name):
        """Reap only the current generation of one component."""
        with self._mutex:
            row = self._processes.get(name)
            if row is None:
                return
            role = row['role']
            for sig,grace in ((signal.SIGINT,4.),(signal.SIGTERM,2.),(signal.SIGKILL,1.)):
                owned = _owned(self.marker,role)
                if not owned:
                    break
                for identity in owned:
                    _signal(identity,self.marker,sig,role)
                deadline = time.monotonic()+grace
                while _owned(self.marker,role) and time.monotonic()<deadline:
                    row['process'].poll()
                    time.sleep(.05)
            row['process'].poll()
            if _owned(self.marker,role) or row['process'].returncode is None:
                raise RuntimeError(f'无法确认 {name} 已退出')

    def _write_processes(self):
        _save(self.session_dir / 'processes.json', {
            name: dict(pid=row['process'].pid, argv=row['argv'], log=str(row['log']),
                       started_wall=row['started_wall'], identity=row['identity'])
            for name, row in self._processes.items()})

    def snapshot(self):
        with self._mutex:
            values = {name: dict(state='disabled' if (self.headless and name == 'rviz'
                                 or name == 'safety' and not self.config['navigation_safety']) else 'not_started',
                                 pid=None, returncode=None, log=None) for name in COMPONENTS}
            for name, row in self._processes.items():
                code = row['process'].poll()
                values[name] = dict(state='running' if code is None else 'exited',
                                    pid=row['process'].pid, returncode=code, log=str(row['log']))
            return values

    def log_tail(self, name, lines=80):
        with self._mutex:
            row = self._processes.get(name)
            if row is None:
                raise KeyError(name)
            path = row['log']
        lines = max(1, min(int(lines), 500))
        with path.open('rb') as stream:
            stream.seek(0, os.SEEK_END)
            stream.seek(max(0, stream.tell() - 128 * 1024))
            return '\n'.join(stream.read().decode('utf-8', errors='replace').splitlines()[-lines:])

    def signal_process(self, name, sig=signal.SIGINT):
        with self._mutex:
            row = self._processes.get(name)
            if row is None or row['process'].poll() is not None:
                return False
            identity = self._process_identity(row)
            if identity is None:
                return False
            return _signal(identity, self.marker, sig)

    def _process_identity(self, row):
        """Retry only missing identities of a still-live tracked child."""
        if row['identity'] is None and row['process'].poll() is None:
            row['identity'] = _identity(row['process'].pid, self.marker)
        return row['identity']

    def close(self, graceful_seconds=4.0):
        """Stop only this session, reaping tracked children and detached descendants."""
        if not math.isfinite(graceful_seconds) or graceful_seconds < 0:
            raise ValueError('graceful_seconds must be finite and nonnegative')
        with self._mutex:
            if self._closed:
                return self._receipt
            self._closed = True
            started = time.monotonic()
            signals = []
            try:
                # Registered wrappers get a chance to run traps. Reverse startup
                # order keeps the simulator last among the normal components.
                for name, row in reversed(tuple(self._processes.items())):
                    identity = self._process_identity(row)
                    if identity and row['process'].poll() is None:
                        if _signal(identity, self.marker, signal.SIGINT):
                            signals.append(dict(name=name, pid=identity['pid'], signal='SIGINT'))
                deadline = time.monotonic() + graceful_seconds
                while _owned(self.marker) and time.monotonic() < deadline:
                    for row in self._processes.values():
                        row['process'].poll()
                    time.sleep(.05)
                for sig, wait in ((signal.SIGTERM, 2.0), (signal.SIGKILL, 1.0)):
                    remaining = _owned(self.marker)
                    if not remaining:
                        break
                    for identity in remaining:
                        if _signal(identity, self.marker, sig):
                            signals.append(dict(pid=identity['pid'], signal=sig.name))
                    deadline = time.monotonic() + wait
                    while _owned(self.marker) and time.monotonic() < deadline:
                        for row in self._processes.values():
                            row['process'].poll()
                        time.sleep(.05)
                for row in self._processes.values():
                    try:
                        row['process'].wait(timeout=.2)
                    except subprocess.TimeoutExpired:
                        pass
                remaining = _owned(self.marker)
                self._receipt = dict(closed_utc=datetime.now(timezone.utc).isoformat(),
                                     elapsed_wall_seconds=time.monotonic() - started,
                                     status='stopped' if not remaining else 'cleanup_incomplete',
                                     remaining_owned_processes=remaining, signals=signals,
                                     exit_codes={name: row['process'].poll()
                                                 for name, row in self._processes.items()},
                                     ownership='UID + unique inherited token + start_ticks + pidfd')
                if self.session_dir is not None:
                    _save(self.session_dir / 'shutdown.json', self._receipt)
                return self._receipt
            finally:
                self._release_locks()
