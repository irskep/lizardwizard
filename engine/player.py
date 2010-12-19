import math
import functools
import pyglet
import pymunk

import actor
import gamestate

from util import settings

TONGUE_IN = 0
TONGUE_EXITING = 1
TONGUE_ENTERING = 2

TONGUE_SIZE = 3

GROUP = 1

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
            controls_map[settings.TONGUE]: self.tongue_out,
        }
        self.release_controls = {
            controls_map[settings.RIGHT]: self.zero_x_right,
            controls_map[settings.LEFT]: self.zero_x_left,
            controls_map[settings.UP]: self.zero_y_up,
            controls_map[settings.DOWN]: self.zero_y_down,
            controls_map[settings.TONGUE]: self.tongue_in,
        }
        
        self.collision_circles = (
            (gamestate.TILE_SIZE*0.4, (0, 0)), 
            (5, (0, 13)), 
            (3, (0, -21))
        )
        
        self.tongue_vl = None
        self.tongue_body = None
        self.tongue_progress = 0.0
        self.tongue_shapes = []
        self.tongue_state = TONGUE_IN
        
        self.move_target = (self.body.position[0], self.body.position[1])
    
    def delete(self):
        super(Player, self).delete()
        self.delete_tongue()
    
    def init_physics(self, x, y):
        # mass = 100
        # moment = pymunk.moment_for_circle(mass, 0, gamestate.TILE_SIZE*0.4)
        inf = 2**32-1
        mass, moment = inf, inf
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, y)
        
        for size, offset in ((gamestate.TILE_SIZE*0.4, (0, 0)), (5, (0, 15)), (5, (0, -15))):
            s = pymunk.Circle(self.body, size, offset)
            s.group = GROUP
            s.parent = self
            s.elasticity = 0.0
            self.shapes.append(s)
        self.scene.space.add(self.body, *self.shapes)
    
    def update(self, dt=0):
        super(Player, self).update(dt)
        if self.tongue_state == TONGUE_EXITING:
            self.tongue_progress += dt
        if self.tongue_progress > .3:
            self.tongue_state = TONGUE_ENTERING
        if self.tongue_state == TONGUE_ENTERING:
            self.tongue_progress -= dt
            if self.tongue_progress <= 0.0:
                self.delete_tongue()
        if self.tongue_progress:
            a = -(self.sprite.rotation-90)*actor.DEG_TO_RAD
            c, s = math.cos(a), math.sin(a)
            bx, by = self.body.position[0], self.body.position[1]
            p = self.tongue_progress
            self.tongue_body.position = (bx+c*(20+1000*p), by+s*(20+1000*p))
            self.tongue_vl.vertices = self.vertices_for_tongue()
    
    def on_mouse_motion(self, x, y, dx, dy):
        self.rotate_to_face(*self.scene.local_to_world(x, y))
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.rotate_to_face(*self.scene.local_to_world(x, y))
    
    def rotate_to_face(self, x, y):
        a = math.atan2(y-self.body.position[1], x-self.body.position[0])
        self.move_x = math.cos(a)
        self.move_y = math.sin(a)
        self.body.angle = a
        self.reset_motion()
    
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
    
    def tongue_out(self):
        if self.tongue_state == TONGUE_IN:
            self.tongue_progress = 0.0
            self.tongue_state = TONGUE_EXITING
            self.init_tongue_physics()
            self.tongue_vl = self.batch.add(6, pyglet.gl.GL_TRIANGLES, None,
                ('v2f/dynamic', self.vertices_for_tongue()),
                ('c4B/static', [255,0,0,255]*6))
    
    def tongue_in(self):
        self.delete_tongue
    
    def init_tongue_physics(self):
        mass = 5
        moment = pymunk.moment_for_circle(mass, 0, TONGUE_SIZE)
        self.tongue_body = pymunk.Body(mass, moment)
        
        velocity = 400.0
        a = -(self.sprite.rotation-90)*actor.DEG_TO_RAD
        c, s = math.cos(a), math.sin(a)
        self.tongue_body.position = (self.body.position[0]+c*20,
                                     self.body.position[1]+s*20)
        
        self.tongue_shapes = []
        sh = pymunk.Circle(self.tongue_body, 5, (0, 0))
        sh.group = GROUP
        sh.parent = self
        sh.elasticity = 0.0
        self.tongue_shapes.append(sh)
        
        self.scene.space.add(self.tongue_body, *self.tongue_shapes)
    
    def delete_tongue(self):
        if self.tongue_body:
            for s in self.tongue_shapes:
                self.scene.space.remove(s)
            del self.tongue_body
            self.tongue_body = None
            self.tongue_shapes = []
            self.tongue_vl.delete()
            self.tongue_state = TONGUE_IN
            self.tongue_progress = 0.0
    
    def vertices_for_tongue(self):
        a = -(self.sprite.rotation-90)*actor.DEG_TO_RAD
        ox, oy = math.cos(a-1.57)*TONGUE_SIZE, math.sin(a-1.57)*TONGUE_SIZE
        ox2, oy2 = math.cos(a)*20, math.sin(a)*20
        
        x1, y1 = self.body.position[0] + ox + ox2, self.body.position[1] + oy + oy2
        x2, y2 = self.body.position[0] - ox + ox2, self.body.position[1] - oy + oy2
        x3, y3 = self.tongue_body.position[0] + ox, self.tongue_body.position[1] + oy
        x4, y4 = self.tongue_body.position[0] - ox, self.tongue_body.position[1] - oy
        return [x1, y1, x2, y2, x3, y3,
                x3, y3, x4, y4, x2, y2]
    
    def zero_x_left(self):
        if self.move_x == 1: return
        self.body.velocity[0] = 0
        self.move_x = 0
        self.stop_moving()
    
    def zero_x_right(self):
        if self.move_x == -1: return
        self.body.velocity[0] = 0
        self.move_x = 0
        self.stop_moving()
    
    def zero_y_down(self):
        if self.move_y == 1: return
        self.body.velocity[1] = 0
        self.move_y = 0
        self.stop_moving()
    
    def zero_y_up(self):
        if self.move_y == -1: return
        self.body.velocity[1] = 0
        self.move_y = 0
        self.stop_moving()
    
    def move_left(self):
        self.body.velocity[0] = -gamestate.MOVE_SPEED
        self.move_x = -1
        self.start_moving()
    
    def move_right(self):
        self.body.velocity[0] = gamestate.MOVE_SPEED
        self.move_x = 1
        self.start_moving()
    
    def move_up(self):
        self.body.velocity[1] = gamestate.MOVE_SPEED
        self.move_y = 1
        self.start_moving()
    
    def move_down(self):
        self.body.velocity[1] = -gamestate.MOVE_SPEED
        self.move_y = -1
        self.start_moving()
    
