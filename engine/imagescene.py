import pyglet

import gamestate
import scene

import images
from explorescene import ExploreScene

class ImageScene(scene.Scene):
    def __init__(self, *args, **kwargs):
        super(ImageScene, self).__init__(None, *args, **kwargs)
        self.sprite = pyglet.sprite.Sprite(images.comics[0], 0, 0)
        self.pos = 0
    
    def enter(self):
        print 'enter'
        gamestate.main_window.push_handlers(self)
    
    def exit(self): 
        print 'exit'   
        gamestate.main_window.pop_handlers()
    
    def on_mouse_press(self, *args, **kwargs):
        self.next()
    
    def on_key_press(self, *args, **kwargs):
        self.next()
    
    def next(self):
        self.pos += 1
        if self.pos < len(images.comics):
            self.sprite.image = images.comics[self.pos]
        else:
            self.handler.go_to(1)
    
    def draw(self):
        self.sprite.draw()
        