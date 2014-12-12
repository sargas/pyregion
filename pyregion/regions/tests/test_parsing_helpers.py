from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .._parsing_helpers import _parse_position, _parse_coordinate
from astropy.coordinates import Longitude, Latitude
from astropy import units as u
import pytest
from numpy.testing.utils import assert_allclose


@pytest.mark.parametrize(("angle", "is_odd", "result"), [
    ('5d', True, 5.),
    ('5.0535d', False, 5.0535),
    ('11:12:13', True, 11*15 + 12/4 + 13/240),
    ('11:12:13', False, 11 + 12/60 + 13/3600),
    ('2r', True, 114.59155902616465),
])
def test_parse_position_angles(angle, is_odd, result):
    angle_obj = _parse_position(angle, is_odd)
    assert angle_obj.unit.is_equivalent(u.radian)
    assert_allclose(angle_obj.degree, result)


@pytest.mark.parametrize(("pixel_string", "result"), [
    ("5", 5),
    ("34.51", 34.51),
    ("941i", 941)
])
def test_parse_position_pixel(pixel_string, result):
    pixel_obj = _parse_position(pixel_string, True)
    assert pixel_obj.unit.is_equivalent(u.pixel)
    assert_allclose(pixel_obj.to(u.pixel).value, result)


@pytest.mark.parametrize(('odd', 'even', 'is_pixel'), [
    ("4h3m1s", "41.25234d", False),
    ("50", "100.0", True)
])
def test_parse_coordinate(odd, even, is_pixel):
    sc = _parse_coordinate(odd, even)
    if is_pixel:
        assert sc.data.x == float(odd)*u.pixel
        assert sc.data.y == float(even)*u.pixel
    else:
        assert sc.data.lon == Longitude(odd)
        assert sc.data.lat == Latitude(even)


def test_parse_coordinate_inconsistent():
    with pytest.raises(Exception):
        _parse_coordinate("4d", "400")
