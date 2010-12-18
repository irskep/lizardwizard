import noise
import pyglet
import itertools
import pymunk

import gamestate

class Terrain(object):
    def __init__(self, batch, space, dict_repr):
        super(Terrain, self).__init__()
        self.batch = batch
        self.space = space
        self.dict_repr = dict_repr
        
        self.body = pymunk.Body(pymunk.inf, pymunk.inf)
        
        self.vls = set()
        self.objs = set()
        
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
        c = self.fill_color
        self.batch.add(n, pyglet.gl.GL_POINTS, None,
                      ('v2f/static', points),
                      ('c4f/static', c*n))
    
    def instantiate_lines(self):
        lines = []
        triangles = []
        t = self.dict_repr['threshold']
        ts = gamestate.TILE_SIZE
        hts = ts//2
        wall = self.wall
        
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
                        lines.append((col_ix*ts-hts, row_ix*ts-hts, 
                                      col_ix*ts-hts, row_ix*ts+hts))
                    if (r and not (u or d)) or lur or urd or rdl:
                        lines.append((col_ix*ts+hts, row_ix*ts-hts, 
                                      col_ix*ts+hts, row_ix*ts+hts))
                    if (d and not (l or r)) or dlu or urd or rdl:
                        lines.append((col_ix*ts-hts, row_ix*ts-hts, 
                                      col_ix*ts+hts, row_ix*ts-hts))
                    if (u and not (l or r)) or dlu or lur or urd:
                        lines.append((col_ix*ts-hts, row_ix*ts+hts, 
                                      col_ix*ts+hts, row_ix*ts+hts))
                    if l and u and not dlu and not lur:
                        p = (col_ix*ts-hts, row_ix*ts-hts, 
                             col_ix*ts+hts, row_ix*ts+hts)
                        lines.append(p)
                        triangles.append(p + (col_ix*ts-hts, row_ix*ts+hts))
                    if l and d and not dlu and not rdl:
                        p = (col_ix*ts+hts, row_ix*ts-hts, 
                             col_ix*ts-hts, row_ix*ts+hts)
                        lines.append(p)
                        triangles.append(p + (col_ix*ts-hts, row_ix*ts-hts))
                    if r and u and not lur and not urd:
                        p = (col_ix*ts+hts, row_ix*ts-hts, 
                             col_ix*ts-hts, row_ix*ts+hts)
                        lines.append(p)
                        triangles.append(p + (col_ix*ts+hts, row_ix*ts+hts))
                    if r and d and not urd and not rdl:
                        p = (col_ix*ts-hts, row_ix*ts-hts, 
                             col_ix*ts+hts, row_ix*ts+hts)
                        lines.append(p)
                        triangles.append(p + (col_ix*ts+hts, row_ix*ts-hts))
        n = len(lines)*2
        c = self.line_color
        coords = list(itertools.chain(*lines))
        vl = self.batch.add(n, pyglet.gl.GL_LINES, None,
                            ('v2f/static', coords), 
                            ('c4f/static', c*n))
        self.vls.add(vl)
        nt = len(triangles)*3
        ct = self.fill_color
        coordst = list(itertools.chain(*triangles))
        vlt = self.batch.add(nt, pyglet.gl.GL_TRIANGLES, None,
                             ('v2f/static', coordst), 
                             ('c4f/static', ct*nt))
        self.vls.add(vlt)
        self.instantiate_quads()
        
        self.instantiate_physics(lines)
    
    def instantiate_quads(self):
        triangles = []
        ts = gamestate.TILE_SIZE
        hts = ts//2
        wall = self.wall
        for col_ix in xrange(0, self.width):
            row_ix = 0
            box_start = 0
            box_end = -1
            while row_ix < self.height:
                if wall(col_ix, row_ix):
                    if box_end == -1:
                        box_start = row_ix
                    box_end = row_ix
                else:
                    if box_end >= 0:
                        triangles.extend((
                            col_ix*ts-hts, box_start*ts-hts,
                            col_ix*ts+hts, box_start*ts-hts,
                            col_ix*ts+hts, box_end*ts+hts,
                            col_ix*ts-hts, box_end*ts+hts,
                            col_ix*ts+hts, box_end*ts+hts,
                            col_ix*ts-hts, box_start*ts-hts,
                        ))
                        box_end = -1
                if box_end >= 0:
                    triangles.extend((
                        col_ix*ts-hts, box_start*ts-hts,
                        col_ix*ts+hts, box_start*ts-hts,
                        col_ix*ts+hts, box_end*ts+hts,
                        col_ix*ts-hts, box_end*ts+hts,
                        col_ix*ts+hts, box_end*ts+hts,
                        col_ix*ts-hts, box_start*ts-hts,
                    ))
                row_ix += 1
        nt = len(triangles)/2
        ct = self.fill_color
        vlt = self.batch.add(nt, pyglet.gl.GL_TRIANGLES, None,
                             ('v2f/static', triangles), 
                             ('c4f/static', ct*nt))
        self.vls.add(vlt)
    
    def instantiate_physics(self, lines):
        for x1, y1, x2, y2 in lines:
            l = pymunk.Segment(self.body, (x1, y1), (x2, y2), 1.0)
            self.space.add(l)
            self.objs.add(l)
    
    def wall(self, x, y):
        in_bounds = (0 < x < self.width-1) and (0 < y < self.height-1)
        return (in_bounds and self.grid[x][y] < self.dict_repr['threshold']) or not in_bounds
    
    def place(self, x, y):
        return x*gamestate.TILE_SIZE, y*gamestate.TILE_SIZE
    
    width = property(lambda self: self.dict_repr['size'][0])
    height = property(lambda self: self.dict_repr['size'][1])
    fill_color = property(lambda self: self.dict_repr['fill'])
    line_color = property(lambda self: self.dict_repr['stroke'])
    
    pixelwidth = property(lambda self: self.dict_repr['size'][0]*gamestate.TILE_SIZE)
    pixelheight = property(lambda self: self.dict_repr['size'][1]*gamestate.TILE_SIZE)
