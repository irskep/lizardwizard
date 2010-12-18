import functools
import json
import os
import pyglet
import yaml

# Functional

def first(list_to_search, condition_to_satisfy):
    """Return first item in a list for which condition_to_satisfy(item) returns True"""
    for item in list_to_search:
        if condition_to_satisfy(item):
            return item
    return None

def frange(start,end=None,step=None):
    """A range function that can accept float increments
    (from http://www.daniweb.com/code/snippet263626.html)"""
    if end==None:
        end=start
        start=0.0
    if step==None:step=1.0
    L=[]
    n=float(start)
    if end>start:
        while n<end:
            L.append(n)
            n+=step
        return L
    elif end<start:
        while n>end:
            L.append(n)
            n-=step
        return L

class pushmatrix(object):
    def __init__(self, gl_func, *args, **kwargs):
        super(pushmatrix, self).__init__()
        self.gl_func = gl_func
        self.args = args
        self.kwargs = kwargs
    
    def __enter__(self):
        pyglet.gl.glPushMatrix()
        self.gl_func(*self.args, **self.kwargs)
    
    def __exit__(self, type, value, traceback):
        pyglet.gl.glPopMatrix()
    

# Conventions

yaml_cache = {}
def load_yaml(*path):
    path = respath('game', *list(path[:-1]) + ["%s.yaml" % path[-1]])
    if not yaml_cache.has_key(path):
        with pyglet.resource.file(path, 'r') as f:
            yaml_cache[path] = yaml.load(f)
    return yaml_cache[path]

def save_yaml(val, *path):
    path = respath('game', *list(path[:-1]) + ["%s.yaml" % path[-1]])
    yaml_cache[path] = val
    with pyglet.resource.file(path, 'w') as f:
        yaml.dump(val, f)

def respath(*args):
    return '/'.join(args)

def respath_func_with_base_path(*args):
    return functools.partial(respath, *args)

def mkdir_if_absent(path):
    if not os.path.exists(path):
        os.mkdir(path)

def load_json(path):
    with open('%s.json' % path, 'r') as f:
        return json.load(f)

def save_json(data, path):
    """Save data to path. Appends .json automatically."""
    with open("%s.json" % path, 'w') as f:
        json.dump(data, f, indent=4)

# Convenience and global use

def load_sprite(path, *args, **kwargs):
    loaded_image = pyglet.resource.image(respath(*path))
    return pyglet.sprite.Sprite(loaded_image, *args, **kwargs)

def image_alpha_at_point(img, x, y):
    x, y = int(x), int(y)
    pixel_data = img.get_image_data().get_data('RGBA',img.width*4)
    pos = y * img.width * 4 + x * 4
    
    if pos+3 < len(pixel_data):
        try:
            return pixel_data[pos+3]/255.0
        except TypeError:
            return ord(pixel_data[pos+3])/255.0
    else:
        return 0

# Easy access if you just import util
import draw
import interpolator
import settings
