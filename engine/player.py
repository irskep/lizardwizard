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
        
        self.keys = pyglet.window.key.KeyStateHandler()
        gamestate.main_window.push_handlers(self.keys)
        
        controls_map = settings.controls_map[self.number]
        self.k = {
            settings.LEFT: controls_map[settings.LEFT],
            settings.RIGHT: controls_map[settings.RIGHT],
            settings.UP: controls_map[settings.UP],
            settings.DOWN: controls_map[settings.DOWN],
            settings.TONGUE: controls_map[settings.TONGUE],
        }
        self.press_controls = {
            controls_map[settings.TONGUE]: self.tongue_out,
        }
        self.release_controls = {
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
        self.target = None
    
    def delete(self):
        super(Player, self).delete()
        self.delete_tongue()
        gamestate.main_window.pop_handlers()
    
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
        self.body.angular_velocity = 0
        super(Player, self).update(dt)
        
        a = math.atan2(self.move_target[1]-self.body.position[1],
                       self.move_target[0]-self.body.position[0])
        self.move_x, self.move_y = 0, 0
        ba = a
        if self.keys[self.k[settings.LEFT]]:
            ba += 1.57
            self.move_x += math.cos(a+1.57)
            self.move_y += math.sin(a+1.57)
        elif self.keys[self.k[settings.RIGHT]]:
            ba -= 1.57
            self.move_x += math.cos(a-1.57)
            self.move_y += math.sin(a-1.57)
        elif self.keys[self.k[settings.UP]]:
            self.move_x += math.cos(a)
            self.move_y += math.sin(a)
        elif self.keys[self.k[settings.DOWN]]:
            ba += 3.14
            self.move_x -= math.cos(a)
            self.move_y -= math.sin(a)
        
        last_ba = self.body.angle
        
        diff = ba - last_ba
        while diff > math.pi:
            diff -= math.pi*2.0
        while diff < -math.pi:
            diff += math.pi*2.0
        while abs(diff) > 0.5:
            diff /= 2.0
        self.body.angle = last_ba + diff
        self.reset_motion()
        self.update_walk_anim()
        
        self.update_tongue(dt)
    
    def on_mouse_press(self, x, y, button, modifiers):
        self.tongue_out()
    
    def on_mouse_motion(self, x, y, dx, dy):
        self.move_target = self.scene.local_to_world(x, y)
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.move_target = self.scene.local_to_world(x, y)
    
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
    
    
    # Tongue
    
    def catch(self, target):
        self.target = target
        target.caught = True
        self.scene.space.remove(target.body)
        self.tongue_state = TONGUE_ENTERING
        self.scene.text_completions[target.piece[0]][1] = 1
        self.scene.update_hud()
    
    def update_tongue(self, dt):
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
            if self.target:
                self.target.body.position = self.tongue_body.position
    
    def tongue_out(self):
        if self.tongue_state == TONGUE_IN:
            self.tongue_progress = 0.0
            self.tongue_state = TONGUE_EXITING
            self.init_tongue_physics()
            self.tongue_vl = self.batch.add(6, pyglet.gl.GL_TRIANGLES, 
                pyglet.graphics.OrderedGroup(-1),
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
            if self.target:
                # self.target.body = None
                self.scene.remove(self.target)
                self.target = None
    
    def vertices_for_tongue(self):
        a = -(self.sprite.rotation-90)*actor.DEG_TO_RAD
        ox, oy = math.cos(a-1.57)*TONGUE_SIZE, math.sin(a-1.57)*TONGUE_SIZE
        ox2, oy2 = math.cos(a)*20, math.sin(a)*20
        
        x1, y1 = self.body.position[0] + ox + ox2, self.body.position[1] + oy + oy2
        x2, y2 = self.body.position[0] - ox + ox2, self.body.position[1] - oy + oy2
        x3, y3 = self.tongue_body.position[0] + ox, self.tongue_body.position[1] + oy
        x4, y4 = self.tongue_body.position[0] - ox, self.tongue_body.position[1] - oy
        return [x1, y1, x2, y2, x3, y3,
                x2, y2, x3, y3, x4, y4]
    
