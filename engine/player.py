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
            controls_map[settings.RIGHT]: self.zero_x_right,
            controls_map[settings.LEFT]: self.zero_x_left,
            controls_map[settings.UP]: self.zero_y_up,
            controls_map[settings.DOWN]: self.zero_y_down,
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
    
    def zero_x_left(self):
        if self.move_x == 1: return
        self.body.velocity[0] = 0
        self.move_x = 0
    
    def zero_x_right(self):
        if self.move_x == -1: return
        self.body.velocity[0] = 0
        self.move_x = 0
    
    def zero_y_down(self):
        if self.move_y == 1: return
        self.body.velocity[1] = 0
        self.move_y = 0
    
    def zero_y_up(self):
        if self.move_y == -1: return
        self.body.velocity[1] = 0
        self.move_y = 0
    
    def move_left(self):
        self.body.velocity[0] = -gamestate.MOVE_SPEED
        self.move_x = -1
    
    def move_right(self):
        self.body.velocity[0] = gamestate.MOVE_SPEED
        self.move_x = 1
    
    def move_up(self):
        self.body.velocity[1] = gamestate.MOVE_SPEED
        self.move_y = 1
    
    def move_down(self):
        self.body.velocity[1] = -gamestate.MOVE_SPEED
        self.move_y = -1
    
