from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from astropy.coordinates import SkyCoord
from astropy import units as u


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
    def __init__(self, lon, lat, radius, comment, coord_system):
        Shape.__init__(self, comment, coord_system)

        self.origin = SkyCoord(lon, lat, frame=coord_system)
        self.radius = radius

    @staticmethod
    def from_coordlist(coordlist, comment, coord_system):
        if len(coordlist) != 3:
            raise ValueError(("Circle created with %s, expected an origin" +
                              " and radius") % repr(coordlist))
        return Circle(*coordlist, comment=comment, coord_system=coord_system)

    @property
    def coord_list(self):
        lon, lat = self.origin.data.lon.degree, self.origin.data.lat.degree
        return [lon, lat, self.radius.to(u.degree).value]


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
