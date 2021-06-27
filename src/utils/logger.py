import json
import os
import time

from rlbot.utils.structures.game_data_struct import GameTickPacket, PlayerInfo, BallInfo, Physics as PhysicsInfo
from src.utils.vec import Vec3, Location, EulerAngles, Velocity, AngularVelocity, Quaternion
from typing import Union


class Logger:
    def __init__(self, name: str):
        self.name = name
        self.data = FrameList()
        self.start_time = time.time()
        self.was_dumped = False

    def dump(self):
        self.was_dumped = True
        i = 0
        while os.path.exists(self.name + str(i) + '.json'):
            i += 1

        with open(self.name + str(i) + '.json', 'w') as logfile:
            json.dump(self.data, logfile, cls=ComplexEncoder, indent=4)

    def log(self, packet: GameTickPacket):
        self.data.add(packet, time.time() - self.start_time)


class FrameList:
    def __init__(self):
        self.frames = []

    def add(self, packet: GameTickPacket, current_time: float):
        self.frames.append(Frame(packet, current_time))


class Frame:
    def __init__(self, packet: GameTickPacket, current_time: float):
        self.time = current_time
        self.game_cars = [Car(packet.game_cars[i]) for i in range(0, packet.num_cars)]
        self.game_ball = GameObject(packet.game_ball)


class GameObject:
    def __init__(self, info: Union[BallInfo, PlayerInfo]):
        self.physics = Physics(info.physics)


class Physics:
    def __init__(self, physics: PhysicsInfo):
        self.location = Location(physics.location)
        self.rotation = Quaternion(physics.rotation)
        self.velocity = Velocity(physics.velocity)
        self.angular_velocity = AngularVelocity(physics.angular_velocity)


class Car(GameObject):
    def __init__(self, player_info: PlayerInfo):
        super(Car, self).__init__(player_info)
        self.has_wheel_contact = player_info.has_wheel_contact
        self.jumped = player_info.jumped
        self.boost = player_info.boost


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (FrameList, Frame, GameObject, Physics, Car)):
            return obj.__dict__
        elif isinstance(obj, (Location, Quaternion, Velocity, AngularVelocity)):
            return {slot: getattr(obj, slot) for slot in obj.__slots__}
        else:
            return json.JSONEncoder.default(self, obj)