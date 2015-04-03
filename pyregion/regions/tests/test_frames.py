from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from astropy import units as u
from astropy.io.fits import Header
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord, ICRS
import pytest
from .. import frames
import numpy as np
from numpy.testing import assert_allclose


def test_image():
    im = frames.Image(X=1*u.pixel, Y=4*u.pixel)
    assert im.X == 1*u.pixel
    assert im.Y == 4*u.pixel


def test_image_with_header():
    header = Header()
    im = frames.Image(X=1*u.pixel, Y=5*u.pixel, fits_header=header)
    assert im.fits_header == header


def test_transform_image_error():
    with pytest.raises(ValueError):
        SkyCoord('4d 6d').transform_to(frames.Image)

    with pytest.raises(ValueError):
        SkyCoord(2*u.pixel, 5*u.pixel, frame=frames.Image).transform_to(ICRS)


@pytest.mark.parametrize(("coordinate", "x", "y"), [
    ("44d 67d", 108, 102),
    ("44.5d 67.5d", 105.1297994, 109.5117237),
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
    assert_allclose(sc.data.x, x*u.pixel)
    assert_allclose(sc.data.y, y*u.pixel)

    sc2 = SkyCoord(x*u.pixel, y*u.pixel,
                   frame=frames.Image(fits_header=header)).transform_to(
                       ICRS)
    sc21 = SkyCoord(coordinate)
    assert sc21.frame.name == sc2.frame.name
    assert_allclose(sc21.ra, sc2.ra)
    assert_allclose(sc21.dec, sc2.dec)
