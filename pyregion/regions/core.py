from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from astropy.coordinates import SphericalRepresentation
from astropy import units as u
from ._parsing_helpers import _parse_angle, _parse_coordinate, _parse_size


__all__ = ['Shape', 'Circle', 'Ellipse']


class Properties:
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


class Shape:
    def __init__(self, coord_system, properties={}):
        self.coord_system = coord_system
        self.properties = Properties(properties)

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


def _get_xy(skycoord):
    if skycoord.representation == SphericalRepresentation:
        return skycoord.data.lon.degree, skycoord.data.lat.degree
    else:
        return skycoord.data.x.value, skycoord.data.y.value


def _get_angle(angle):
    if angle.unit.is_equivalent(u.radian):
        return angle.to(u.degree).value
    else:
        return angle.value


class Circle(Shape):
    def __init__(self, origin, radius, coord_system, properties={}):
        Shape.__init__(self, coord_system, properties)

        self.origin = origin
        self.radius = radius

    @staticmethod
    def from_coordlist(coordlist, coord_system, properties={}):
        if len(coordlist) != 3:
            raise ValueError(("Circle created with %s, expected an origin" +
                              " and radius") % repr(coordlist))
        lon, lat, radius = coordlist
        origin = _parse_coordinate(lon, lat, coord_system)
        radius = _parse_size(radius)
        return Circle(origin, radius, properties=properties,
                      coord_system=coord_system)

    @property
    def coord_list(self):
        lon, lat = _get_xy(self.origin)
        radius = _get_angle(self.radius)

        return [lon, lat, radius]


class Ellipse(Shape):
    def __init__(self, origin, levels, angle, coord_system, properties={}):
        Shape.__init__(self, coord_system, properties)

        self.origin = origin
        self.levels = levels
        self.angle = angle

    @property
    def coord_list(self):
        lon, lat = _get_xy(self.origin)
        radii = list(r.to(u.degree).value
                     for pair in self.levels
                     for r in pair)
        angle = _get_angle(self.angle)
        return [lon, lat] + radii + [angle]

    @staticmethod
    def from_coordlist(coordlist, coord_system, properties={}):
        if len(coordlist) < 5 or len(coordlist) % 2 == 0:
            raise ValueError(("Ellipse created with %s, expected an origin" +
                              ", multiple semi-major/semi-minor axes, and " +
                              "an angle of rotation") % repr(coordlist))

        origin = _parse_coordinate(coordlist[0], coordlist[1], coord_system)
        angle = _parse_angle(coordlist[-1])

        for i in range(2, len(coordlist) - 1):
            coordlist[i] = _parse_size(coordlist[i])
        levels = list(zip(coordlist[2:-1:2], coordlist[3:-1:2]))

        return Ellipse(origin, levels, angle, properties=properties,
                       coord_system=coord_system)
