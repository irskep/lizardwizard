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

import pyglet
import pymunk

pyglet.options['debug_gl'] = False

from engine import gamestate
from engine import scenehandler
from engine import util

class GameWindow(pyglet.window.Window):
    """
    Basic customizations to Window, plus configuration.
    """
    def __init__(self, first_level, reset_save=False):
        if util.settings.fullscreen:
            super(GameWindow,self).__init__(fullscreen=True, vsync=True)
        else:
            super(GameWindow,self).__init__(width=gamestate.norm_w, 
                                                height=gamestate.norm_h, vsync=False)
        self.set_caption(gamestate.name)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.gl.glEnable(pyglet.gl.GL_LINE_SMOOTH)
        
        pymunk.init_pymunk()
        
        if reset_save:
            try:
                shutil.rmtree(os.path.join(gamestate.save_path, "autosave"))
            except OSError:
                pass    # Directory didn't exist but we don't care
        
        gamestate.main_window = self    # Make main window accessible to others.
                                        #   Necessary for convenient event juggling.
        gamestate.init_scale()          # Set up scaling transformations to have
                                        #   a consistent window size
        
        self.scene_handler = scenehandler.SceneHandler(first_level)
        
        self.fps_display = pyglet.clock.ClockDisplay()
        
        # Schedule drawing and update functions.
        # Draw really only needs 60 FPS, update can be faster.
        pyglet.clock.schedule_interval(self.on_draw, 1/72.0)
        pyglet.clock.schedule_interval(self.scene_handler.update, 1/72.0)
    
    def on_draw(self, dt=0):
        self.clear()
        self.scene_handler.draw()
        self.fps_display.draw()
    
    def on_key_press(self, symbol, modifiers):
        # Override default behavior of escape key quitting
        if symbol == pyglet.window.key.ESCAPE:
            return pyglet.event.EVENT_HANDLED
    

def run_game():
    if len(sys.argv) == 2:
        main_window = GameWindow(reset_save=True, first_level=sys.argv[1])
    else:
        main_window = GameWindow(reset_save=True, first_level="1")
    pyglet.app.run()

if __name__ == '__main__':
    run_game()