from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest
from astropy.coordinates import Angle, Longitude, Latitude, SkyCoord
from astropy import units as u
from numpy.testing import assert_allclose
from .. import Circle, Ellipse

""" Test initalization and other aspects of Shape objects """


def test_circle():
    with pytest.raises(ValueError):
        Circle.from_coordlist([0], "Some comment", "galactic")

    with pytest.raises(ValueError):
        Circle.from_coordlist([1, 2, 3, 4], "Some comment", "galactic")

    lon, lat = Longitude('2640', unit='arcminute'), Latitude('2d')
    sc = SkyCoord(lon, lat)
    radius_angle = Angle('4"')
    c = Circle(sc, radius_angle, "some comment", "icrs")
    assert c.origin.data.lon == lon
    assert c.origin.data.lat == lat
    assert c.origin.frame.name == sc.frame.name
    assert c.radius == radius_angle
    assert c.coord_list == [44, 2, 4/3600]
    assert c.coord_format == "icrs"

    c2 = Circle.from_coordlist(['44d0m0s', '2d', '4"'], 'comment', 'galactic')
    assert c2.origin.data.lon == lon
    assert c2.origin.data.lat == lat
    assert c2.origin.frame.name == 'galactic'
    assert c2.radius == radius_angle
    assert c2.coord_list == [44, 2, 4/3600]
    assert c2.coord_format == 'galactic'


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
    c = Circle.from_coordlist(proplist, "-", system)
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


def test_ellipse():
    with pytest.raises(ValueError):
        Ellipse([], "some comment", "icrs")

    with pytest.raises(ValueError):
        Ellipse([1, 2, 3, 4, 5, 6], "some comment", "icrs")

    lon, lat = Longitude('2640', unit='arcminute'), Latitude('2d')
    distance_angles = [Angle("1'"), Angle("20d"), Angle("5d"), Angle("1'")]
    rot_angle = Angle('4"')
    c = Ellipse([lon, lat, distance_angles[0], distance_angles[1],
                rot_angle], "some comment", "icrs")
    assert c.origin.data.lon == lon
    assert c.origin.data.lat == lat
    assert c.angle == rot_angle
    assert c.coord_list == [44, 2, 1/60, 20, 4/3600]

    c2 = Ellipse([lon, lat] + distance_angles + [rot_angle], "comment", 'fk5')
    assert c2.origin.data.lon == lon
    assert c2.origin.data.lat == lat
    assert c2.angle == rot_angle
    assert c2.coord_list == [44, 2, 1/60, 20, 5, 1/60, 4/3600]
