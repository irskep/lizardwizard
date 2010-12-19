import math
import functools
import pyglet
import pymunk
import random

import actor
import gamestate

class Fly(actor.Actor):
    def __init__(self, scn, batch, x, y):
        super(Fly, self).__init__(scn, batch, kind='fly', x=x, y=y)
        self.angle_target = random.random()*math.pi*2.0
        self.body.angle = random.random()*math.pi*2.0
        pyglet.clock.schedule_once(self.change_angular_velocity, 0.8+random.random())
    
    def delete(self):
        super(Fly, self).delete()
        pyglet.clock.unschedule(self.change_angular_velocity)
    
    def change_angular_velocity(self, dt=0):
        self.body.angular_velocity = (random.random()*math.pi*2.0-math.pi)*2
        pyglet.clock.schedule_once(self.change_angular_velocity, 0.8+random.random())
    
    def update(self, dt=0):
        super(Fly, self).update(dt)
        a = self.body.angle
        self.body.velocity = (math.cos(a)*160, math.sin(a)*160)
    
