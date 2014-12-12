from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .._parsing_helpers import _parse_position, _parse_coordinate, _parse_size
from .. import DS9ParsingException
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


@pytest.mark.parametrize(('odd', 'even', 'is_pixel', 'system'), [
    ("4h3m1s", "41.25234d", False, 'icrs'),
    ("50", "100.0", True, 'icrs'),
    ("4h3m1s", "41.25234d", False, 'fk4'),
    ("50", "100.0", True, 'fk4')
])
def test_parse_coordinate(odd, even, is_pixel, system):
    sc = _parse_coordinate(odd, even, system)
    if is_pixel:
        assert sc.data.x == float(odd)*u.pixel
        assert sc.data.y == float(even)*u.pixel
        assert sc.frame.name != system
    else:
        assert sc.data.lon == Longitude(odd)
        assert sc.data.lat == Latitude(even)
        assert sc.frame.name == system


def test_parse_coordinate_inconsistent():
    with pytest.raises(DS9ParsingException):
        _parse_coordinate("4d", "400", 'galactic')


@pytest.mark.parametrize(("angle", "result"), [
    ('5d', 5.),
    ('5.0535d', 5.0535),
    ('41"', 41/60/60),
    ("51'", 51/60),
    ('2r', 114.59155902616465),
])
def test_parse_size_angles(angle, result):
    size_object = _parse_size(angle)
    assert size_object.unit.is_equivalent(u.radian)
    assert_allclose(size_object.degree, result)


@pytest.mark.parametrize(("pixel_string", "result"), [
    ("5", 5),
    ("34.51", 34.51),
    ("941i", 941)
])
def test_parse_size_pixel(pixel_string, result):
    pixel_obj = _parse_size(pixel_string)
    assert pixel_obj.unit.is_equivalent(u.pixel)
    assert_allclose(pixel_obj.to(u.pixel).value, result)
