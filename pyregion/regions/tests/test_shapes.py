from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest
from astropy.coordinates import Angle, Longitude, Latitude
from .. import Circle, Ellipse

""" Test initalization and other aspects of Shape objects """


def test_circle():
    with pytest.raises(ValueError):
        Circle.from_coordlist([0], "Some comment", "galactic")

    with pytest.raises(ValueError):
        Circle.from_coordlist([1, 2, 3, 4], "Some comment", "galactic")

    lon, lat = Longitude('2640', unit='arcminute'), Latitude('2d')
    radius_angle = Angle('4"')
    c = Circle.from_coordlist([lon, lat, radius_angle], "some comment", "icrs")
    assert c.origin.data.lon == lon
    assert c.origin.data.lat == lat
    assert c.radius == radius_angle
    assert c.coord_list == [44, 2, 4/3600]
    assert c.coord_format == "icrs"


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
