"""
The Scene class manages all objects (Actors) in a level.
"""

import pyglet
import pymunk
import itertools

import actor
import camera
import fly
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
        self.space._space.elasticIterations = 0
        self.space.set_default_collision_handler(self.collision_events, None, None,
                                                 self.enforce_wall_hugging)
        self.pymunk_accum = 0.0
        
        self.init_clock()
        self.interp = interpolator.InterpolatorController()
        
        self.load()
        
        self.events = 0
        
        self.update(0)
    
    def enter(self):
        if not self.events:
            self.events += len(self.players)
            for p in self.players:
                gamestate.main_window.push_handlers(p)
    
    def exit(self):
        if self.events:
            self.events -= len(self.players)
            for p in self.players:
                gamestate.main_window.pop_handlers()
    
    def remove(self, act):
        act.delete()
        del self.actors[act.name]
        del self.space
    
    def load(self):
        self.grid = []
        with pyglet.resource.file('game/levels/%s.txt' % self.name) as f:
            for line in f:
                row = line.split()
                self.width = len(row)
                self.grid.append(row)
            self.height = len(self.grid)
        
        data = {}
        handlers = {
            'P': self._make_player,
            'F': self._make_foot,
            'Y': self._make_fly,
        }
        for y, row in enumerate(self.grid):
            for x, char in enumerate(row):
                f = handlers.get(char)
                if f:
                    f(x, y)
        
        self.terrain = terrain.Terrain(self.batch, self.space, self.grid)
        
        hts = gamestate.TILE_SIZE//2
        self.camera.max_bounds = (self.pixelwidth-gamestate.norm_w//2-hts,
                                  self.pixelheight-gamestate.norm_h//2-hts,)
    
    pixelwidth = property(lambda self: self.width*gamestate.TILE_SIZE)
    pixelheight = property(lambda self: self.height*gamestate.TILE_SIZE)
    
    def place(self, x, y):
        return x*gamestate.TILE_SIZE, y*gamestate.TILE_SIZE
    
    def _make_player(self, x, y):
        i = len(self.players) + 1
        np = player.Player(self, self.batch, i, *self.place(x, y))
        self.players.append(np)
        self.actors[np.name] = np
    
    def _make_foot(self, x, y):
        na = actor.Actor(self, self.batch, 'foot', *self.place(x, y))
        self.actors[na.name] = na
    
    def _make_fly(self, x, y):
        na = fly.Fly(self, self.batch, *self.place(x, y))
        self.actors[na.name] = na
    
    def local_to_world(self, x, y):
        return ((x+self.camera.x-640)/gamestate.scale_factor,
                (y+self.camera.y-360)/gamestate.scale_factor)
    
    # Physics
    
    def enforce_wall_hugging(self, space, arbiter, *args, **kwargs):
        for s in arbiter.shapes:
            try:
                p = s.parent
                p.reset_motion()
            except AttributeError:
                pass
        return True
    
    def collision_events(self, space, arbiter, *args, **kwargs):
        tags = []
        for s in arbiter.shapes:
            if hasattr(s, 'parent'):
                tags.append(s.parent.kind)
        
        if 'player' in tags and 'foot' in tags and self.events:
            for p in self.players:
                p.move_x, p.move_y = 0, 0
                p.reset_motion()
                p.update_walk_anim()
            f = [x for x in self.actors.itervalues() if x.kind == 'foot'][0]
            f.delete()
            del self.actors[f.name]
            self.handler.go_to("2")
        elif 'player' in tags and 'fly' in tags:
            pass
        elif 'player' in tags and len(arbiter.shapes) == 2 and len(tags) == 1:
            a, b = arbiter.shapes
            if hasattr(b, 'parent'):
                a, b = b, a
            if a in a.parent.tongue_shapes:
                if a.parent.tongue_state == player.TONGUE_EXITING and a in a.parent.tongue_shapes:
                    a.parent.tongue_state = player.TONGUE_ENTERING
                return False
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
            # draw.set_color(1,0,0,1)
            # for p in self.players:
            #     for size, (offset_x, offset_y) in p.collision_circles:
            #         draw.circle(p.x+offset_x, p.y+offset_y, size)
            # draw.set_color(1,1,1,1)
    
    
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
    
