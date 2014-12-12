from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from astropy.coordinates import SkyCoord, SphericalRepresentation
from astropy import units as u
from ._parsing_helpers import _parse_coordinate, _parse_size


__all__ = ['Shape', 'Circle', 'Ellipse']


def parse(s):
    pass


class Shape:
    def __init__(self, comment, coord_system):
        self.comment = comment
        self.coord_system = coord_system

    @property
    def coord_format(self):
        """ Old name kept for compatibility """
        return self.coord_system


class Circle(Shape):
    def __init__(self, origin, radius, comment, coord_system):
        Shape.__init__(self, comment, coord_system)

        self.origin = origin
        self.radius = radius

    @staticmethod
    def from_coordlist(coordlist, comment, coord_system):
        if len(coordlist) != 3:
            raise ValueError(("Circle created with %s, expected an origin" +
                              " and radius") % repr(coordlist))
        lon, lat, radius = coordlist
        origin = _parse_coordinate(lon, lat, coord_system)
        radius = _parse_size(radius)
        return Circle(origin, radius, comment=comment,
                      coord_system=coord_system)

    @property
    def coord_list(self):
        if self.origin.representation == SphericalRepresentation:
            lon, lat = self.origin.data.lon.degree, self.origin.data.lat.degree
        else:
            lon, lat = self.origin.data.x.value, self.origin.data.y.value

        if self.radius.unit.is_equivalent(u.radian):
            radius = self.radius.to(u.degree).value
        else:
            radius = self.radius.value

        return [lon, lat, radius]


class Ellipse(Shape):
    def __init__(self, coordlist, comment, coord_format):
        Shape.__init__(self, comment, coord_format)

        if len(coordlist) < 5 or len(coordlist) % 2 == 0:
            raise ValueError(("Ellipse created with %s, expected an origin" +
                              ", multiple semi-major/semi-minor axes, and " +
                              "an angle of rotation") % repr(coordlist))

        self.origin = SkyCoord(coordlist[0], coordlist[1], frame=coord_format)
        self.angle = coordlist[-1]
        self.levels = list(zip(coordlist[2:-1:2], coordlist[3:-1:2]))

    @property
    def coord_list(self):
        lon, lat = self.origin.data.lon.degree, self.origin.data.lat.degree
        radii = list(r.to(u.degree).value
                     for pair in self.levels
                     for r in pair)
        return [lon, lat] + radii + [self.angle.to(u.degree).value]


_LIST_OF_SHAPES = [Circle, Ellipse]
