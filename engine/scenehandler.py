"""
The scene handler is responsible for transitioning between scenes as well as saving and restoring game state.
"""

import json
import sys

import pyglet

import actionsequencer
import gamestate
import scene
import util
from util import interpolator

class SceneHandler(actionsequencer.ActionSequencer):
    def __init__(self, first_scene):
        super(SceneHandler, self).__init__()
        self.scene = None   # Main scene
        self.scenes = []    # Scenes to be drawn
        
        self.controller = interpolator.InterpolatorController()
        self.fade_time = 1.0
        self.blackout_alpha = 0.0
        self.batch = pyglet.graphics.Batch()
        
        self.set_first_scene(scene.Scene(first_scene, self))
    
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
    def go_to(self, next_scene):
        if next_scene is None:
            sys.exit(0)
        else:
            self.fade_to(next_scene)
    
    def fade_to(self, next_scene):
        InterpClass = interpolator.LinearInterpolator
        def fade_out(ending_action=None):
            self.scene.exit()
            interp = InterpClass(self, 'blackout_alpha', end=1.0, start=0, duration=self.fade_time,
                                done_function=self.next_action)
            self.controller.add_interpolator(interp)
        
        def complete_transition(ending_action=None):
            self.scene.enter()
            self.next_action()
        
        def fade_in(ending_action=None):
            # Remove scene
            self.scene.exit()
            new_scene = scene.Scene(next_scene, self)
            self.set_scenes(new_scene)
            interp = InterpClass(self, 'blackout_alpha', end=0, start=1.0, duration=self.fade_time,
                                done_function=complete_transition)
            self.controller.add_interpolator(interp)
        
        self.simple_sequence(fade_out, fade_in)
    
    def update(self, dt=0):
        self.controller.update_interpolators(dt)
        for scn in self.scenes:
            scn.update(dt)
    
    def draw(self, dt=0):
        with util.pushmatrix(gamestate.scale):
            for scn in self.scenes:
                scn.draw()
        if self.blackout_alpha > 0.0:
            util.draw.set_color(0, 0, 0, self.blackout_alpha)
        self.batch.draw()
    
