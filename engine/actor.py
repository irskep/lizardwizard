"""
A collection of graphics primitives with interpolators that represents a single object. Will eventually be connected to pymunk (physics).

You can probably figure out how this works by reading the sprite YAML files and this chapter of the pyglet programming guide: http://pyglet.org/doc/programming_guide/graphics.html
"""

import math
import pyglet
import pymunk

from pymunk._chipmunk import _cpvlerp as lerp

import gamestate
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
        self.scene = scn
        self.batch = batch
        self.kind = kind
        self.interp = util.interpolator.InterpolatorController()
        self.vx, self.vy = 0.0, 0.0
        
        if name is None:
            name = next_actor_id.next()
        self.name = name
        
        if self.scene:
            self.body = pymunk.Body(pymunk.inf, pymunk.inf)
            self.body.position = (x, y)
            # self.body.angle = r*DEG_TO_RAD
            self.shape = pymunk.Circle(self.body, gamestate.TILE_SIZE/2)
            self.shape.parent = self
            self.scene.space.add(self.shape)
        else:
            self.shape = None
            self.body = None
    
    def update(self, dt):
        self.body.position[0] += self.vx*dt
        self.body.position[1] += self.vy*dt
    
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
    r = property(lambda self: self.body.angle*RAD_TO_DEG, _set_r)
