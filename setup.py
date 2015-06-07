#!/usr/bin/env python

from setuptools import setup

setup(name='tagdog',
      version='0.2',
      description='Tag media files',
      author='Albert Pham',
      author_email='the.sk89q@gmail.com',
      url='https://github.com/sk89q/TagDog',
      install_requires=[
          'titlecase',
          'mutagen',
          'pyechonest'
      ],
      scripts=['tagdog.py']
      )