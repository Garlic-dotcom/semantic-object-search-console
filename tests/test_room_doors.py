import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt,label
import yaml

from semantic_search.room_doors import DOORS,add_room_doors,create_door_map,transition
from semantic_search.rooms import room_at


ROOT=Path(__file__).resolve().parents[1]


def test_closed_door_models_and_open_map_match_configured_entries(tmp_path):
    world=ET.Element('world')
    add_room_doors(world)
    rooms=json.loads((ROOT/'src/semantic_search/config/rooms_aws_house_v6.json').read_text())
    output=tmp_path/'house.yaml'
    create_door_map(ROOT/'scenes/aws_house/r0_v1/maps/house.yaml',output)
    metadata=yaml.safe_load(output.read_text())
    ox,oy,yaw=metadata['origin']
    assert yaw==0.
    resolution=metadata['resolution']
    with Image.open(tmp_path/metadata['image']) as image:
        free=np.asarray(image)[::-1]>=250
    groups,_=label(distance_transform_edt(free)*resolution>=.22)
    def component(p):
        return groups[int((p[1]-oy)/resolution),int((p[0]-ox)/resolution)]
    dock=component((-1.8,-4.))
    assert dock>0
    assert set(DOORS)|{'living'}==set(rooms)
    closed=free.copy()
    xs=ox+(np.arange(free.shape[1])+.5)*resolution
    ys=oy+(np.arange(free.shape[0])+.5)*resolution
    for name,door in DOORS.items():
        door_model=world.find(f"model[@name='room_door_{name}']")
        assert door_model.find("joint[@type='prismatic']") is not None
        outside,inside=door.staging(True)
        assert room_at(rooms,*outside[:2])=='living'
        assert room_at(rooms,*inside[:2])==name
        assert component(outside)==component(inside)==component(door.point(0.))==dock
        assert door.sweep_clearance(outside)>.38
        assert door.sweep_clearance(inside)>.38
        assert door.sweep_clearance(door.point(.13*door.inward))<1e-9
        n,t=(xs[None,:],ys[:,None]) if door.axis=='x' else (ys[:,None],xs[None,:])
        closed[(abs(n-door.fixed-.13*door.inward)<.06)&(abs(t-door.center)<door.width/2)]=False
    groups,_=label(distance_transform_edt(closed)*resolution>=.22)
    for door in DOORS.values():
        outside,inside=door.staging(True)
        assert component(inside)>0 and component(outside)!=component(inside)



def test_transition_exits_first_then_enters_and_keeps_same_room():
    assert transition('gym','gym')==[]
    assert transition('living','utility')==[(DOORS['utility'],True)]
    assert transition('gym','kitchen')==[(DOORS['gym'],False),(DOORS['kitchen'],True)]
