from astropy import units as u
from astropy.coordinates import Angle
import pytest
from .._ply_helper import parse_region_string
from .. import ShapeList, DS9ParsingException


@pytest.mark.parametrize(("reg_string", "x", "y", "radius"), [
    ("circle 5 3 54", 5*u.pixel, 3*u.pixel, 54*u.pixel),
    ("circle(5,4,54)", 5*u.pixel, 4*u.pixel, 54*u.pixel),
    ("circle(5 4 54)", 5*u.pixel, 4*u.pixel, 54*u.pixel),
    ("circle(-5 4 -54)", -5*u.pixel, 4*u.pixel, -54*u.pixel),
])
def test_ply_parsing(reg_string, x, y, radius):
    result = parse_region_string(reg_string)
    assert isinstance(result, ShapeList)
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
    result = parse_region_string(reg_string)
    assert len(result) == 1
    test_circle = result[0]

    assert test_circle.origin.data.x == x
    assert test_circle.origin.data.y == y
    assert test_circle.radius == radius


def test_multiple_circles():
    result = parse_region_string("circle(1,2,3);circle(4,5,6);")

    assert isinstance(result, ShapeList)
    assert len(result) == 2
    assert result[0].origin.data.x == 1*u.pixel
    assert result[0].origin.data.y == 2*u.pixel
    assert result[0].radius == 3*u.pixel
    assert result[1].origin.data.x == 4*u.pixel
    assert result[1].origin.data.y == 5*u.pixel
    assert result[1].radius == 6*u.pixel


def test_errors():
    with pytest.raises(DS9ParsingException):
        parse_region_string("fulcrum(1,2,3)")

    with pytest.raises(DS9ParsingException):
        parse_region_string("circle;")


@pytest.mark.parametrize(("reg_string", "coordinate_systems"), [
    ("circle(1, 2, 3)", ["physical"]),
    ("fk5; circle(1d, 2d, 3d)", ["fk5"]),
    ("fk5; circle(1d, 2d, 3d)\ncircle(2d,3d,4d)", ['fk5', 'fk5']),
    ("image; circle(1,2,3); icrs\n circle(1d,2d,3d)", ['image', 'icrs']),
    ("galactic;circle(1d, 2d, 3d)", ["galactic"]),
    ("fk5; circle(1d, 2d, 3d);galactic;circle(2d,3d,4d)", ['fk5', 'galactic']),
    ("FK5;circle(1d, 2d, 3d);icrs;circle(2d,3d,4d)", ['fk5', 'icrs']),
    ("icrs;circle(1d, 2d, 3d);j2000;circle(2d,3d,4d)", ['icrs', 'fk5']),
    ("fk5;circle(1d, 2d, 3d);B1950;circle(2d,3d,4d)", ['fk5', 'fk4']),
])
def test_coordinate_systems(reg_string, coordinate_systems):
    result = parse_region_string(reg_string)
    assert len(result) == len(coordinate_systems)
    for reg_object, reference_system in zip(result, coordinate_systems):
        assert reg_object.origin.frame.name == reference_system
        assert reg_object.coord_system.name == reference_system


@pytest.mark.parametrize(("reg_string", "x", "y", "radius"), [
    ("circle 5 3 54\n#Hello world", 5*u.pixel, 3*u.pixel, 54*u.pixel),
    ("# Hello World\ncircle(5,4,54)", 5*u.pixel, 4*u.pixel, 54*u.pixel),
    ("# circle(5 4 54)\ncircle(5,4,54)", 5*u.pixel, 4*u.pixel, 54*u.pixel),
])
def test_ignore_comments(reg_string, x, y, radius):
    result = parse_region_string(reg_string)
    assert len(result) == 1
    test_circle = result[0]

    assert test_circle.origin.data.x == x
    assert test_circle.origin.data.y == y
    assert test_circle.radius == radius


def test_default_properties():
    result = parse_region_string('circle 1 2 3;')[0]

    assert result.properties.color == 'green'
    assert result.properties.text == ''
    assert result.properties.font == 'helvetica 10 normal roman'
    assert result.properties.select
    assert result.properties.edit
    assert result.properties.move
    assert result.properties.delete
    assert result.properties.highlite
    assert result.properties.include
    assert not result.properties.fixed

    with pytest.raises(AttributeError):
        result.properties.ruler
    with pytest.raises(AttributeError):
        result.properties.line
    with pytest.raises(AttributeError):
        result.properties.point


