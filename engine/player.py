import functools
import pyglet
import pymunk

import actor
import gamestate

from util import settings

class Player(actor.Actor):
    def __init__(self, scn, batch, number, x=640, y=25):
        super(Player, self).__init__(scn, batch, kind='player', x=x, y=y)
        self.number = number
        
        controls_map = settings.controls_map[self.number]
        self.press_controls = {
            controls_map[settings.RIGHT]: self.move_right,
            controls_map[settings.LEFT]: self.move_left,
            controls_map[settings.UP]: self.move_up,
            controls_map[settings.DOWN]: self.move_down,
        }
        self.release_controls = {
            controls_map[settings.RIGHT]: self.zero_x,
            controls_map[settings.LEFT]: self.zero_x,
            controls_map[settings.UP]: self.zero_y,
            controls_map[settings.DOWN]: self.zero_y,
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
    
    def zero_x(self):
        self.vx = 0
    
    def zero_y(self):
        self.vy = 0
    
    def move_left(self):
        self.vx = -gamestate.MOVE_SPEED
    
    def move_right(self):
        self.vx = gamestate.MOVE_SPEED
    
    def move_up(self):
        self.vy = gamestate.MOVE_SPEED
    
    def move_down(self):
        self.vy = -gamestate.MOVE_SPEED
    
