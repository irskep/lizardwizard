import sys
import noise
import pyglet
import gamestate

class Terrain(object):
    def __init__(self, batch, dict_repr):
        super(Terrain, self).__init__()
        self.batch = batch
        self.dict_repr = dict_repr
        
        octaves = 1
        
        x_off, y_off = self.dict_repr['position']
        
        freq=1024
        scale = 0.1
        
        nf = lambda x, y: int((noise.pnoise2(
                        (x+x_off)*scale, (y+y_off)*scale, repeatx=freq, repeaty=freq) + 1.0) * 100)
        self.grid = [[nf(x, y) for y in range(self.height)] for x in range(self.width)]
        print self.grid
        self.instantiate()
    
    def instantiate(self):
        points = []
        t = self.dict_repr['threshold']
        ts = gamestate.TILE_SIZE
        for col_ix, col in enumerate(self.grid):
            for row_ix, cell in enumerate(col):
                if cell < t:
                    points.extend((col_ix*ts+ts/2, row_ix*ts+ts/2))
        n = len(points)/2
        c = (0.81, 0.357, 0.255, 1.0)
        self.batch.add(n, pyglet.gl.GL_POINTS, None,
                      ('v2f/static', points), ('c4f/dynamic', c*n))
        
    
    width = property(lambda self: self.dict_repr['size'][0])
    height = property(lambda self: self.dict_repr['size'][1])