def test_properties():
    result = parse_region_string(' circle 1 2 3 # color="yellow"'
                                 ''' text={howdy ' "}''')[0]
    assert result.properties.color == 'yellow'
    assert result.properties.text == '''howdy ' "'''

    result = parse_region_string('circle(1,2,3); circle(4,5,6)'
                                 '# edit=0\ncircle(7,8,9)')
    assert result[0].properties.edit
    assert not result[1].properties.edit
    assert result[2].properties.edit

    result = parse_region_string(' circle 1 2 3 # color="yellow"'
                                 ' dashlist = 8 3')[0]
    assert result.properties.color == 'yellow'
    assert result.properties.dashlist == ('8', '3')
    assert result.properties.is_source
    assert not result.properties.is_background


def test_source_background_properties():
    result = parse_region_string('circle 1 2 3 # color="yellow"'
                                 ' dashlist = 8 3')[0]
    assert result.properties.color == 'yellow'
    assert result.properties.dashlist == ('8', '3')
    assert result.properties.is_source
    assert not result.properties.is_background

    result = parse_region_string('circle 1 2 3 # edit=1 source background')[0]
    assert result.properties.edit
    assert not result.properties.is_source
    assert result.properties.is_background

    result = parse_region_string('circle 1 2 3 # edit=1 background')[0]
    assert result.properties.edit
    assert not result.properties.is_source
    assert result.properties.is_background

    result = parse_region_string('circle 1 2 3 # background edit=1')[0]
    assert result.properties.edit
    assert not result.properties.is_source
    assert result.properties.is_background

    result = parse_region_string('global source=0\ncircle 1 2 3')[0]
    assert result.properties.is_background
    assert not result.properties.is_source

    result = parse_region_string('global source=1\ncircle 1 2 3')[0]
    assert result.properties.is_source
    assert not result.properties.is_background


def test_tags():
    result = parse_region_string('circle 1 2 3 # color={yellow}')[0]
    assert len(result.tag) == 0

    result = parse_region_string('circle 1 2 3 # tag=42 tag=1')[0]
    assert result.tag == ['42', '1']

    result = parse_region_string('circle 1 2 3 # color="yellow" tag={Group 1}'
                                 ' tag=Hello')[0]
    assert result.properties.color == 'yellow'
    assert result.tag == ['Group 1', 'Hello']


def test_global_properties():
    result = parse_region_string('global font="test"\ncircle 1 2 3')
    assert len(result) == 1
    assert result[0].properties.font == 'test'

    result = parse_region_string('global font="test"\ncircle 1 2 3 # font="x"')
    assert len(result) == 1
    assert result[0].properties.font == 'x'

    result = parse_region_string('global font="test" background\ncircle 1 2 3')
    assert len(result) == 1
    assert result[0].properties.font == 'test'
    assert result[0].properties.is_background


def test_include_flag():
    result = parse_region_string('circle 1 2 3')[0]
    assert result.properties.include

    result = parse_region_string('+circle 1 2 3')[0]
    assert result.properties.include

    result = parse_region_string('-circle 1 2 3')[0]
    assert not result.properties.include

    result = parse_region_string('-circle 1 2 3; circle 3 2 1; +circle 5 6 7')
    assert len(result) == 3
    assert not result[0].properties.include
    assert result[1].properties.include
    assert result[2].properties.include

    result = parse_region_string('global include=0\n'
                                 'circle 1 2 3;+circle 1 2 3')
    assert not result[0].properties.include
    assert result[1].properties.include


def test_unsupported():
    with pytest.raises(DS9ParsingException):
        parse_region_string('wcsa; circle 1 2 3')

    with pytest.raises(DS9ParsingException):
        parse_region_string('tile 2; circle 1 2 3')


def test_parse_ellipse():
    result = parse_region_string('ellipse 1 2 3 4 5')
    assert len(result) == 1
    assert result[0].origin.data.x == 1*u.pixel
    assert result[0].origin.data.y == 2*u.pixel
    assert len(result[0].levels) == 1
    assert result[0].levels[0] == (3*u.pixel, 4*u.pixel)
    assert result[0].angle == Angle(5, u.degree)


