"""
Usage (Mac):
    python setup.py py2app
"""

import sys

mainscript = 'LizardWizard.py'

OPTIONS = dict(
    argv_emulation=True,
    frameworks=['pymunk/libchipmunk.dylib', 'libavbin.dylib'],
    plist = dict(CFBundleIconFile='lizardwizard.icns'), 
    # PyRuntimeLocations=['/Library/Frameworks/Python.framework/Versions/2.7/Python']
    #, '/System/Library/Frameworks/Python.framework/Versions/Current/Python'])
)

if sys.platform == 'darwin':
     from setuptools import setup
     extra_options = dict(
         setup_requires=['py2app'],
         app=[mainscript],
         options={'py2app': OPTIONS},
     )

setup(
    name='Lizard Wizard',
    data_files=['engine','game', 'lizardwizard.icns'],
                # 'noise', 'yaml', 'pyglet', 'pymunk'],
    **extra_options
)