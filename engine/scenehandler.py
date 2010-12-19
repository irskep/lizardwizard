"""
The scene handler is responsible for transitioning between scenes as well as saving and restoring game state.
"""

import json
import sys

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
        self.fs = self.fade_sprite_2
    
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
    def go_to(self, next_scene_func=None, immediate=False, alt=True):
            
        if next_scene_func is None:
            sys.exit(0)
        else:
            if immediate:
                self.scene.exit()
                self.set_scenes(next_scene_func())
                self.scene.enter()
            else:
                if alt:
                    self.fs = self.fade_sprite
                else:
                    self.fs = self.fade_sprite_2
                self.fade_to(next_scene_func)
    
    def fade_to(self, next_scene_func):
        InterpClass = interpolator.LinearInterpolator
        
        def complete_transition(ending_action=None):
            self.scene.enter()
            self.next_action()
        
        def fade_in(ending_action=None):
            # Remove scene
            self.set_scenes(next_scene_func())
            interp = InterpClass(self, 'blackout_alpha', end=0, start=1.0, duration=self.fade_time,
                                done_function=complete_transition)
            self.controller.add_interpolator(interp)
        self.scene.exit()
        interp = InterpClass(self, 'blackout_alpha', end=1.0, start=0, duration=self.fade_time,
                            done_function=fade_in)
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
    
