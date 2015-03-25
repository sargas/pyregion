from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from astropy import units as u
from astropy.io.fits import Header
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import pytest
from .. import frames
import numpy as np


def test_image():
    im = frames.Image(X=1*u.pixel, Y=4*u.pixel)
    assert im.X == 1*u.pixel
    assert im.Y == 4*u.pixel


def test_image_with_header():
    header = Header()
    im = frames.Image(X=1*u.pixel, Y=5*u.pixel, fits_header=header)
    assert im.fits_header == header


def test_transform_to_image_error():
    with pytest.raises(ValueError):
        SkyCoord('4d 6d').transform_to(frames.Image)


@pytest.mark.parametrize(("coordinate", "x", "y"), [
    ("44d 67d", 108, 102)
])
def test_transform_to_image(coordinate, x, y):
    w = WCS(naxis=2)
    w.wcs.crpix = [108, 102]
    w.wcs.cdelt = np.array([-0.066667, 0.066667])
    w.wcs.crval = [44, 67]
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    header = w.to_header()

    sc = SkyCoord(coordinate).transform_to(frames.Image(
        fits_header=header))
    assert sc.data.x == x*u.pixel
    assert sc.data.y == y*u.pixel
