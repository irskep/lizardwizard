import noise
import pyglet
import itertools

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
        
        def nf(x, y):
            if 0 < x < self.width-1 and 0 < y < self.height-1:
                return int((noise.pnoise2((x+x_off)*scale, (y+y_off)*scale, 
                                           repeatx=freq, repeaty=freq) + 1.0) * 100)
            else:
                return 0
        
        self.grid = [[nf(x, y) for y in range(self.height)] for x in range(self.width)]
        self.instantiate_lines()
    
    def instantiate_points(self):
        points = []
        t = self.dict_repr['threshold']
        ts = gamestate.TILE_SIZE
        for col_ix, col in enumerate(self.grid):
            for row_ix, cell in enumerate(col):
                if cell < t:
                    points.extend((col_ix*ts+ts//2, row_ix*ts+ts//2))
        n = len(points)//2
        c = (0.81, 0.357, 0.255, 1.0)
        self.batch.add(n, pyglet.gl.GL_POINTS, None,
                      ('v2f/static', points),
                      ('c4f/static', c*n))
    
    def instantiate_lines(self):
        lines = []
        t = self.dict_repr['threshold']
        ts = gamestate.TILE_SIZE
        def wall(x, y):
            in_bounds = (0 < x < self.width-1) and (0 < y < self.height-1)
            return (in_bounds and self.grid[x][y] < t) or not in_bounds
        
        for row_ix in range(1, self.height-1):
            for col_ix in range(1, self.width-1):
                if not wall(col_ix, row_ix):
                    l = wall(col_ix-1, row_ix)
                    r = wall(col_ix+1, row_ix)
                    d = wall(col_ix, row_ix-1)
                    u = wall(col_ix, row_ix+1)
                    dlu = (l and u and d)
                    lur = (l and u and r)
                    urd = (u and r and d)
                    rdl = (r and d and l)
                    if (l and not (u or d)) or dlu or lur or rdl:
                        lines.append((col_ix*ts-ts//2, row_ix*ts-ts//2, 
                                      col_ix*ts-ts//2, row_ix*ts+ts//2))
                    if (r and not (u or d)) or lur or urd or rdl:
                        lines.append((col_ix*ts+ts//2, row_ix*ts-ts//2, 
                                      col_ix*ts+ts//2, row_ix*ts+ts//2))
                    if (d and not (l or r)) or dlu or urd or rdl:
                        lines.append((col_ix*ts-ts//2, row_ix*ts-ts//2, 
                                      col_ix*ts+ts//2, row_ix*ts-ts//2))
                    if (u and not (l or r)) or dlu or lur or urd:
                        lines.append((col_ix*ts-ts//2, row_ix*ts+ts//2, 
                                      col_ix*ts+ts//2, row_ix*ts+ts//2))
                    if l and u and not dlu and not lur:
                        lines.append((col_ix*ts-ts//2, row_ix*ts-ts//2, 
                                      col_ix*ts+ts//2, row_ix*ts+ts//2))
                    if l and d and not dlu and not rdl:
                        lines.append((col_ix*ts+ts//2, row_ix*ts-ts//2, 
                                      col_ix*ts-ts//2, row_ix*ts+ts//2))
                    if r and u and not lur and not urd:
                        lines.append((col_ix*ts+ts//2, row_ix*ts-ts//2, 
                                      col_ix*ts-ts//2, row_ix*ts+ts//2))
                    if r and d and not urd and not rdl:
                        lines.append((col_ix*ts-ts//2, row_ix*ts-ts//2, 
                                      col_ix*ts+ts//2, row_ix*ts+ts//2))
        n = len(lines)*2
        c = (0.81, 0.357, 0.255, 1.0)
        coords = list(itertools.chain(*lines))
        self.batch.add(n, pyglet.gl.GL_LINES, None,
                       ('v2f/static', coords), 
                       ('c4f/static', c*n))
        
    
    width = property(lambda self: self.dict_repr['size'][0])
    height = property(lambda self: self.dict_repr['size'][1])
