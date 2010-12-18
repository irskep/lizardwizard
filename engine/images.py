import pyglet
import itertools

walk_sequences = {
    'player': [pyglet.resource.image('game/images/player_walk_%d.png' % f) for f in (1, 2)]
}

# The Ministry of Silly Walks
walks = {
    'player': pyglet.image.Animation.from_image_sequence(walk_sequences['player'], 0.06, True)
}

sits = {
    'player': pyglet.resource.image('game/images/player_sit.png')
}

for img in itertools.chain(walks.itervalues(), sits.itervalues()):
    try:
        img.anchor_x = img.width//2
        img.anchor_y = img.height//2
    except AttributeError:
        for f in img.frames:
            f.image.anchor_x = f.image.width//2
            f.image.anchor_y = f.image.height//2