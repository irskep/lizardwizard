"""
The Scene class manages all objects (Actors) in a level.
"""

import pyglet

import pyglet
import pymunk
import itertools

import actor
import camera
import fly
import gamestate
import player
import scene
import scenehandler
import terrain
import util

from util import pushmatrix, draw, interpolator

pymunk_update_t = 1/120.0

class ExploreScene(scene.Scene):
    
    # Initialization
    
    def __init__(self, name, scene_handler, texts):
        super(ExploreScene, self).__init__(name, scene_handler)
        self.texts = texts
        self.text_completions = {}
        self.pieces = []
        for t in self.texts.iterkeys():
            self.text_completions[t] = []
            for i, p in enumerate(t.split('\n\n')):
                self.pieces.append((t, i, self.texts[p]))
                self.text_completions[t].append(0)
        
        self.players = []
        hts = gamestate.TILE_SIZE//2
        self.camera.min_bounds = (gamestate.norm_w//2-hts, gamestate.norm_h//2-hts)
        
        self.space = pymunk.Space()
        self.space._space.elasticIterations = 0
        self.space.set_default_collision_handler(self.collision_events, None, None,
                                                 self.enforce_wall_hugging)
        self.pymunk_accum = 0.0
        
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
        }
        for y, row in enumerate(self.grid):
            for x, char in enumerate(row):
                f = handlers.get(char)
                if f:
                    f(x, y)
        
        self.terrain = terrain.Terrain(self.batch, self.space, self.grid)
        
        for p in self.pieces:
            x, y = self.terrain.random_clear_cell()
            self._make_fly(x, y, p)
        
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
    
    def _make_fly(self, x, y, piece):
        xx, yy = self.place(x, y)
        na = fly.Fly(self, self.batch, xx, yy, piece)
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
        
        if len(arbiter.shapes) != 2:
            return True # Give up
        if 'player' in tags and 'foot' in tags and self.events:
            for p in self.players:
                p.move_x, p.move_y = 0, 0
                p.reset_motion()
                p.update_walk_anim()
            f = [x for x in self.actors.itervalues() if x.kind == 'foot'][0]
            self.remove(f)
            self.handler.go_to("2")
        elif 'player' in tags and 'fly' in tags:
            a, b = arbiter.shapes
            if b.parent.kind == 'player':
                a, b = b, a
            if a.parent.tongue_state != player.TONGUE_IN and not a.parent.target and not b.parent.caught:
                a.parent.catch(b.parent)
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
        
        super(ExploreScene, self).update(dt)
        
        self.camera.position = self.players[0].position
    
