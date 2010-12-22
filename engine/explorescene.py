"""
The Scene class manages all objects (Actors) in a level.
"""

import pyglet
import pymunk
import itertools
import functools

import actor
import camera
import fly
import gamestate
import images
import player
import scene
import scenehandler
import terrain
import util

from util import pushmatrix, draw, interpolator

NUM_LEVELS = 4

pymunk_update_t = 1/120.0

class ExploreScene(scene.Scene):
    
    # Initialization
    
    def __init__(self, name, scene_handler, texts):
        # texts = util.wiki.text_dicts(min(self.name, 5))
        super(ExploreScene, self).__init__(name, scene_handler)
        self.texts = texts
        
        self.text_completions = {}
        self.pieces = []
        self.hud_batch = pyglet.graphics.Batch()
        self.hud_objects = set()
        
        lx = 10
        for t in self.texts.iterkeys():
            self.text_completions[t] = []
            
            l = pyglet.text.Label(t, x=lx, y=gamestate.norm_h-10, 
                                  anchor_x='left', anchor_y='top',
                                  batch=self.hud_batch, group=pyglet.graphics.OrderedGroup(3))
            w = max(l.content_width, 200)
            x1, y1 = l.x-5, l.y-l.content_height-5
            x2, y2 = x1, l.y+5
            x3, y3 = l.x+w+5, y2
            x4, y4 = x3, y1
            self.hud_batch.add(8, pyglet.gl.GL_LINES, pyglet.graphics.OrderedGroup(2),
                               ('v2f/static', (x1, y1, x2, y2, 
                                               x2, y2, x3, y3, 
                                               x3, y3, x4, y4,
                                               x4, y4, x1, y1)),
                               ('c4B/static', (255,255,255,255)*8))
            for i, p in enumerate(self.texts[t]):
                self.pieces.append((t, i, p, l))
                self.text_completions[t].append(0)
            lx += w + 30
        self.update_hud()
        
        self.players = []
        hts = gamestate.TILE_SIZE//2
        self.camera.min_bounds = (gamestate.norm_w//2-hts, gamestate.norm_h//2-hts)
        
        self.space = pymunk.Space()
        self.space._space.elasticIterations = 0
        self.space.resize_static_hash(20)
        self.space.resize_active_hash(20)
        self.space.set_default_collision_handler(self.collision_events, None, None,
                                                 self.enforce_wall_hugging)
        self.pymunk_accum = 0.0
        
        self.load()
        
        self.topright_label = pyglet.text.Label('', multiline=True, font_size=12,
                                                x=gamestate.norm_w-410, y=gamestate.norm_h-10,
                                                anchor_x='left', anchor_y='top',
                                                width=400, batch=self.hud_batch,
                                                group=pyglet.graphics.OrderedGroup(2),
                                                color=[255,255,255,255])
        
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
        with pyglet.resource.file('game/levels/%d.txt' % ((self.name-1) % NUM_LEVELS)) as f:
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
        self.pixelwidth = self.width*gamestate.TILE_SIZE
        self.pixelheight = self.height*gamestate.TILE_SIZE
        self.camera.max_bounds = (self.pixelwidth-gamestate.norm_w//2-hts,
                                  self.pixelheight-gamestate.norm_h//2-hts,)
    
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
        return (x/gamestate.scale_factor+self.camera.x-gamestate.norm_w//2,
                y/gamestate.scale_factor+self.camera.y-gamestate.norm_h//2)
    
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
        if 'player' in tags and 'fly' in tags:
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
    
    def check_for_next(self, dt=0):
        def all_true(l):
            for item in l:
                if item not in (1, True):
                    return False
            return True
        if all_true([all_true(l) for l in self.text_completions.itervalues()]):
            self.handler.go_to(self.name+1)
    
    def bump(self, piece):
        self.topright_label.begin_update()
        self.topright_label.text = self.texts[piece[0]][piece[1]]
        self.topright_label.end_update()
        def fade_out(dt=0):
            interp = interpolator.FadeInterpolator(self.topright_label, 'color', duration=0.5,
                                                    start=255, end=0, 
                                                    done_function=self.check_for_next)
            self.interp.add_interpolator(interp)
        
        def wait(dt=0):
            pyglet.clock.schedule_once(fade_out, 3.0)
        
        interp = interpolator.FadeInterpolator(self.topright_label, 'color', duration=0.5,
                                                start=0, end=255, done_function=wait)
        for i in self.interp.interpolators:
            if i.host_object == self.topright_label:
                i.progress = 10000000000
        self.interp.add_interpolator(interp)
        self.text_completions[piece[0]][piece[1]] = 1
        self.update_hud()
    
    def update_hud(self):
        for title, i, txt, l in self.pieces:
            c = self.text_completions[title]
            if c[i] == 1:
                w = (max(l.content_width, 200)+10)/float(len(c))
                x = l.x-5 + w*i
                x1, y1 = x, l.y-l.content_height-5
                x2, y2 = x1, l.y+5
                x3, y3 = x+w, y2
                x4, y4 = x3, y1
                self.hud_batch.add(4, pyglet.gl.GL_QUADS, pyglet.graphics.OrderedGroup(2),
                                   ('v2f/static', (x1, y1, x2, y2, 
                                                   x3, y3, x4, y4)),
                                   ('c4B/static', (50,80,128,255)*4))
    
    def update(self, dt=0):
        if self.paused: 
            return
        self.pymunk_accum += dt
        while self.pymunk_accum >= pymunk_update_t:
            self.space.step(pymunk_update_t)
            self.pymunk_accum -= pymunk_update_t
        
        super(ExploreScene, self).update(dt)
        
        if self.players:
            self.camera.position = self.players[0].position
    
    def draw(self, dt=0):
        with camera.apply_camera(self.camera):
            images.background.blit_tiled(0, 0, 0, self.pixelwidth, self.pixelheight)
            self.batch.draw()
        self.hud_batch.draw()
    
