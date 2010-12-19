import sys
import noise
import random

octaves = 1

x_off, y_off = random.randint(0,1024), random.randint(0,1024)


freq=1024
scale = 0.1
t = 90

width = 100
height = 100

def nf(x, y):
    if 0 < x < width-1 and 0 < y < height-1:
        return int((noise.pnoise2((x+x_off)*scale, (y+y_off)*scale, 
                                   repeatx=freq, repeaty=freq) + 1.0) * 100)
    else:
        return 0

def char(x, y):
    in_bounds = (0 < x < width-1) and (0 < y < height-1)
    if (in_bounds and nf(x, y) < t) or not in_bounds:
        return 'X'
    else:
        return '.'

grid = [[char(x, y) for x in range(width)] for y in range(height)]

with open(sys.argv[1], 'w') as f:
    f.write('\n'.join(' '.join(row) for row in grid))
