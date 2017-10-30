#!/usr/bin/env python

from distutils.core import setup

setup(name='el4000',
      version='0.1',
      description='Energy Logger 4000 utility',
      author='Peter Wu',
      author_email='peter@lekensteyn.nl',
      url='https://github.com/Lekensteyn/el4000/',
      packages=['el4000'],
      package_dir={'el4000': 'src/el4000'},
      scripts=['scripts/el4000']
     )
