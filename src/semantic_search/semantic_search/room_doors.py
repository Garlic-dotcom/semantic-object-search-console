"""Geometry and calibrated entrances for the optional powered-door house."""
from dataclasses import dataclass
from math import atan2, hypot
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class Door:
    room: str
    axis: str
    fixed: float
    center: float
    minimum: float
    maximum: float
    inward: int
    width: float = 1.10

    @property
    def travel(self):
        return self.width+.02

    @property
    def direction(self):
        return 1 if self.maximum-self.center>=self.center-self.minimum else -1

    def sweep_clearance(self,point):
        normal,tangent=point[:2] if self.axis=='x' else point[:2][::-1]
        across=normal-self.fixed-.13*self.inward
        offset=tangent-self.center
        low=min(0.,self.direction*self.travel)-self.width/2
        high=max(0.,self.direction*self.travel)+self.width/2
        return hypot(across,max(low-offset,offset-high,0.))

    def point(self,normal,tangent=0.):
        positions=(self.fixed+normal,self.center+tangent)
        return positions if self.axis=='x' else positions[::-1]

    def staging(self,entering):
        sign=self.inward if entering else -self.inward
        a=self.point(-sign*.62)
        b=self.point(sign*.62)
        yaw=atan2(b[1]-a[1],b[0]-a[0])
        return (*a,yaw),(*b,yaw)


DOORS = {
    door.room:door for door in (
        Door('kitchen','x',4.8,-.8,-5.5,3.1,1),
        Door('bedroom','x',-2.5,-.5,-1.5,3.1,-1),
        Door('utility','x',-2.5,-2.05,-5.5,-1.5,-1),
        Door('gym','y',1.,0.,-2.5,4.8,1),
    )
}


def walls():
    for door in DOORS.values():
        for low,high in ((door.minimum,door.center-door.width/2),
                         (door.center+door.width/2,door.maximum)):
            if high-low>.001:
                yield door.axis,door.fixed,low,high
    # Recess the wall end from the utility panel's sweep. The 0.21 m
    # recess is narrower than the robot and leaves both rooms isolated.
    yield 'y',-1.5,-9.3,-2.71


def transition(start_room,end_room):
    if start_room==end_room:
        return []
    route=[]
    if start_room in DOORS:
        route.append((DOORS[start_room],False))
    if end_room in DOORS:
        route.append((DOORS[end_room],True))
    return route


def _box(link,size,color):
    for name in ('collision','visual'):
        item=ET.SubElement(link,name,name=name)
        dims=ET.SubElement(ET.SubElement(ET.SubElement(item,'geometry'),'box'),'size')
        dims.text=' '.join(map(str,size))
        if name=='visual':
            ET.SubElement(ET.SubElement(item,'material'),'diffuse').text=color


def add_room_doors(world):
    for i,(axis,fixed,lo,hi) in enumerate(walls()):
        x,y=(fixed,(lo+hi)/2) if axis=='x' else ((lo+hi)/2,fixed)
        size=(.10,hi-lo,2.10) if axis=='x' else (hi-lo,.10,2.10)
        model=ET.SubElement(world,'model',name=f'room_partition_{i}')
        ET.SubElement(model,'static').text='true'
        ET.SubElement(model,'pose').text=f'{x} {y} 1.05 0 0 0'
        link=ET.SubElement(model,'link',name='wall')
        _box(link,size,'.73 .76 .79 1')
    for room,door in DOORS.items():
        model=ET.SubElement(world,'model',name='room_door_'+room)
        x,y=door.point(.13*door.inward)
        ET.SubElement(model,'pose').text=f'{x} {y} 1.015 0 0 0'
        link=ET.SubElement(model,'link',name='panel')
        ET.SubElement(link,'gravity').text='false'
        size=(.07,door.width+.01,2.02) if door.axis=='x' else (door.width+.01,.07,2.02)
        _box(link,size,'.53 .27 .12 1')
        inertial=ET.SubElement(link,'inertial')
        ET.SubElement(inertial,'mass').text='2.'
        inertia=ET.SubElement(inertial,'inertia')
        for key,val in dict(ixx=1.,iyy=1.,izz=.5,ixy=0.,ixz=0.,iyz=0.).items():
            ET.SubElement(inertia,key).text=str(val)
        joint=ET.SubElement(model,'joint',name='slide',type='prismatic')
        ET.SubElement(joint,'parent').text='world'
        ET.SubElement(joint,'child').text='panel'
        axis=ET.SubElement(joint,'axis')
        # Slide toward the longer wall segment, never into the doorway.
        sign=door.direction
        ET.SubElement(axis,'xyz').text=f'0 {sign} 0' if door.axis=='x' else f'{sign} 0 0'
        limit=ET.SubElement(axis,'limit')
        for key,val in dict(lower=0,upper=door.travel,effort=45,velocity=.85).items():
            ET.SubElement(limit,key).text=str(val)
        controller=ET.SubElement(model,'plugin',filename='ignition-gazebo-joint-position-controller-system',
                                 name='ignition::gazebo::systems::JointPositionController')
        for key,val in dict(joint_name='slide',topic=f'/doors/{room}/command',p_gain=65,d_gain=8,
                            cmd_max=38,cmd_min=-38).items():
            ET.SubElement(controller,key).text=str(val)
        feedback=ET.SubElement(model,'plugin',filename='ignition-gazebo-joint-state-publisher-system',
                               name='ignition::gazebo::systems::JointStatePublisher')
        ET.SubElement(feedback,'joint_name').text='slide'
        ET.SubElement(feedback,'topic').text=f'/doors/{room}/joint_state'


def create_door_map(source,output):
    """Generate an open-door planning map from partitions only."""
    from pathlib import Path
    from PIL import Image
    import numpy as np
    import yaml
    source,output=Path(source),Path(output)
    config=yaml.safe_load(source.read_text())
    ox,oy,yaw=config['origin']
    if yaw!=0:
        raise ValueError('Door profile requires the calibrated nonrotated map')
    r=config['resolution']
    with Image.open(source.parent/config['image']) as image:
        values=np.asarray(image.convert('L')).copy()
    yy=oy+(values.shape[0]-np.arange(values.shape[0])-.5)*r
    xx=ox+(np.arange(values.shape[1])+.5)*r
    for axis,fixed,lo,hi in walls():
        n,t=(xx[None,:],yy[:,None]) if axis=='x' else (yy[:,None],xx[None,:])
        values[(np.abs(n-fixed)<=.055)&(t>=lo-r/2)&(t<=hi+r/2)]=0
    output.parent.mkdir(parents=True,exist_ok=True)
    config['image']=output.with_suffix('.pgm').name
    Image.fromarray(values).save(output.with_suffix('.pgm'))
    output.write_text(yaml.safe_dump(config,sort_keys=False))
