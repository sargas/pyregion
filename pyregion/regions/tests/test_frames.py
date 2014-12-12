from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from astropy import units as u
from .. import frames


def test_image():
    im = frames.Image(X=1*u.pixel, Y=4*u.pixel)
    assert im.X == 1*u.pixel
    assert im.Y == 4*u.pixel
