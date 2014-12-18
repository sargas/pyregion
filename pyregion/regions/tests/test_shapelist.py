""" Test initalization and other aspects of ShapeList objects """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest
from astropy.coordinates import Angle, SkyCoord
from .. import ShapeList, Circle


def test_shapelists():
    circle1 = Circle(SkyCoord('1d 2d'), Angle('3d'))
    circle2 = Circle(SkyCoord('3d 4d'), Angle('5d'))
    circle3 = Circle(SkyCoord('6d 7d'), Angle('8d'))

    result = ShapeList([circle1, circle2, circle3])
    assert len(result) == 3
    assert result[0] == circle1
    assert result[1] == circle2
    assert result[2] == circle3

    sliced_result = result[:2]
    assert isinstance(sliced_result, ShapeList)
    assert len(sliced_result) == 2
    assert sliced_result[0] == circle1
    assert sliced_result[1] == circle2
    with pytest.raises(IndexError):
        sliced_result[2]


def test_shapelists_check_imagecoord():
    circle1 = Circle(SkyCoord('1d 2d'), Angle('3d'), coord_system='image')
    circle2 = Circle(SkyCoord('3d 4d'), Angle('5d'), coord_system='fk5')
    circle3 = Circle(SkyCoord('6d 7d'), Angle('8d'), coord_system='fk4')
    assert ShapeList([circle1, circle2, circle3]).check_imagecoord()
    assert not ShapeList([circle2, circle3]).check_imagecoord()
