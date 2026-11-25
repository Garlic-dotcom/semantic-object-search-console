#!/usr/bin/env python3
"""Approach a powered doorway, confirm its joint position, then cross it."""
import argparse
import json
from math import dist
import os
from pathlib import Path
import signal
import time

import rclpy
from rclpy.signals import SignalHandlerOptions
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64

from nav2_msgs.srv import ClearEntireCostmap
from navigation_client import NavigationRun, StopRequested
from robot_console import write_json
from semantic_search.room_doors import DOORS, transition
from semantic_search.rooms import room_at


class DoorRun(NavigationRun):
    def __init__(self,args,stopped):
        super().__init__(args,stopped,node_name='room_door_transit')
        self.progress_filename='door_progress.json'
        self.feedback={}
        self.pubs={}
        self.events=[]
        self.clearing=[self.node.create_client(ClearEntireCostmap,
            f'/{name}_costmap/clear_entirely_{name}_costmap') for name in ('local','global')]

        for name in DOORS:
            self.pubs[name]=self.node.create_publisher(Float64,f'/doors/{name}/command',10)
            self.node.create_subscription(JointState,f'/doors/{name}/joint_state',
                                          lambda msg,n=name:self.receive_door(n,msg),10)

    def receive_door(self,name,msg):
        if 'slide' in msg.name:
            index=msg.name.index('slide')
            if index<len(msg.position):
                self.feedback[name]=(time.monotonic(),msg.position[index])

    def set_door(self,door,opening):
        if not self.parked():
            raise RuntimeError('打开或关闭门之前需要停稳。')
        location=self.pose()
        if location is None:
            raise RuntimeError('无法确认门前位置。')
        distance=dist(location[:2],door.point(0.))
        if distance>1.15 or door.sweep_clearance(location)<.38:
            raise RuntimeError('请在门前安全位置停稳再操作门。')
        target=door.travel if opening else 0.
        self.stage='opening_door' if opening else 'closing_door'
        def confirmed():
            stamp,measured=self.feedback.get(door.room,(0.,0.))
            if time.monotonic()-stamp<.6 and abs(measured-target)<.035:
                return True
            command=Float64()
            command.data=target
            self.pubs[door.room].publish(command)
            return False
        self.wait_for(confirmed,20,require_pose=True)
        self.events.append(dict(door=door.room,stage='opened' if opening else 'closed',
                                position_m=self.feedback[door.room][1],base_pose=list(location)))
        print(self.events[-1],flush=True)

    def reobserve_doorway(self):
        # Remove old observations of the closed panel, then let the running
        # layers refill from live range data before allowing a new action.
        self.wait_for(lambda:all(client.service_is_ready() for client in self.clearing),
                      5,require_pose=True)
        calls=[client.call_async(ClearEntireCostmap.Request()) for client in self.clearing]
        self.wait_for(lambda:all(call.done() for call in calls),5,require_pose=True)
        for call in calls:
            call.result()
        refresh_at=self.node.get_clock().now().nanoseconds+2_000_000_000
        self.wait_for(lambda:self.node.get_clock().now().nanoseconds>=refresh_at and self.parked(),
                      12,require_pose=True)

    def run(self):
        cfg=json.loads(self.args.rooms.read_text())
        self.wait_for(lambda:self.pose() and self.parked() and
                      (self.args.kind=='door' or self.client.server_is_ready()),20)
        here=self.pose()
        self.start_pose=here
        self.last_pose_wall=time.monotonic()
        if self.args.kind=='door':
            name=min(DOORS,key=lambda k:dist(here[:2],DOORS[k].point(0.)))
            self.set_door(DOORS[name],self.args.room=='open')
            return
        start=room_at(cfg,*here[:2])
        if start is None:
            raise RuntimeError('机器人未定位到可识别的房间。')
        for door,entering in transition(start,self.args.room):
            approach,inside=door.staging(entering)
            self.stage='approaching_door'
            if not self.go(approach,self.deadline,timeout=130,purpose='room_entry'):
                raise RuntimeError('无法到达门前：'+door.room)
            self.set_door(door,True)
            self.reobserve_doorway()
            self.stage='crossing_door'
            if not self.go(inside,self.deadline,timeout=30,purpose='room_entry'):
                raise RuntimeError('门已打开，但机器人未能通行：'+door.room)
            pose=self.pose()
            measured_in=pose and room_at(cfg,*pose[:2])==(door.room if entering else 'living')
            if not measured_in or dist(pose[:2],inside[:2])>.24:
                raise RuntimeError('没有确认机器人越过门口：'+door.room)
            self.events.append(dict(door=door.room,stage='crossed',entering=entering,base_pose=list(pose)))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind',choices=('search','clean','return','door'))
    parser.add_argument('room')
    parser.add_argument('rooms',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('command',nargs=argparse.REMAINDER)
    args=parser.parse_args()
    args.timeout=240.
    stopped=[]
    for name in (signal.SIGINT,signal.SIGTERM):
        signal.signal(name,lambda sig,frame:stopped.append(sig))
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    status,message='failed','门口操作未完成。'
    node=None
    try:
        node=DoorRun(args,stopped)
        node.run()
        status,message='completed','已完成门口操作。'
    except StopRequested:
        status,message='canceled','已停止门口操作。'
    except Exception as error:
        message=str(error)
    finally:
        settled=bool(node and node.settled)
        report=dict(status=status,message=message,navigation_settled=settled,
                    events=node.events if node else [],trace=node.trace if node else [],goals=node.goals if node else [])
        name='door_return.json' if args.kind=='return' and (args.output/'door_route.json').exists() else 'door_route.json'
        write_json(args.output/name,report)
        if node:
            node.node.destroy_node()
        rclpy.try_shutdown()
    if stopped and status=='completed':
        status,message='canceled','已停止门口操作。'
    if args.kind=='door':
        return 0 if status=='completed' else 130 if status=='canceled' else 1
    if status=='completed' and args.command:
        os.execv(args.command[0],args.command)
    if args.kind=='search':
        write_json(args.output/'diagnostics.json',
                   dict(command_sent=not settled,outcome='door_transit',errors=[message]))
    else:
        name='clean_result.json' if args.kind=='clean' else 'return_result.json'
        write_json(args.output/name,dict(status=status,message=message,navigation_settled=settled))
    return 130 if status=='canceled' else 1


if __name__=='__main__':
    raise SystemExit(main())
