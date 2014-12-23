from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from astropy.coordinates import BaseCoordinateFrame, CartesianRepresentation
from astropy.coordinates import RepresentationMapping
from astropy import units as u


__all__ = ['Image', 'Physical', 'Amplifier', 'Detector']


class _2DCartesianRepresentation(CartesianRepresentation):
    def __init__(*args, **kwargs):
        kwargs.setdefault('z', 0 * kwargs.get('x').unit)
        CartesianRepresentation.__init__(*args, **kwargs)

    attr_classes = CartesianRepresentation.attr_classes


class Image(BaseCoordinateFrame):
    "Image coordinate frame"
    default_representation = _2DCartesianRepresentation

    frame_specific_representation_info = {
        _2DCartesianRepresentation: [
            RepresentationMapping(reprname='x', framename='X',
                                  defaultunit=u.pixel),
            RepresentationMapping(reprname='y', framename='Y',
                                  defaultunit=u.pixel),
            RepresentationMapping(reprname='z', framename='Z',
                                  defaultunit=u.pixel)],
    }


class Physical(BaseCoordinateFrame):
    "Physical coordinate frame"
    default_representation = _2DCartesianRepresentation

    frame_specific_representation_info = {
        _2DCartesianRepresentation: [
            RepresentationMapping(reprname='x', framename='X',
                                  defaultunit=u.pixel),
            RepresentationMapping(reprname='y', framename='Y',
                                  defaultunit=u.pixel),
            RepresentationMapping(reprname='z', framename='Z',
                                  defaultunit=u.pixel)],
    }
Amplifier = Image
Detector = Image
