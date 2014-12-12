from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .frames import Image
from astropy.coordinates import Angle, SkyCoord
from astropy import units as u


class DS9ParsingException(Exception):
    pass


def _parse_position(position, odd):
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


def _parse_coordinate(odd_coordinate, even_coordinate, coord_system):
    odd_coordinate = _parse_position(odd_coordinate, True)
    even_coordinate = _parse_position(even_coordinate, False)

    if odd_coordinate.unit.is_equivalent(u.radian) and\
       even_coordinate.unit.is_equivalent(u.radian):
        return SkyCoord(odd_coordinate, even_coordinate, frame=coord_system)
    elif (odd_coordinate.unit.is_equivalent(u.pixel) and
          even_coordinate.unit.is_equivalent(u.pixel)):
        return SkyCoord(odd_coordinate, even_coordinate, frame=Image)
    else:
        raise DS9ParsingException(
            "Inconsistent units found when parsing coordinate."
            "Obtained {} and {}".format(odd_coordinate, even_coordinate))


def _parse_size(size):
    if 'd' in size or '"' in size or "'" in size:
        return Angle(size)

    if size[-1] == 'r':
        return Angle(size[:-1], unit=u.radian)

    if size[-1] in ['p', 'i']:
        return float(size[:-1])*u.pixel
    else:
        return float(size)*u.pixel
