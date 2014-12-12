from astropy import units as u
import pytest
from .. import _ply_helper
from .. import DS9ParsingException


@pytest.mark.parametrize(("reg_string", "x", "y", "radius"), [
    ("circle 5 3 54", 5*u.pixel, 3*u.pixel, 54*u.pixel),
    ("circle(5,4,54)", 5*u.pixel, 4*u.pixel, 54*u.pixel),
    ("circle(5 4 54)", 5*u.pixel, 4*u.pixel, 54*u.pixel),
])
def test_ply_parsing(reg_string, x, y, radius):
    result = _ply_helper.parse_region_string(reg_string)
    assert len(result) == 1
    test_circle = result[0]

    assert test_circle.origin.data.x == x
    assert test_circle.origin.data.y == y
    assert test_circle.radius == radius


@pytest.mark.parametrize(("reg_string", "x", "y", "radius"), [
    ("circle 5 3 54\n", 5*u.pixel, 3*u.pixel, 54*u.pixel),
    ("circle(5,4,54);;", 5*u.pixel, 4*u.pixel, 54*u.pixel),
    (";;circle(5 4 54)\n\n", 5*u.pixel, 4*u.pixel, 54*u.pixel),
])
def test_delimiters(reg_string, x, y, radius):
    result = _ply_helper.parse_region_string(reg_string)
    assert len(result) == 1
    test_circle = result[0]

    assert test_circle.origin.data.x == x
    assert test_circle.origin.data.y == y
    assert test_circle.radius == radius


def test_multiple_circles():
    result = _ply_helper.parse_region_string("circle(1,2,3);circle(4,5,6);")

    assert len(result) == 2
    assert result[0].origin.data.x == 1*u.pixel
    assert result[0].origin.data.y == 2*u.pixel
    assert result[0].radius == 3*u.pixel
    assert result[1].origin.data.x == 4*u.pixel
    assert result[1].origin.data.y == 5*u.pixel
    assert result[1].radius == 6*u.pixel


def test_errors():
    with pytest.raises(DS9ParsingException):
        _ply_helper.parse_region_string("fulcrum(1,2,3)")

    with pytest.raises(DS9ParsingException):
        _ply_helper.parse_region_string("circle;")


@pytest.mark.parametrize(("reg_string", "coordinate_systems"), [
    ("circle(1d, 2d, 3d)", ["fk5"]),
    ("circle(1d, 2d, 3d)\ncircle(2d,3d,4d)", ['fk5', 'fk5']),
    ("galactic;circle(1d, 2d, 3d)", ["galactic"]),
    ("circle(1d, 2d, 3d);galactic;circle(2d,3d,4d)", ['fk5', 'galactic']),
    ("FK5;circle(1d, 2d, 3d);icrs;circle(2d,3d,4d)", ['fk5', 'icrs']),
    ("icrs;circle(1d, 2d, 3d);j2000;circle(2d,3d,4d)", ['icrs', 'fk5']),
    ("circle(1d, 2d, 3d);B1950;circle(2d,3d,4d)", ['fk5', 'fk4']),
])
def test_coordinate_systems(reg_string, coordinate_systems):
    result = _ply_helper.parse_region_string(reg_string)
    assert len(result) == len(coordinate_systems)
    for reg_object, reference_system in zip(result, coordinate_systems):
        assert reg_object.origin.frame.name == reference_system
        assert reg_object.coord_system == reference_system


@pytest.mark.parametrize(("reg_string", "x", "y", "radius"), [
    ("circle 5 3 54\n#Hello world", 5*u.pixel, 3*u.pixel, 54*u.pixel),
    ("# Hello World\ncircle(5,4,54)", 5*u.pixel, 4*u.pixel, 54*u.pixel),
    ("# circle(5 4 54)\ncircle(5,4,54)", 5*u.pixel, 4*u.pixel, 54*u.pixel),
])
def test_ignore_comments(reg_string, x, y, radius):
    result = _ply_helper.parse_region_string(reg_string)
    assert len(result) == 1
    test_circle = result[0]

    assert test_circle.origin.data.x == x
    assert test_circle.origin.data.y == y
    assert test_circle.radius == radius
