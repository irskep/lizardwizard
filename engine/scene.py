"""
The Scene class manages all objects (Actors) in a level.
"""

import pyglet
import pymunk
import itertools

import camera
import gamestate

from util import pushmatrix, draw, interpolator

update_t = 1/72.0

class Scene(object):
    
    # Initialization
    
    def __init__(self, name, scene_handler):
        super(Scene, self).__init__()
        self.name = name
        self.handler = scene_handler
        self.batch = pyglet.graphics.Batch()
        self.actors = {}
        hts = gamestate.TILE_SIZE//2
        self.camera = camera.Camera(min_bounds=(gamestate.norm_w//2, gamestate.norm_h//2))
        
        self.game_time = 0.0
        self.accum_time = 0.0
        self.clock = pyglet.clock.Clock(time_function=lambda: self.game_time)
        self.paused = False
        
        self.init_clock()
        self.interp = interpolator.InterpolatorController()
        
        self.to_delete = set()
    
    def enter(self):
        pass
    
    def exit(self):
        pass
    
    def remove(self, act):
        self.to_delete.add(act)
    
    # Update/draw
    
    def update(self, dt=0):
        if self.paused: 
            return
        
        # We have a custom clock that stops when the game is paused
        self.update_clock(dt)
        self.interp.update_interpolators(dt)
        
        # Also update the actors
        for act in self.actors.itervalues():
            act.update(dt)
        
        for act in self.to_delete:
            del self.actors[act.name]
            act.delete()
        
        self.to_delete = set()
    
    def draw(self, dt=0):
        with camera.apply_camera(self.camera):
            self.batch.draw()
    
    
    # Clock
    
    def init_clock(self):
        self.game_time = 0.0
        self.accum_time = 0.0
        self.clock = pyglet.clock.Clock(time_function=lambda: self.game_time)
    
    def update_clock(self, dt=0):
        # Align updates to fixed timestep 
        self.accum_time += dt 
        if self.accum_time > update_t * 3: 
            self.accum_time = update_t 
        while self.accum_time >= update_t: 
            self.game_time += update_t
            self.clock.tick() 
            self.accum_time -= update_t
    
