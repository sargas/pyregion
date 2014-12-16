from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import deque
from ._parsing_helpers import AngleArgument, DS9InconsistentArguments
from ._parsing_helpers import IntegerArgument
from ._parsing_helpers import RepeatedArgument, SizeArgument, SkyCoordArgument


__all__ = ['Shape', 'Box', 'Circle', 'Ellipse', 'Panda', 'Polygon']


class Properties(object):
    # defaults from http://ds9.si.edu/ref/region.html
    _default_properties = {
        'text': '',
        'color': 'green',
        'font': 'helvetica 10 normal roman',
        'select': '1',
        'edit': '1',
        'move': '1',
        'delete': '1',
        'highlite': '1',
        'include': '1',
        'fixed': '0',
        'tag': []
    }

    def __init__(self, properties={}):
        self._properties = self._default_properties.copy()
        self._properties.update(properties)

    def __getattr__(self, name):
        BOOLEAN_PROPERTIES = ['select', 'highlight', 'dash', 'fixed', 'edit',
                              'move', 'rotate', 'delete']
        if name in BOOLEAN_PROPERTIES:
                return self._properties[name] == '1'
        elif name in self._properties:
            return self._properties[name]

        raise AttributeError("No property named {} defined".format(name))

    @property
    def is_source(self):
        return self._properties.get('sourcebackground', 'source') == 'source'

    @property
    def is_background(self):
        return not self.is_source


class Shape(object):
    def __init__(self, *args, **kwargs):
        self.coord_system = kwargs['coord_system']
        self.properties = Properties(kwargs.get('properties', {}))
        for argument, value in zip(self.arguments, args):
            setattr(self, argument.name, value)

    @property
    def coord_format(self):
        """ Old name kept for compatibility """
        return self.coord_system

    @property
    def name(self):
        return type(self).__name__.lower()

    @property
    def tag(self):
        return self.properties.tag

    @classmethod
    def from_coordlist(cls, coordlist, coord_system, properties={}):

        coords = deque(coordlist)
        args = [argument.from_coords(coords, coord_system)
                for argument in cls.arguments]

        if len(coords) > 0:
            raise DS9InconsistentArguments(
                "{} created with too many coordinates: {}"
                .format(repr(cls), coordlist))

        return cls(*args, coord_system=coord_system, properties=properties)

    @property
    def coord_list(self):
        coordlist = []
        for argument in self.arguments:
            coordlist.extend(argument.to_coords(getattr(self, argument.name)))

        return coordlist


class Circle(Shape):
    arguments = [SkyCoordArgument('origin'), SizeArgument('radius')]


class Ellipse(Shape):
    arguments = [SkyCoordArgument('origin'),
                 RepeatedArgument([SizeArgument(), SizeArgument()], 'levels'),
                 AngleArgument('angle')]


class Box(Shape):
    arguments = [SkyCoordArgument('origin'),
                 RepeatedArgument([SizeArgument(), SizeArgument()], 'levels'),
                 AngleArgument('angle')]

    @property
    def width(self):
        print(self.levels)
        return self.levels[0][0]

    @property
    def height(self):
        return self.levels[0][1]


class Polygon(Shape):
    arguments = [RepeatedArgument([SkyCoordArgument()], 'points')]


class Panda(Shape):
    arguments = [SkyCoordArgument('origin'),
                 AngleArgument('start_angle'),
                 AngleArgument('stop_angle'),
                 IntegerArgument('nangle'),
                 SizeArgument('inner'),
                 SizeArgument('outer'),
                 IntegerArgument('nradius'),
                 ]
