"""
SUP YO IT'S TIME FOR LUDUM DARE 19 

PUMP-UP QUOTE:
YEAH YEAH YEAH YEAH YEAH YEAH YEAH YEAH YEAH YEAH YEAH YEAH YEAH YEAH YEAH
YEAH YEAH YEAH YEAH YEAH YEAH YEAH YEAH YEAH YEAH YEAH YEAH YEAH YEAH YEAH
YEEEAAAHHH
-Bono
"""

try:
    import psyco
    psyco.full()
    print 'PSYCO ENABLED, GO GO GO!'
except ImportError:
    print 'You should probably install psyco. It runs on Python 2.6 and under.'
    pass

import os
import shutil
import sys
import functools

import pyglet
import pymunk

pyglet.options['debug_gl'] = False

from engine import imagescene
from engine import gamestate
from engine import images
from engine import scenehandler
from engine import util

class GameWindow(pyglet.window.Window):
    """
    Basic customizations to Window, plus configuration.
    """
    def __init__(self):
        if util.settings.fullscreen:
            super(GameWindow,self).__init__(fullscreen=True, vsync=True)
        else:
            super(GameWindow,self).__init__(width=gamestate.norm_w, 
                                                height=gamestate.norm_h, vsync=True)
        self.set_caption(gamestate.name)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.gl.glEnable(pyglet.gl.GL_LINE_SMOOTH)
        
        pymunk.init_pymunk()
        
        gamestate.main_window = self    # Make main window accessible to others.
                                        #   Necessary for convenient event juggling.
        gamestate.init_scale()          # Set up scaling transformations to have
                                        #   a consistent window size
        gamestate.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(gamestate.keys)
        
        self.scene_handler = scenehandler.SceneHandler()
        fs = imagescene.ImageScene(self.scene_handler)
        self.scene_handler.set_first_scene(fs)
        
        pyglet.gl.glClearColor(0.81, 0.357, 0.255, 1.0)
        self.title_image = pyglet.resource.image('game/images/title1.png')
        w, h = self.title_image.width, self.title_image.height
        f = functools.partial(self.title_image.blit, self.width/2-w/2, self.height/2-h/2)
        self.scene_draw = f
        # Load resources or something
        self.finish_title()
        
        self.scene_draw = self.scene_handler.draw
        
        self.fps_display = pyglet.clock.ClockDisplay()
        
        # Schedule drawing and update functions.
        # Draw really only needs 60 FPS, update can be faster.
        pyglet.clock.schedule_interval(self.on_draw, 1/72.0)
        pyglet.clock.schedule_interval(self.scene_handler.update, 1/72.0)
        
        music = False
        if music:
            gamestate.dj = pyglet.media.Player()
            gamestate.dj.eos_action = 'loop'
            gamestate.dj.queue(pyglet.resource.media('game/music.wav', streaming=True))
            gamestate.dj.play()
    
    def finish_title(self):
        # self.scene_draw = self.scene_handler.draw
        # pyglet.gl.glClearColor(0, 0, 0, 1.0)
        # pyglet.gl.glClearColor(0.2, 0.1, 0.05, 1.0)
        pyglet.gl.glClearColor(0.5, 0.3, 0.255, 1.0)
    
    def on_draw(self, dt=0):
        self.clear()
        self.scene_draw()
        self.fps_display.draw()
    
    def on_key_press(self, symbol, modifiers):
        # Override default behavior of escape key quitting
        if symbol == pyglet.window.key.ESCAPE:
            return pyglet.event.EVENT_HANDLED
    

def run_game():
    GameWindow()
    pyglet.app.run()

if __name__ == '__main__':
    run_game()
