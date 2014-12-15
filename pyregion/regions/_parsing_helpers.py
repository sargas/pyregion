from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .frames import Image
from astropy.coordinates import Angle, SkyCoord, SphericalRepresentation
from astropy import units as u


class DS9ParsingException(Exception):
    pass


class DS9InconsistentArguments(Exception):
    pass


class Argument:
    def __init__(self, name=None):
        self.name = name


class SkyCoordArgument(Argument):
    def to_coords(self, skycoord):
        if skycoord.representation == SphericalRepresentation:
            return skycoord.data.lon.degree, skycoord.data.lat.degree
        else:
            return skycoord.data.x.value, skycoord.data.y.value

    def _parse_position(self, position, odd):
        if 'd' in position or 'h' in position:
            return Angle(position)

        if position[-1] == 'r':
            return Angle(position[:-1], unit=u.radian)

        if ':' in position:
            colon_split = position.split(':')
            colon_split = tuple(float(x) for x in colon_split)

            if odd:
                return Angle(colon_split, unit=u.hourangle)
            else:
                return Angle(colon_split, unit=u.degree)

        if position[-1] in ['p', 'i']:
            return float(position[:-1])*u.pixel
        else:
            return float(position)*u.pixel

    def from_coords(self, coords, coord_system):
        if len(coords) < 2:
            raise DS9InconsistentArguments('Expected atleast two arguments'
                                           ' for a coordinate, but only see'
                                           '{}'.format(coords))
        odd_coordinate = self._parse_position(coords.popleft(), True)
        even_coordinate = self._parse_position(coords.popleft(), False)

        if odd_coordinate.unit.is_equivalent(u.radian) and\
           even_coordinate.unit.is_equivalent(u.radian):
            return SkyCoord(odd_coordinate, even_coordinate,
                            frame=coord_system)
        elif (odd_coordinate.unit.is_equivalent(u.pixel) and
              even_coordinate.unit.is_equivalent(u.pixel)):
            return SkyCoord(odd_coordinate, even_coordinate, frame=Image)
        else:
            raise DS9ParsingException(
                "Inconsistent units found when parsing coordinate."
                "Obtained {} and {}".format(odd_coordinate, even_coordinate))


class SizeArgument(Argument):
    def to_coords(self, angle):
        if angle.unit.is_equivalent(u.radian):
            return [angle.to(u.degree).value]
        else:
            return [angle.value]

    def from_coords(self, coords, coord_system):
        if len(coords) == 0:
            raise DS9InconsistentArguments('Expected a size argument')
        size = coords.popleft()
        if 'd' in size or '"' in size or "'" in size:
            return Angle(size)

        if size[-1] == 'r':
            return Angle(size[:-1], unit=u.radian)

        if size[-1] in ['p', 'i']:
            return float(size[:-1])*u.pixel
        else:
            return float(size)*u.pixel


class AngleArgument(Argument):
    # Need to explicitly define this for Py2k compat
    # to_coords = SizeArgument.to_coords
    def to_coords(self, angle):
        return SizeArgument().to_coords(angle)

    def from_coords(self, coords, coord_system):
        if len(coords) == 0:
            raise DS9InconsistentArguments('Expected an angle argument')
        return Angle(coords.popleft(), unit=u.degree)


class RepeatedArgument(Argument):
    def __init__(self, arguments, name=None):
        self.name = name
        self.arguments = arguments

    def from_coords(self, coords, coord_system):
        new_coords = []
        while(len(coords) >= len(self.arguments)):
            new_coords.append(tuple(_.from_coords(coords, coord_system)
                                    for _ in self.arguments))

        if len(new_coords) == 0:
            raise DS9InconsistentArguments("Expected repeated numbers of "
                                           "arguments for {}, but didn't "
                                           "parse any in {}".format(self.name,
                                                                    coords))
        return new_coords

    def to_coords(self, tuple_list):
        coords = []
        for tuple_item in tuple_list:
            for argument, coord in zip(self.arguments, tuple_item):
                coords.extend(argument.to_coords(coord))

        return coords
