import functools
import pyglet
import pymunk

import actor

from util import settings

class Player(object):
    def __init__(self, scn, number, x=640, y=25):
        super(Player, self).__init__()
        self.scene = scn
        self.number = number
        self.actor = actor.Actor(self.scene, self.scene.batch, kind='player', x=0, y=0)
        
        controls_map = settings.controls_map[self.number]
        self.press_controls = {
            controls_map[settings.RIGHT]: None,
            controls_map[settings.LEFT]: None,
            controls_map[settings.FIRE]: None,
        }
        self.release_controls = {
            controls_map[settings.RIGHT]: None,
            controls_map[settings.LEFT]: None
        }
    
    def on_key_press(self, symbol, modifiers):
        f = self.press_controls.get(symbol, None)
        if f:
            f()
            return pyglet.event.EVENT_HANDLED
    
    def on_key_release(self, symbol, modifiers):
        f = self.release_controls.get(symbol, None)
        if f:
            f()
            return pyglet.event.EVENT_HANDLED
    
