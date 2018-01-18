#!/usr/bin/env py
import os
from setuptools import setup
LINK_NAME = 'README'
if not os.path.exists(LINK_NAME):
    os.symlink('.'.join([LINK_NAME, 'md']), LINK_NAME)
setup(
    setup_requires=['pbr'],
    pbr=True,
)
