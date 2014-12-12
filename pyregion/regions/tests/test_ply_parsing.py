from astropy import units as u
import pytest
from .. import _ply_helper
from .. import DS9ParsingException


@pytest.mark.parametrize(("reg_string", "x", "y", "radius"), [
    ("circle 5 3 54", 5*u.pixel, 3*u.pixel, 54*u.pixel),
    ("circle(5,4,54)", 5*u.pixel, 3*u.pixel, 54*u.pixel),
])
def test_ply_parsing(reg_string, x, y, radius):
    result = _ply_helper.DS9Parser().parse(reg_string)
    assert len(result) == 1
    test_circle = result[0]

    test_circle.origin.data.x == x
    test_circle.origin.data.y == y
    test_circle.radius == radius


def test_multiple_circles():
    result = _ply_helper.DS9Parser().parse("circle(1,2,3);circle(4,5,6);")

    assert len(result) == 2
    result[0].origin.data.x == 1*u.pixel
    result[0].origin.data.y == 2*u.pixel
    result[0].radius == 3*u.pixel
    result[1].origin.data.x == 4*u.pixel
    result[1].origin.data.y == 5*u.pixel
    result[1].radius == 6*u.pixel


def test_errors():
    with pytest.raises(DS9ParsingException):
        _ply_helper.DS9Parser().parse("fulcrum(1,2,3)")

    with pytest.raises(DS9ParsingException):
        _ply_helper.DS9Parser().parse("circle circle circle")
