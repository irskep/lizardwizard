fullscreen = False
resources_path = 'resources'

from pyglet.window import key

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
TONGUE = 4

controls_map = {
    1: {
        UP: key.UP,
        RIGHT: key.RIGHT,
        DOWN: key.DOWN,
        LEFT: key.LEFT,
        TONGUE: key.SPACE,
    },
    2: {
        UP: key.W,
        RIGHT: key.D,
        DOWN: key.S,
        LEFT: key.A,
        TONGUE: key.LSHIFT,
    },
}
