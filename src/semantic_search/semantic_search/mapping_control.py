"""Bounded commands and short, map-checked detours for the mapping mode."""
import math
import re

import numpy as np
from scipy.ndimage import distance_transform_edt


ALIASES = {
    'forward': ('前进', '向前', '往前', '直走', '向前走', '往前走'),
    'backward': ('后退', '向后', '往后', '倒退', '向后退'),
    'left': ('左转', '向左转', '往左转'),
    'right': ('右转', '向右转', '往右转'),
    'faster': ('加速', '快一点', '快点'),
    'slower': ('减速', '慢一点', '慢点'),
    'stop': ('停止', '停下', '停住', '停车'),
    'detour': ('绕行', '绕过障碍', '绕开障碍'),
}
COMMANDS = frozenset(ALIASES)
RADIUS = .22
MARGIN = .07
MAX_SPEED = .26
MAX_TURN = .70
PULSE_SECONDS = 1.5


def parse_motion(text):
    word = re.sub(r'[\s，。！？,.!?]+', '', text.strip()).lower()
    for prefix in ('麻烦你', '请你', '请'):
        if word.startswith(prefix):
            word = word.removeprefix(prefix)
            break
    for suffix in ('一下', '吧'):
        word = word.removesuffix(suffix)
    if word in COMMANDS:
        return word
    for name, aliases in ALIASES.items():
        if word in aliases:
            return name
    raise ValueError('请说一条运动指令，例如前进、左转、停止或绕行。')


def obstacle(points, linear, angular, reaction_seconds=.9):
    """Nearest point within the next swept circular base footprint."""
    if not (linear or angular):
        return None
    reach = linear * reaction_seconds
    radius = RADIUS + MARGIN
    nearest = None
    for x, y in points:
        if reach and abs(y) <= radius:
            # Ignore the opposite half plane for straight motion. A pure turn
            # checks the whole footprint, regardless of steering direction.
            if x * linear < 0:
                continue
        edge = min(max(x, min(0., reach)), max(0., reach))
        if math.hypot(x-edge, y) <= radius:
            distance = math.hypot(x, y)
            nearest = distance if nearest is None else min(nearest, distance)
    return nearest


def angle_difference(target, current):
    return math.remainder(target-current, 2*math.pi)


def short_detour(grid, position, heading, obstacles=()):
    """Find a short rectangular bypass through known space only.

    The grid uses map coordinates. The current scan is also rasterized so a
    newly seen obstacle still constrains the route while SLAM updates.
    """
    info = grid.info
    resolution = float(info.resolution)
    width, height = info.width, info.height
    if not (0 < resolution <= .15 and 0 < width*height <= 2_000_000):
        return None
    origin = info.origin
    q = origin.orientation
    yaw = math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
    c, s = math.cos(yaw), math.sin(yaw)

    def cell(x, y):
        dx, dy = x-origin.position.x, y-origin.position.y
        return math.floor((c*dx+s*dy)/resolution), math.floor((-s*dx+c*dy)/resolution)

    free = np.asarray(grid.data).reshape(height,width) == 0
    for x, y in obstacles:
        col, row = cell(x,y)
        if 0 <= col < width and 0 <= row < height:
            free[row,col] = False
    clearance = distance_transform_edt(np.pad(free, 1))[1:-1,1:-1] * resolution
    safe_radius = RADIUS + MARGIN + resolution * .8

    def safe(x, y):
        col, row = cell(x,y)
        return 0 <= col < width and 0 <= row < height and clearance[row,col] >= safe_radius

    def segment(a, b):
        steps = max(1, math.ceil(math.dist(a,b) / (resolution/2)))
        return all(safe(a[0]+(b[0]-a[0])*i/steps, a[1]+(b[1]-a[1])*i/steps)
                   for i in range(steps+1))

    x,y = position
    dx,dy = math.cos(heading),math.sin(heading)
    for ahead in (1.0, 1.3, 1.6):
        end = (x+ahead*dx,y+ahead*dy)
        if not safe(*end) or segment(position,end):
            continue
        for width_offset in (.60, .80, 1.0):
            for side in (width_offset,-width_offset):
                a = (x-side*dy, y+side*dx)
                b = (end[0]-side*dy, end[1]+side*dx)
                route = [position,a,b,end]
                if all(segment(p,q) for p,q in zip(route,route[1:])):
                    return route[1:]
    return None
