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
        
        self.tl1 = pyglet.text.Label(
            "Articles to find:",
            x=30, y=gamestate.norm_h, anchor_x='left', anchor_y='top',
            color=(213,218,160,255),
            font_name='Fortunaschwein', font_size=64,
            multiline=False
        )
        self.tl2 = pyglet.text.Label(
            '\n'.join(self.texts.keys()),
            x=30, y=gamestate.norm_h-120, anchor_x='left', anchor_y='top',
            color=(213,218,160,255), width=gamestate.norm_w,
            font_name='Fortunaschwein', font_size=42,
            multiline=True,
        )
    
    def enter(self):
        gamestate.main_window.push_handlers(self)
    
    def exit(self):
        gamestate.main_window.pop_handlers()
    
    def on_mouse_press(self, *args, **kwargs):
        self.handler.begin_explore(self.name, self.texts)
    
    def draw(self):
        self.sprite.draw()
        self.tl1.draw()
        self.tl2.draw()
    