def test_parse_box():
    result = parse_region_string('box 1 2 3 4 5')
    assert len(result) == 1
    assert result[0].origin.data.x == 1*u.pixel
    assert result[0].origin.data.y == 2*u.pixel
    assert result[0].width == 3*u.pixel
    assert result[0].height == 4*u.pixel
    assert result[0].angle == Angle(5, u.degree)

    result = parse_region_string('rotbox 1 2 3 4 5')
    assert len(result) == 1
    assert result[0].origin.data.x == 1*u.pixel
    assert result[0].origin.data.y == 2*u.pixel
    assert result[0].width == 3*u.pixel
    assert result[0].height == 4*u.pixel
    assert result[0].angle == Angle(5, u.degree)

    result = parse_region_string('box 1 2 3 4 5 6 7')
    assert len(result) == 1
    assert result[0].origin.data.x == 1*u.pixel
    assert result[0].origin.data.y == 2*u.pixel
    assert result[0].width == 3*u.pixel
    assert result[0].height == 4*u.pixel
    assert len(result[0].levels) == 2
    assert result[0].levels[0] == (3*u.pixel, 4*u.pixel)
    assert result[0].levels[1] == (5*u.pixel, 6*u.pixel)
    assert result[0].angle == Angle(7, u.degree)


def test_parse_polygon():
    result = parse_region_string('polygon 1 2 3 4 5 6')
    assert len(result) == 1
    result = result[0]
    assert len(result.points) == 3
    assert result.points[0].data.x == 1*u.pixel
    assert result.points[0].data.y == 2*u.pixel
    assert result.points[1].data.x == 3*u.pixel
    assert result.points[1].data.y == 4*u.pixel
    assert result.points[2].data.x == 5*u.pixel
    assert result.points[2].data.y == 6*u.pixel


def test_parse_panda():
    result = parse_region_string('panda 1 2 3 4 5 6 7 8')
    assert len(result) == 1
    result = result[0]
    assert result.origin.data.x == 1*u.pixel
    assert result.origin.data.y == 2*u.pixel
    assert result.start_angle == Angle('3d')
    assert result.stop_angle == Angle('4d')
    assert result.nangle == 5
    assert result.inner == 6*u.pixel
    assert result.outer == 7*u.pixel
    assert result.nradius == 8


def test_parse_point():
    result = parse_region_string('point 1 2 # point=diamond 1')
    assert len(result) == 1
    result = result[0]
    assert result.origin.data.x == 1*u.pixel
    assert result.origin.data.y == 2*u.pixel
    assert result.point_type == 'diamond'
    assert result.point_size == 1

    result = parse_region_string('point 1 2 # point=diamond edit = 1')
    assert len(result) == 1
    result = result[0]
    assert result.origin.data.x == 1*u.pixel
    assert result.origin.data.y == 2*u.pixel
    assert result.point_type == 'diamond'
    assert result.point_size is None
    assert result.properties.edit


def test_parse_line():
    result = parse_region_string('line 1 2 3 4')
    assert len(result) == 1
    result = result[0]
    assert result.start_position.data.x == 1*u.pixel
    assert result.start_position.data.y == 2*u.pixel
    assert result.last_position.X == 3*u.pixel
    assert result.last_position.Y == 4*u.pixel

    result = parse_region_string('line 1 2 3 4 # line=0 1')
    assert len(result) == 1
    result = result[0]
    assert result.start_position.data.x == 1*u.pixel
    assert result.start_position.data.y == 2*u.pixel
    assert result.last_position.X == 3*u.pixel
    assert result.last_position.Y == 4*u.pixel
    assert result.properties.line == ('0', '1')


def test_parse_annulus():
    result = parse_region_string('annulus(1,2,3)')
    assert len(result) == 1
    result = result[0]
    assert result.origin.X == 1*u.pixel
    assert result.origin.Y == 2*u.pixel
    assert result.radii == [3*u.pixel]

    result = parse_region_string('annulus(1,2,3,4,5,6,7)')
    assert len(result) == 1
    result = result[0]
    assert result.origin.X == 1*u.pixel
    assert result.origin.Y == 2*u.pixel
    assert result.radii == [i*u.pixel for i in range(3, 8)]
