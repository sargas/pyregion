from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest
from astropy.coordinates import Angle, Longitude, Latitude, SkyCoord
from astropy import units as u
from numpy.testing import assert_allclose
from .. import Circle, Ellipse

""" Test initalization and other aspects of Shape objects """


def test_circle():
    lon, lat = Longitude('2640', unit='arcminute'), Latitude('2d')
    sc = SkyCoord(lon, lat)
    radius_angle = Angle('4"')
    c = Circle(sc, radius_angle, "icrs")
    assert c.origin.data.lon == lon
    assert c.origin.data.lat == lat
    assert c.origin.frame.name == sc.frame.name
    assert c.radius == radius_angle
    assert c.coord_list == [44, 2, 4/3600]
    assert c.coord_format == "icrs"
    assert c.name == 'circle'


def test_circle_errors():
    with pytest.raises(ValueError):
        Circle.from_coordlist([0], "galactic")

    with pytest.raises(ValueError):
        Circle.from_coordlist([1, 2, 3, 4], "galactic")


@pytest.mark.parametrize(('proplist', 'lon', 'lat', 'radius', 'system',
                          'coordlist'), [
    (['44d', '2d', '4"'], Angle('44d'), Angle('2d'), Angle('4"'), 'icrs',
     [44, 2, 4/3600]),
    (['1d', '0.5d', '40'], Angle('1d'), Angle('.5d'), 40*u.pixel, 'galactic',
     [1, 0.5, 40]),
    (['42', '5', '4"'], 42*u.pixel, 5*u.pixel, Angle('4"'), 'fk4',
     [42, 5, 4/3600]),
])
def test_circle_from_coordlist(proplist, lon, lat, radius, system, coordlist):
    c = Circle.from_coordlist(proplist, system)
    if lon.unit.is_equivalent(u.radian):
        assert c.origin.data.lon == lon
        assert c.origin.data.lat == lat
        assert c.origin.frame.name == system
    else:
        assert c.origin.data.x == lon
        assert c.origin.data.y == lat
        assert c.origin.frame.name == 'image'

    assert c.radius == radius
    assert_allclose(c.coord_list, coordlist)
    assert c.name == 'circle'


def test_ellipse():
    lon, lat = Longitude('2640', unit='arcminute'), Latitude('2d')
    sc = SkyCoord(lon, lat)
    distance_angles = [Angle("1'"), Angle("20d"), Angle("5d"), Angle("1'")]
    rot_angle = Angle('4"')
    c = Ellipse(sc, [(distance_angles[0], distance_angles[1])],
                rot_angle, "icrs")
    assert c.origin.data.lon == lon
    assert c.origin.data.lat == lat
    assert c.angle == rot_angle
    assert c.coord_list == [44, 2, 1/60, 20, 4/3600]


def test_ellipse_from_coordlist():
    c2 = Ellipse.from_coordlist(['44', '2', '1"', '20d', '5d', '1"', '50'],
                                'fk5')
    assert c2.origin.X == 44*u.pixel
    assert c2.origin.Y == 2*u.pixel
    assert len(c2.levels) == 2
    assert c2.levels[0] == (Angle(1, unit=u.arcsecond), Angle('20d'))
    assert c2.levels[1] == (Angle('5d'), Angle(1, unit=u.arcsecond))
    assert c2.angle == Angle(50, unit=u.degree)
    assert c2.coord_list == [44, 2, 1/3600, 20, 5, 1/3600, 50]


def test_ellipse_errors():
    with pytest.raises(ValueError):
        Ellipse.from_coordlist([], "icrs")

    with pytest.raises(ValueError):
        Ellipse.from_coordlist([1, 2, 3, 4, 5, 6], "icrs")
