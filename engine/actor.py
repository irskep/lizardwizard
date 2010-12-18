"""
A collection of graphics primitives with interpolators that represents a single object. Will eventually be connected to pymunk (physics).

You can probably figure out how this works by reading the sprite YAML files and this chapter of the pyglet programming guide: http://pyglet.org/doc/programming_guide/graphics.html
"""

import math
import pyglet
import pymunk

from pymunk._chipmunk import _cpvlerp as lerp

import util

def id_generator():
    i = 0
    while True:
        yield i
        i += 1

next_actor_id = id_generator()

DEG_TO_RAD = math.pi*2/360.0
RAD_TO_DEG = 360.0/math.pi*2

class Actor(object):
    def __init__(self, scn=None, batch=None, kind="unknown", x=0, y=0, name=None):
        super(Actor, self).__init__()
        self.atl = above_the_law #..s of physics
        self.scene = scn
        self.batch = batch
        self.interp = util.interpolator.InterpolatorController()
        
        if name is None:
            name = next_actor_id.next()
        self.name = name
        
        if self.scene:
            mass = 100
            circle_radius = 10
            moment = pymunk.moment_for_circle(mass, 0, circle_radius)
            collision_group = ENEMY
            self.body = pymunk.Body(mass, moment)
            self.body.position = (x, y)
            self.body.angle = r*DEG_TO_RAD
            self.shape = pymunk.Circle(self.body, circle_radius)
            self.shape.parent = self
            self.shape.group = collision_group
            self.scene.space.add(self.body, self.shape)
        else:
            self.shape = None
            self.body = None
    
    def update(self, dt):
        pass
    
    def delete(self):
        if self.shape:
            self.scene.space.remove(self.shape)
        if self.body and not self.atl:
            self.scene.space.remove(self.body)
    
    def __repr__(self):
        return "Actor(name=%s, kind=%s, x=%0.1f, y=%0.1f, r=%0.1f)" % (
                        str(self.name), self.kind, self.x, self.y, self.r)
    
    def _set_position(self, v):
        self.body.position = v
    
    def _set_x(self, v):
        self._set_position((v, self.body.position[1]))
    
    def _set_y(self, v):
        self._set_position((self.body.position[0], v))
    
    def _set_r(self, v):
        self.body.angle = v*DEG_TO_RAD
    
    position = property(lambda self: self.body.position, _set_position)
    x = property(lambda self: self.body.position[0], _set_x)
    y = property(lambda self: self.body.position[1], _set_y)
    r = property(lambda self: self.group.r, _set_r)
