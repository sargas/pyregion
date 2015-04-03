from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from astropy.coordinates import BaseCoordinateFrame, CartesianRepresentation
from astropy.coordinates import RepresentationMapping, FrameAttribute, SkyCoord
from astropy.coordinates import FunctionTransform, ICRS, frame_transform_graph
from astropy import units as u
from astropy.wcs import WCS


__all__ = ['Image', 'Physical', 'Amplifier', 'Detector']


class TwoDCartesianRepresentation(CartesianRepresentation):
    def __init__(*args, **kwargs):
        kwargs.setdefault('z', 0 * kwargs.get('x').unit)
        CartesianRepresentation.__init__(*args, **kwargs)

    attr_classes = CartesianRepresentation.attr_classes


class SkyFrame(BaseCoordinateFrame):
    """A frame with 2d pixel coordinates"""
    default_representation = TwoDCartesianRepresentation

    frame_specific_representation_info = {
        TwoDCartesianRepresentation: [
            RepresentationMapping(reprname='x', framename='X',
                                  defaultunit=u.pixel),
            RepresentationMapping(reprname='y', framename='Y',
                                  defaultunit=u.pixel),
            RepresentationMapping(reprname='z', framename='Z',
                                  defaultunit=u.pixel)],
    }

    fits_header = FrameAttribute(default=None)


class Image(SkyFrame):
    """Image coordinate frame"""
    pass


class Physical(SkyFrame):
    """Physical coordinate frame"""
    pass


class Amplifier(SkyFrame):
    """Amplifier coordinate frame"""
    pass


class Detector(SkyFrame):
    """Detector coordinate frame"""
    pass


@frame_transform_graph.transform(FunctionTransform, ICRS, Image)
def icrs_to_image(icrs_coord, image_frame):
    if image_frame.fits_header is None:
        raise ValueError("Cannot convert {} to {} frame without a FITS header"
                         .format(repr(icrs_coord), repr(image_frame)))
    image_wcs = WCS(image_frame.fits_header)
    x, y = SkyCoord(icrs_coord).to_pixel(image_wcs, 1)
    return image_frame.__class__(X=x*u.pixel, Y=y*u.pixel,
                                 fits_header=image_frame.fits_header)


@frame_transform_graph.transform(FunctionTransform, Image, ICRS)
def image_to_icrs(image_coord, icrs_frame):
    if image_coord.fits_header is None:
        raise ValueError("Cannot convert {} to {} frame without a FITS header"
                         .format(repr(image_coord), repr(icrs_frame)))
    image_wcs = WCS(image_coord.fits_header)

    return SkyCoord.from_pixel(image_coord.data.x,
                               image_coord.data.y,
                               image_wcs,
                               origin=1).transform_to(icrs_frame).frame
