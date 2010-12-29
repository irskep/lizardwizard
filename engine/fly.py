import math
import functools
import pyglet
import pymunk
import random

import actor
import gamestate
import player

colorsf = [(1.0, 0.0, 0.0), (1.0, 0.5, 0.0), (1.0, 1.0, 0.0), 
           (0.5, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 1.0, 0.5), 
           (0.0, 1.0, 1.0), (0.0, 0.5, 1.0), (0.0, 0.0, 1.0), 
           (0.5, 0.0, 1.0), (1.0, 0.0, 1.0), (1.0, 0.0, 0.5)]
colorsb = [tuple([int(255*i) for i in c]) for c in colorsf]

def cycle_color_indexes_gen():
    i = 0
    while True:
        yield i
        i = (i + 1) % len(colorsb)

color_indexes_cycler = cycle_color_indexes_gen()

color_map = {}
def color_for_title(t):
    if not color_map.has_key(t):
        color_map[t] = colorsb[color_indexes_cycler.next()]
    return color_map[t]

class Fly(actor.Actor):
    def __init__(self, scn, batch, x, y, piece, good=True):
        super(Fly, self).__init__(scn, batch, kind='fly', x=x, y=y)
        self.sprite.color = color_for_title(piece[0])
        self.piece = piece
        self.good = good
        self.sprite.group = pyglet.graphics.OrderedGroup(1)
        self.angle_target = random.random()*math.pi*2.0
        self.body.angle = random.random()*math.pi*2.0
        pyglet.clock.schedule_once(self.change_angular_velocity, 0.8+random.random())
    
    def init_physics(self, x, y):
        #  All normal except collision group
        mass = 100
        moment = pymunk.moment_for_circle(mass, 0, gamestate.TILE_SIZE*0.6)
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, y)
        # self.body.angle = r*DEG_TO_RAD
        s = pymunk.Circle(self.body, gamestate.TILE_SIZE*0.6)
        s.parent = self
        s.group = player.BODY_GROUP
        s.elasticity = 0.0
        self.shapes.append(s)
        self.scene.space.add(self.body, *self.shapes)
    
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
    
