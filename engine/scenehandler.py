"""
The scene handler is responsible for transitioning between scenes as well as saving and restoring game state.
"""

import json
import sys
import threading

import pyglet

import actionsequencer
import explorescene
import gamestate
import scene
import util
from util import interpolator

class SceneHandler(actionsequencer.ActionSequencer):
    def __init__(self):
        super(SceneHandler, self).__init__()
        self.scene = None   # Main scene
        self.scenes = []    # Scenes to be drawn
        
        self.controller = interpolator.InterpolatorController()
        self.fade_time = 1.0
        self.blackout_alpha = 0.0
        self.batch = pyglet.graphics.Batch()
        self.fade_sprite = pyglet.sprite.Sprite(pyglet.resource.image('game/images/fade.png'),
                                                0, 0, batch=self.batch)
        self.fade_sprite.opacity = 0.0
        self.fade_sprite_2 = pyglet.sprite.Sprite(pyglet.resource.image('game/images/fade2.png'), 
                                                0, 0, batch=self.batch)
        self.fade_sprite_2.opacity = 0.0
        self.fs = self.fade_sprite
        
        self.next_text_ready = False
        self.next_text = {'error': 'error'}
    
    def set_first_scene(self, scn):
        self.set_scenes(scn)
        self.scene.enter()
    
    def set_scenes(self, *args):
        if args:
            self.scene = args[0]
        else:
            self.scene = None
        self.scenes = args
    
    def __repr__(self):
        return "SceneHandler(scene_object=%s)" % str(self.scene)

    # Called by a scene to load a new scene.
    # If dir is specified a sliding transition is used
    def go_to(self, name=1):
        self.fade_to_explore(name)
    
    def fade_to_explore(self, name):
        self.next_text_ready = False
        def worker():
            self.next_text = util.wiki.text_dicts(min(name, 5))
            self.next_text_ready = True

        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        
        InterpClass = interpolator.LinearInterpolator
        
        def complete_transition(ending_action=None):
            self.scene.enter()
            self.next_action()
        
        def fade_in(ending_action=None):
            # Remove scene
            self.set_scenes(explorescene.ExploreScene(name, self, self.next_text))
            interp = InterpClass(self, 'blackout_alpha', end=0, start=1.0, duration=self.fade_time,
                                done_function=complete_transition)
            self.controller.add_interpolator(interp)
        
        def check_fade_in(dt=0):
            if self.next_text_ready:
                fade_in()
                self.next_text_ready = False
                self.next_text = {'error': 'error'}
            else:
                pyglet.clock.schedule_once(check_fade_in, 0.5)
        
        self.scene.exit()
        interp = InterpClass(self, 'blackout_alpha', end=1.0, start=0, duration=self.fade_time,
                            done_function=check_fade_in)
        self.controller.add_interpolator(interp)
    
    def update(self, dt=0):
        self.controller.update_interpolators(dt)
        for scn in self.scenes:
            scn.update(dt)
    
    def draw(self, dt=0):
        with util.pushmatrix(gamestate.scale):
            for scn in self.scenes:
                scn.draw()
        if self.blackout_alpha > 0.0:
            self.fs.opacity = self.blackout_alpha*255
            self.fs.set_position(0, 0)
            self.batch.draw()
    
