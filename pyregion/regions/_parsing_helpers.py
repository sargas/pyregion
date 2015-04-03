from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from astropy.coordinates import Angle, SkyCoord, SphericalRepresentation
from astropy import units as u
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales


class DS9ParsingException(Exception):
    """Parsing exception for DS9/CIAO Region files"""
    pass


class DS9InconsistentArguments(Exception):
    """Exception for shapes specified with incorrect arguments"""
    pass


class Argument(object):
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
            raise DS9InconsistentArguments('Expected at least two arguments'
                                           ' for a coordinate, but only see'
                                           '{}'.format(coords))
        odd_coordinate = self._parse_position(coords.popleft(), True)
        even_coordinate = self._parse_position(coords.popleft(), False)

        if odd_coordinate.unit.is_equivalent(even_coordinate.unit):
            return SkyCoord(odd_coordinate, even_coordinate,
                            frame=coord_system)
        else:
            raise DS9ParsingException(
                "Inconsistent units found when parsing coordinate."
                "Obtained {} and {}".format(odd_coordinate, even_coordinate))

    def transform_to(self, skycoord, old_frame, new_frame):
        return skycoord.transform_to(new_frame)


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

    def transform_to(self, angle, old_frame, new_frame):
        if hasattr(new_frame, 'fits_header') and angle.unit == u.pixel:
            # from pixel to pixel (TODO?)
            return angle

        elif hasattr(new_frame, 'fits_header') and angle.unit != u.pixel:
            # from WCS to pixel frame
            w = WCS(new_frame.fits_header)
            return angle.value * u.pixel / proj_plane_pixel_scales(w)[0]

        elif angle.unit == u.pixel and not hasattr(new_frame, 'fits_header'):
            # from pixel to WCS
            w = WCS(old_frame.fits_header)
            return angle.value * u.degree * proj_plane_pixel_scales(w)[0]

        elif angle.unit != u.pixel and not hasattr(new_frame, 'fits_header'):
            # from wcs to wcs
            # TODO handle different WCS
            return angle


class AngleArgument(Argument):
    # Need to explicitly define this for Py2k compat
    # to_coords = SizeArgument.to_coords
    def to_coords(self, angle):
        return SizeArgument().to_coords(angle)

    def from_coords(self, coords, coord_system):
        if len(coords) == 0:
            raise DS9InconsistentArguments('Expected an angle argument')
        return Angle(coords.popleft(), unit=u.degree)

    def transform_to(self, angle, old_frame, new_frame):
        from ..wcs_helper import _estimate_angle
        new_is_pixel = hasattr(new_frame, 'fits_header')
        old_is_pixel = hasattr(old_frame, 'fits_header')

        if new_is_pixel and old_is_pixel:
            # Angles don't change between pixel frames
            return angle

        elif not old_is_pixel and new_is_pixel:
            # from WCS to pixel frame
            w = WCS(new_frame.fits_header)
            origin = SkyCoord.from_pixel(new_frame.fits_header['NAXIS1']/2,
                                         new_frame.fits_header['NAXIS2']/2,
                                         w, 1)

            return Angle(_estimate_angle(angle.degree, origin, w),
                         unit=u.degree)

        elif old_is_pixel and not new_is_pixel:
            # from pixel frame to WCS
            w = WCS(old_frame.fits_header)
            origin = SkyCoord.from_pixel(old_frame.fits_header['NAXIS1']/2,
                                         old_frame.fits_header['NAXIS2']/2,
                                         w, 1)

            return Angle(_estimate_angle(angle.degree, origin, w,
                                         otherway=True),
                         unit=u.degree)

        elif not (new_is_pixel or old_is_pixel):
            # from wcs to wcs
            # TODO: WCS frames that are rotated from another
            return angle


class RepeatedArgument(Argument):
    def __init__(self, arguments, name=None):
        Argument.__init__(self, name)
        self.arguments = arguments

    def from_coords(self, coords, coord_system):
        new_coords = []
        while len(coords) >= len(self.arguments):
            if len(self.arguments) == 1:
                new_coords.append(self.arguments[0].from_coords(
                    coords, coord_system))
            else:
                new_coords.append(tuple(_.from_coords(coords, coord_system)
                                        for _ in self.arguments))

        if len(new_coords) == 0:
            raise DS9InconsistentArguments("Expected repeated numbers of "
                                           "arguments for {}, but didn't "
                                           "parse any in {}".format(self.name,
                                                                    coords))
        return new_coords

    def to_coords(self, coords):
        new_coords = []

        if len(self.arguments) == 1:
            for coord in coords:
                new_coords.extend(self.arguments[0].to_coords(coord))
        else:
            for tuple_item in coords:
                for argument, coord in zip(self.arguments, tuple_item):
                    new_coords.extend(argument.to_coords(coord))

        return new_coords

    def transform_to(self, attributes, old_frame, new_frame):
        new_attributes = []
        attributes = list(attributes)
        while len(attributes) > 0:
            new_attributes.append(tuple(
                argument.transform_to(attribute, old_frame, new_frame)
                for argument, attribute in
                zip(self.arguments, attributes.pop(0))))

        return new_attributes


class IntegerArgument(Argument):
    def from_coords(self, integer, coord_system):
        value = integer.popleft()
        try:
            return int(value)
        except ValueError as e:
            raise DS9InconsistentArguments('Obtained {} when expecting an'
                                           ' integer'.format(integer), e)

    def to_coords(self, coord):
        return [coord]

    def transform_to(self, integer, old_frame, new_frame):
        return integer
