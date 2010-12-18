import noise
import pyglet
import itertools
import pymunk

import gamestate

class Terrain(object):
    def __init__(self, batch, space, grid):
        super(Terrain, self).__init__()
        self.batch = batch
        self.space = space
        self.grid = grid
        
        self.body = pymunk.Body(pymunk.inf, pymunk.inf)
        
        self.vls = set()
        self.objs = set()
        
        self.width = len(self.grid[0])
        self.height = len(self.grid)
        
        self.fill_color = [0.2, 0.1, 0.05, 1.0]
        # self.fill_color = [0.5, 0.3, 0.255, 1.0]
        self.line_color = [1.0, 1.0, 1.0, 1.0]
        
        self.instantiate_lines()
    
    def instantiate_lines(self):
        lines = []
        triangles = []
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
        return self.grid[y][x] == 'X'
