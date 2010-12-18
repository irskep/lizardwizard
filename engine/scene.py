"""
The Scene class manages all objects (Actors) in a level.
"""

import pyglet
import pymunk
import itertools

import actor
import camera
import gamestate
import player
import scenehandler
import terrain
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
        hts = gamestate.TILE_SIZE//2
        self.camera = camera.Camera(min_bounds=(gamestate.norm_w//2-hts, gamestate.norm_h//2-hts))
        
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
            print p
            gamestate.main_window.push_handlers(p)
    
    def exit(self):
        for p in self.players:
            print 'pop'
            gamestate.main_window.pop_handlers()
    
    def remove(self, act):
        act.delete()
        del self.actors[act.name]
    
    def load(self):
        dict_repr = util.load_yaml('levels', self.name)
        self.terrain = terrain.Terrain(self.batch, dict_repr['terrain'])
        self.players = [player.Player(self, self.batch, 1, 640, 340)]
        for p in self.players:
            self.actors[p.name] = p
        
        hts = gamestate.TILE_SIZE//2
        self.camera.max_bounds = (self.terrain.pixelwidth-gamestate.norm_w//2-hts,
                                  self.terrain.pixelheight-gamestate.norm_h//2-hts,)
    
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
        
        for act in to_delete:
            self.remove(act)
        
        self.camera.position = self.players[0].position
    
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
    
