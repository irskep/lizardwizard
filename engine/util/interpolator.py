"""Introspective magic to make anything animate"""

import math

class InterpolatorController(object):
    """Keeps track of the lifecycles of multiple interpolators"""
    def __init__(self):
        super(InterpolatorController, self).__init__()
        self.interpolators = set()
        
        # Shortcut to add a new interpolator
        self.add_interpolator = self.interpolators.add
    
    def update_interpolators(self, dt=0):
        """Update all interpolators and remove those that have completed"""
        to_remove = set()
        for i in self.interpolators:
            i.update(dt)
            if i.complete():
                to_remove.add(i)
        for i in to_remove:
            if i.done_function:
                i.done_function(i)
        self.interpolators -= to_remove
    

class Interpolator(object):
    def __init__(self, host_object, attr_name, end, start=None, 
                 name="value", speed=0.0, duration=0.0,
                 done_function=None):
        self.host_object = host_object
        self.attr_name = attr_name
        self.done_function = done_function
        self.start = start
        if self.start is None:
            self.start = getattr(host_object, attr_name)
        self.end = end
        self.name = name
        self.speed = speed
        self.duration = duration
        self.fix_speed_and_duration()
        self.progress = 0.0
    
    def complete(self):
        return self.progress >= self.duration
    
    def fix_speed_and_duration(self):
        if self.speed == 0.0:
            if self.duration == 0.0:
                self.speed = 100.0
                self.duration = abs((self.start-self.end)/self.speed)
            else:
                self.speed = abs((self.start-self.end)/self.duration)
        elif self.duration == 0.0:
            self.duration = abs((self.start-self.end)/self.speed)
        if self.end < self.start:
            self.speed = -self.speed
    
    def update(self, dt=0):
        self.progress = min(self.progress+dt, self.duration)
    
    def __repr__(self):
        fmt = "Interpolator '%s' on %s.%s from %0.2f to %0.2f taking %0.2f seconds)"
        return fmt % (self.name, str(self.host_object), self.attr_name, 
                      self.start, self.end, self.duration)


class ForeverInterpolator(Interpolator):
    """docstring for ForeverInterpolator"""
    def __init__(self, *args, **kwargs):
        super(ForeverInterpolator, self).__init__(*args, **kwargs)
        self.stop = False
    
    def stop(self):
        self.stop = True
    
    def complete(self):
        return self.stop
        

class LinearInterpolator(Interpolator):
    def __init__(self, *args, **kwargs):
        super(LinearInterpolator, self).__init__(*args, **kwargs)
        self.update(0.0)
    
    def update(self, dt=0):
        super(LinearInterpolator, self).update(dt)
        setattr(self.host_object, self.attr_name, self.start + self.progress*self.speed)
    
    def __repr__(self):
        fmt = "LinearInterpolator '%s' on %s.%s from %0.2f to %0.2f taking %0.2f seconds)"
        return fmt % (self.name, str(self.host_object), self.attr_name, 
                      self.start, self.end, self.duration)

class Linear2DInterpolator(Interpolator):
    def __init__(self, host_object, attr_name, end_tuple, name="position", 
                 start_tuple=None, speed=0.0, duration=0.0, done_function=None):
        if start_tuple is None:
            start_tuple = getattr(host_object, attr_name)
        self.start_tuple = start_tuple
        self.end_tuple = end_tuple
        
        self.speed = speed
        self.duration = duration
        
        diff_tuple = (end_tuple[0] - start_tuple[0], end_tuple[1] - start_tuple[1])
        angle = math.atan2(diff_tuple[1], diff_tuple[0])
        length = math.sqrt(diff_tuple[0] * diff_tuple[0] + diff_tuple[1] * diff_tuple[1])
        
        super(Linear2DInterpolator, self).__init__(host_object, attr_name, 
                                                   end=length, start=0.0, 
                                                   speed=self.speed, 
                                                   name=name, done_function=done_function,
                                                   duration=self.duration)
        
        self.x_speed = self.speed*math.cos(angle)
        self.y_speed = self.speed*math.sin(angle)
        
        self.update(0.0)
    
    def update(self, dt=0):
        super(Linear2DInterpolator, self).update(dt)
        new_tuple = ((self.start_tuple[0] + self.progress*self.x_speed),
                     (self.start_tuple[1] + self.progress*self.y_speed))
        setattr(self.host_object, self.attr_name, new_tuple)
    
    def __repr__(self):
        fmt = "Linear2DInterpolator '%s' on %s.%s from %s to %s taking %0.2f seconds)"
        return fmt % (self.name, str(self.host_object), self.attr_name, 
                      str(self.start_tuple), str(self.end_tuple), self.duration)
    

class JumpInterpolator(Interpolator):
    """Cause the target to 'jump' using a sine wave"""
    
    def __init__(self, host_object, attr_name, height, **kwargs):
        self.base_y = getattr(host_object, attr_name)
        self.height = height
        super(JumpInterpolator, self).__init__(host_object, attr_name, 
                                               start=0.0, end=math.pi, **kwargs)
        self.update(0.0)
    
    def update(self, dt=0):
        super(JumpInterpolator, self).update(dt)
        setattr(self.host_object, self.attr_name, 
                self.base_y + math.sin(self.progress*self.speed)*self.height)
    
    def complete(self):
        if super(JumpInterpolator, self).complete():
            setattr(self.host_object, self.attr_name, self.base_y)
            return True
        else:
            return False
    

class PulseInterpolator(ForeverInterpolator):
    """Pulse on a sine wave"""
    
    def __init__(self, host_object, attr_name, inner, outer, **kwargs):
        self.inner = inner
        self.spread = outer - inner
        super(PulseInterpolator, self).__init__(host_object, attr_name, 
                                               start=0.0, end=math.pi*2, **kwargs)
        self.update(0.0)
    
    def update(self, dt=0):
        self.progress += dt
        setattr(self.host_object, self.attr_name, 
                self.inner + math.sin(self.progress*self.speed)*self.spread)
    

class ForeverLinearInterpolator(ForeverInterpolator):
    def __init__(self, host_object, attr_name, start_val, speed, mod=None, **kwargs):
        super(ForeverLinearInterpolator, self).__init__(host_object, attr_name, 0.0,
                                                        start=start_val, speed=speed, **kwargs)
        self.mod = mod
        self.update(0.0)
    
    def update(self, dt=0):
        self.start += self.speed*dt
        if self.mod:
            self.start = self.start % self.mod
        setattr(self.host_object, self.attr_name, self.start)
    

class FadeInterpolator(Interpolator):
    def __init__(self, host_object, attr_name, rgb=(255,255,255), **kwargs):
        self.rgb = rgb
        super(FadeInterpolator, self).__init__(host_object, attr_name, **kwargs)
        self.update(0.0)
    
    def update(self, dt=0):
        super(FadeInterpolator, self).update(dt)
        if not self.host_object:
            return
        new_val = (self.rgb[0], self.rgb[1], self.rgb[2], int(self.start + self.progress*self.speed))
        setattr(self.host_object, self.attr_name, new_val)
    
    def complete(self):
        if not self.host_object:
            return True
        if super(FadeInterpolator, self).complete():
            setattr(self.host_object, self.attr_name, (self.rgb[0], self.rgb[1], self.rgb[2], int(self.duration*self.speed)))
            return True
        else:
            return False
    
