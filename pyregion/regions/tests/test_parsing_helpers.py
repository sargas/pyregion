from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .._parsing_helpers import AngleArgument, IntegerArgument, RepeatedArgument
from .._parsing_helpers import SizeArgument, SkyCoordArgument
from .. import DS9ParsingException, DS9InconsistentArguments
from astropy.coordinates import Longitude, Latitude
from astropy import units as u
import pytest
from numpy.testing.utils import assert_allclose
from collections import deque


@pytest.mark.parametrize(("angle", "is_odd", "result"), [
    ('5d', True, 5.),
    ('5.0535d', False, 5.0535),
    ('11:12:13', True, 11*15 + 12/4 + 13/240),
    ('11:12:13', False, 11 + 12/60 + 13/3600),
    ('2r', True, 114.59155902616465),
])
def test_parse_position_angles(angle, is_odd, result):
    skycoord_arg = SkyCoordArgument()
    angle_obj = skycoord_arg._parse_position(angle, is_odd)
    assert angle_obj.unit.is_equivalent(u.radian)
    assert_allclose(angle_obj.degree, result)


@pytest.mark.parametrize(("pixel_string", "result"), [
    ("5", 5),
    ("34.51", 34.51),
    ("941i", 941)
])
def test_parse_position_pixel(pixel_string, result):
    skycoord_arg = SkyCoordArgument()
    pixel_obj = skycoord_arg._parse_position(pixel_string, True)
    assert pixel_obj.unit.is_equivalent(u.pixel)
    assert_allclose(pixel_obj.to(u.pixel).value, result)


@pytest.mark.parametrize(('odd', 'even', 'is_pixel', 'system', 'coordlist'), [
    ("4h3m1s", "41.25234d", False, 'icrs', (60.754166666666656, 41.25234)),
    ("50", "100.0", True, 'icrs', (50, 100)),
    ("4h3m1s", "41.25234d", False, 'fk4', (60.754166666666656, 41.25234)),
    ("50", "100.0", True, 'fk4', (50, 100))
])
def test_skycoordargument(odd, even, is_pixel, system, coordlist):
    skycoord_arg = SkyCoordArgument()
    coords = deque([odd, even])
    sc = skycoord_arg.from_coords(coords, system)
    if is_pixel:
        assert sc.data.x == float(odd)*u.pixel
        assert sc.data.y == float(even)*u.pixel
        assert sc.frame.name != system
    else:
        assert sc.data.lon == Longitude(odd)
        assert sc.data.lat == Latitude(even)
        assert sc.frame.name == system

    assert skycoord_arg.to_coords(sc) == coordlist
    assert len(coords) == 0


def test_skycoordargument_inconsistent():
    skycoord_arg = SkyCoordArgument()

    with pytest.raises(DS9ParsingException):
        skycoord_arg.from_coords(deque(["4d", "400"]), 'galactic')


@pytest.mark.parametrize(("angle", "result"), [
    ('5d', 5.),
    ('5.0535d', 5.0535),
    ('41"', 41/60/60),
    ("51'", 51/60),
    ('2r', 114.59155902616465),
])
def test_sizeargument_angles(angle, result):
    size_arg = SizeArgument()
    coords = deque([angle])

    size_object = size_arg.from_coords(coords, "icrs")
    assert size_object.unit.is_equivalent(u.radian)
    assert_allclose(size_object.degree, result)
    assert len(coords) == 0

    assert size_arg.to_coords(size_object) == [result, ]


@pytest.mark.parametrize(("pixel_string", "result"), [
    ("5", 5),
    ("34.51", 34.51),
    ("941i", 941)
])
def test_sizeargument_pixel(pixel_string, result):
    size_arg = SizeArgument()
    coords = deque([pixel_string])

    pixel_obj = size_arg.from_coords(coords, 'icrs')
    assert pixel_obj.unit.is_equivalent(u.pixel)
    assert_allclose(pixel_obj.to(u.pixel).value, result)
    assert len(coords) == 0

    assert size_arg.to_coords(pixel_obj) == [result, ]


@pytest.mark.parametrize(("angle", "result"), [
    ('5', 5.),
    ('5.0535', 5.0535),
])
def test_angleargument(angle, result):
    angle_arg = AngleArgument()
    coords = deque([angle])

    angle_object = angle_arg.from_coords(coords, "icrs")
    assert angle_object.unit.is_equivalent(u.radian)
    assert_allclose(angle_object.degree, result)
    assert len(coords) == 0

    assert angle_arg.to_coords(angle_object) == [result, ]


def test_missing_arguments():
    with pytest.raises(DS9InconsistentArguments):
        SizeArgument().from_coords(deque([]), 'icrs')

    with pytest.raises(DS9InconsistentArguments):
        AngleArgument().from_coords(deque([]), 'icrs')

    with pytest.raises(DS9InconsistentArguments):
        SkyCoordArgument().from_coords(deque([]), 'icrs')

    with pytest.raises(DS9InconsistentArguments):
        SkyCoordArgument().from_coords(deque(['4']), 'icrs')


def test_repeatedargument():
    class MockArg:
        def from_coords(coords, coord_system):
            return coords.popleft() + 1

        def to_coords(coord):
            return [coord - 1]

    repeated_arg = RepeatedArgument([MockArg, MockArg, MockArg])

    coords = deque([1, 2, 3, 4, 5, 6])
    assert repeated_arg.from_coords(coords, '') == [(2, 3, 4), (5, 6, 7)]
    assert len(coords) == 0
    assert_allclose(repeated_arg.to_coords([(2, 3, 4), (5, 6, 7)]),
                    [1, 2, 3, 4, 5, 6])

    with pytest.raises(DS9InconsistentArguments):
        repeated_arg.from_coords(deque([1, 2]), '')


def test_integerargument():
    int_arg = IntegerArgument()
    coords = deque(['4', None, None])
    assert int_arg.from_coords(coords, '') == 4
    assert len(coords) == 2
    assert int_arg.to_coords(2) == [2]

    with pytest.raises(DS9InconsistentArguments):
        int_arg.from_coords(deque(['1.3']), '')
