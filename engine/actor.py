"""
A collection of graphics primitives with interpolators that represents a single object. Will eventually be connected to pymunk (physics).

You can probably figure out how this works by reading the sprite YAML files and this chapter of the pyglet programming guide: http://pyglet.org/doc/programming_guide/graphics.html
"""

import math
import pyglet
import pymunk

import gamestate
import images
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
        
        self.sprite = pyglet.sprite.Sprite(images.sits[self.kind], batch=batch, x=x, y=y)
        
        if name is None:
            name = next_actor_id.next()
        self.name = name
        
        self.move_x = 0
        self.move_y = 0
        
        self.shapes = []
        
        self.init_physics(x, y)
    
    def init_physics(self, x, y):
        mass = 100
        moment = pymunk.moment_for_circle(mass, 0, gamestate.TILE_SIZE*0.4)
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, y)
        # self.body.angle = r*DEG_TO_RAD
        s = pymunk.Circle(self.body, gamestate.TILE_SIZE*0.4)
        s.parent = self
        s.elasticity = 0.0
        self.shapes.append(s)
        self.scene.space.add(self.body, *self.shapes)
    
    def update(self, dt):
        self.sprite.position = (self.body.position[0], self.body.position[1])
        self.body.angular_velocity = 0
        a = self.body.angle
        self.sprite.rotation = -a/math.pi*180.0+90.0
    
    def delete(self):
        for s in self.shapes:
            self.scene.space.remove(s)
        if self.body:
            self.scene.space.remove(self.body)
        self.sprite.delete()
    
    def reset_motion(self):
        self.body.velocity[0] = gamestate.MOVE_SPEED*self.move_x
        self.body.velocity[1] = gamestate.MOVE_SPEED*self.move_y
    
    def start_moving(self):
        self.sprite.image = images.walks[self.kind]
    
    def estop(self):
        self.move_x, self.move_y = 0
        self.stop_moving()
    
    def stop_moving(self):
        if self.move_x != 0 or self.move_y != 0:
            return
        self.sprite.image = images.sits[self.kind]
    
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
