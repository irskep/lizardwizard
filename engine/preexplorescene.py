import pyglet

import gamestate
import scene

import images

class PreExploreScene(scene.Scene):
    def __init__(self, name, scene_handler, texts):
        super(PreExploreScene, self).__init__(name, scene_handler)
        self.sprite = pyglet.sprite.Sprite(images.preexplore, 0, 0)
        self.pos = 0
        self.texts = texts
    
    def enter(self):
        gamestate.main_window.push_handlers(self)
    
    def exit(self):
        gamestate.main_window.pop_handlers()
    
    def on_mouse_press(self, *args, **kwargs):
        self.handler.begin_explore(self.name, self.texts)
    
    def draw(self):
        self.sprite.draw()
    
