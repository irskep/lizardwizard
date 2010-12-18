import pyglet, functools

import gamestate

class apply_camera(object):
    def __init__(self, c):
        self.camera = c
    
    def __enter__(self):
        self.camera.apply()
    
    def __exit__(self, type, value, traceback):
        self.camera.unapply()
    

class Camera(object):
    def __init__(self, min_bounds=None, max_bounds=None, speed=50000.0, dict_repr=None):
        self.min_bounds = min_bounds or gamestate.camera_min
        self.max_bounds = max_bounds or gamestate.camera_max
        self._x, self._y = self.min_bounds
        dict_repr = dict_repr or {}
    
    def _set_position(self, p):
        self._x, self._y = self.constrain_point(*p)
    
    position = property(lambda self: (self._x, self._y), _set_position)
    
    def _set_x(self, x):
        self._set_position((x, self._y))
    
    def _set_y(self, y):
        self._set_position((self._x, y))
    
    x = property(lambda self: self._x, _set_x)
    y = property(lambda self: self._y, _set_y)
    
    def constrain_point(self, x, y):
        x = min(max(x, self.min_bounds[0]), self.max_bounds[0])
        y = min(max(y, self.min_bounds[1]), self.max_bounds[1])
        return (x, y)
    
    def apply(self):
        pyglet.gl.glPushMatrix()
        pyglet.gl.glTranslatef(-self.position[0]+gamestate.norm_w//2, 
                               -self.position[1]+gamestate.norm_h//2,0)
    
    def unapply(self):
        pyglet.gl.glPopMatrix()
    
    def mouse_to_canvas(self, x, y):
        return (x/gamestate.scale_factor + self.position[0]-gamestate.norm_w//2, 
                y/gamestate.scale_factor + self.position[1]-gamestate.norm_h//2)

    # returns a position on the screen based on a point in the game world (i.e. where a point is relative to the camera)
    def world_to_screen_position(self, x, y):
        return ( (x/gamestate.scale_factor) - (self.position[0]-gamestate.norm_w//2), 
                (y/gamestate.scale_factor) - (self.position[1]-gamestate.norm_h//2))
    
