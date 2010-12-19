import pyglet

import scene

class ImageScene(scene.Scene):
    def __init__(self, image, next, *args, **kwargs):
        super(ImageScene, self).__init__(*args, **kwargs)
        self.img_batch = pyglet.graphics.Batch()
        self.sprite = pyglet.sprite.Sprite(image, 0, 0)
    
    def draw(self):
        self.image.bli
        