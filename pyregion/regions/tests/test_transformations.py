""" Test coordinate system transformations """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from astropy.coordinates import Angle, ICRS, FK5, SkyCoord, Longitude, Latitude
from astropy import units as u
from .. import Circle
from ..frames import Image


def test_no_change():
    test_input = Circle(SkyCoord(5*u.pixel, 2*u.pixel, frame=Image),
                        1*u.pixel,
                        coord_system=Image)
    test_result = test_input.transform_to(Image)
    assert test_input.origin.separation(test_result.origin) == 0
    assert test_input.radius == test_result.radius
    assert test_result.origin.frame.name == Image.name
    assert test_result.coord_system.name == Image.name

    test_input = Circle(SkyCoord('1d 2d', frame=ICRS),
                        Angle('5d'),
                        coord_system=ICRS)
    test_result = test_input.transform_to(ICRS)
    assert test_input.origin.separation(test_result.origin) == 0
    assert test_input.radius == test_result.radius
    assert test_result.origin.frame.name == ICRS.name
    assert test_result.coord_system.name == ICRS.name


def test_sky_transformations():
    test_input = Circle(SkyCoord('1d 2d', frame=FK5),
                        Angle('5d'),
                        coord_system=FK5)
    test_result = test_input.transform_to(ICRS)
    assert test_input.origin.separation(test_result.origin) == 0
    assert test_result.origin.frame.name == ICRS.name
    assert test_result.coord_system.name == ICRS.name
    assert test_result.origin.data.lon == Longitude('0.9999934443434741d')
    assert test_result.origin.data.lat == Latitude('1.99999756908023d')
    assert test_result.radius == Angle('5d')
