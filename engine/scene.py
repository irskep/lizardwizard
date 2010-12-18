"""
The Scene class manages all objects (Actors) in a level.
"""

import pyglet
import pymunk
import itertools

import actor
import gamestate
import player
import scenehandler
import util

from util import pushmatrix, draw, interpolator

update_t = 1/72.0

pymunk_update_t = 1/120.0

draw_paths = True
draw_player_path = True

class Scene(object):
    
    # Initialization
    
    def __init__(self, name, scene_handler=None):
        super(Scene, self).__init__()
        self.name = name
        self.handler = scene_handler
        self.batch = pyglet.graphics.Batch()
        self.actors = {}
        self.players = []
        
        self.game_time = 0.0
        self.accum_time = 0.0
        self.clock = pyglet.clock.Clock(time_function=lambda: self.game_time)
        self.paused = False
        
        self.space = pymunk.Space()
        self.space.set_default_collision_handler(self.handle_collision, None, None, None)
        self.pymunk_accum = 0.0
        
        self.init_clock()
        self.interp = interpolator.InterpolatorController()
        
        self.load()
        
        self.update(0)
    
    def enter(self):
        for p in self.players:
            gamestate.main_window.push_handlers(p)
    
    def exit(self):
        for p in self.players:
            gamestate.main_window.pop_handlers()
    
    def remove(self, act):
        act.delete()
        del self.actors[act.name]
    
    def load(self):
        dict_repr = util.load_yaml('levels', self.name)
        # IT'S A TOTAL MYSTERY WHAT THE LEVELS WILL BE! HOW EXCITING!!!
    
    def handle_collision(self, space, arbiter, *args, **kwargs):
        for s in arbiter.shapes:
            self.remove(s.parent)
        return True
    
    # Update/draw
    
    def update(self, dt=0):
        if self.paused: 
            return
        
        self.pymunk_accum += dt
        while self.pymunk_accum >= pymunk_update_t:
            self.space.step(pymunk_update_t)
            self.pymunk_accum -= pymunk_update_t
        
        # We have a custom clock that stops when the game is paused
        self.update_clock(dt)
        self.interp.update_interpolators(dt)
        
        to_delete = set()
        
        # Also update the actors
        for act in self.actors.itervalues():
            act.update(dt)
            if abs(act.x-self.player.actor.x) > gamestate.norm_w*2 \
            or abs(act.y-self.player.actor.y) > gamestate.norm_h*2:
                to_delete.add(act)
        
        for act in to_delete:
            self.remove(act)
    
    def draw(self, dt=0):
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
    