""" Test coordinate system transformations """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from astropy.coordinates import Angle, ICRS, FK5, SkyCoord, Longitude, Latitude
from astropy import units as u
from astropy.wcs import WCS
import numpy as np
from numpy.testing import assert_allclose
from .. import Circle, Panda, Ellipse
from ..frames import Image


def test_no_change():
    test_input = Circle(SkyCoord(5*u.pixel, 2*u.pixel, frame=Image),
                        1*u.pixel,
                        coord_system=Image)
    test_result = test_input.transform_to(Image)
    assert test_input.origin.separation(test_result.origin) == 0
    assert test_input.radius == test_result.radius
    assert test_result.origin.frame.name == Image.name
    assert test_result.coord_system.name == Image.name

    test_input = Circle(SkyCoord('1d 2d', frame=ICRS),
                        Angle('5d'),
                        coord_system=ICRS)
    test_result = test_input.transform_to(ICRS)
    assert test_input.origin.separation(test_result.origin) == 0
    assert test_input.radius == test_result.radius
    assert test_result.origin.frame.name == ICRS.name
    assert test_result.coord_system.name == ICRS.name


def test_sky_transformations():
    test_input = Circle(SkyCoord('1d 2d', frame=FK5),
                        Angle('5d'),
                        coord_system=FK5)
    test_result = test_input.transform_to(ICRS)
    assert test_input.origin.separation(test_result.origin) == 0
    assert test_result.origin.frame.name == ICRS.name
    assert test_result.coord_system.name == ICRS.name
    assert test_result.origin.data.lon == Longitude('0.9999934443434741d')
    assert test_result.origin.data.lat == Latitude('1.99999756908023d')
    assert test_result.radius == Angle('5d')


def test_image_to_sky_transformations():
    w = WCS(naxis=2)
    w.wcs.crpix = [108, 102]
    w.wcs.cdelt = np.array([-0.066667, 0.066667])
    w.wcs.crval = [44, 67]
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    header = w.to_header()
    header['NAXIS1'] = 1014
    header['NAXIS2'] = 1024
    frame = Image(fits_header=header)

    test_input = Circle(SkyCoord(108*u.pixel, 102*u.pixel, frame=frame),
                        2*u.pixel,
                        coord_system=frame)
    test_result = test_input.transform_to(ICRS)
    assert test_result.origin.ra == Longitude('44d')
    assert test_result.origin.dec == Latitude('67d')
    assert_allclose(test_result.radius, Angle(2*0.066667*u.degree),
                    atol=0.000001)

    test_input = Panda(SkyCoord(108*u.pixel, 102*u.pixel, frame=frame),
                       Angle('30d'), Angle('90d'), 1,
                       20*u.pixel, 40*u.pixel, 1,
                       coord_system=frame)
    test_result = test_input.transform_to(ICRS)
    assert test_result.origin.ra == Longitude('44d')
    assert test_result.origin.dec == Latitude('67d')
    assert_allclose(test_result.start_angle, Angle(293.538*u.degree),
                    atol=0.001)
    assert_allclose(test_result.stop_angle, Angle(353.538*u.degree),
                    atol=0.001)
    assert test_result.nangle == 1
    assert_allclose(test_result.inner, Angle(20*0.066667*u.degree),
                    atol=0.000001)
    assert_allclose(test_result.outer, Angle(40*0.066667*u.degree),
                    atol=0.000001)
    assert test_result.nradius == 1

    test_input = Ellipse(SkyCoord(108*u.pixel, 102*u.pixel, frame=frame),
                         [(Angle('30d'), Angle('90d'))],
                         Angle(0*u.degree),
                         coord_system=frame)
    test_result = test_input.transform_to(ICRS)
