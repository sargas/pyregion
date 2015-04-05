from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import deque
from ._parsing_helpers import AngleArgument, DS9InconsistentArguments
from ._parsing_helpers import IntegerArgument
from ._parsing_helpers import RepeatedArgument, SizeArgument, SkyCoordArgument
from astropy.units import UnitsError


__all__ = ['Shape', 'ShapeList', 'Bpanda', 'Box', 'Circle', 'Epanda',
           'Ellipse', 'Panda', 'Point', 'Polygon', 'Line', 'Properties',
           'Annulus']


class ShapeList(object):
    """List of Shapes in a DS9 Region file

    This class provides convenience methods for dealing with the shapes found
    in a DS9 region. The shapes are retrievable as in a normal list.

    Parameters
    ----------
    shapes : list of `Shape`
        shapes to include
    """
    def __init__(self, shapes):
        self._shapes = shapes

    def __len__(self):
        return len(self._shapes)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return ShapeList(self._shapes.__getitem__(key))
        else:
            return self._shapes.__getitem__(key)

    def __iter__(self):
        return self._shapes.__iter__()

    def check_imagecoord(self):
        """Checks if this ShapeList includes image-based coordinates

        Returns
        -------
        bool
            True if any `Shape`.coord_system is an image coordinate
        """
        # Perhaps should be `coord_system in frames.*`
        return any(s.coord_system == 'image' for s in self)


class Properties(object):
    """Container for properties held by shapes

    The specifications for these properties come from
    `DS9 <http://ds9.si.edu/ref/region.html>`_.

    Parameters
    ----------
    properties : dict, optional
        Properties to record

    Attributes
    ----------
    text : str
        The text displayed with this shape
    color : {white, black, red, green, blue, cyan, magenta, yellow}
        The color of the region when rendered
    font : str
        Font family, size, weight and slant of text
    select : bool
        Whether this shape is selectable
    edit : bool
        Whether this shape is editable in DS9
    move : bool
        Whether this shape is movable in DS9
    delete : bool
        Whether this shape is deletable in DS9
    highlite : bool
        Whether this shape can be highlited in DS9
    include : bool
        Whether this shape is marked as included in this region
    fixed : bool
        Whether this shape stays fixed in size regardless of zoom in DS9
    tag : list of str
        List of tags associated with this shape
    """
    # defaults from http://ds9.si.edu/ref/region.html
    _default_properties = {
        'text': '',
        'color': 'green',
        'font': 'helvetica 10 normal roman',
        'select': '1',
        'edit': '1',
        'move': '1',
        'delete': '1',
        'highlite': '1',
        'include': '1',
        'fixed': '0',
        'tag': []
    }

    _BOOLEAN_PROPERTIES = ['select', 'highlight', 'dash', 'fixed', 'edit',
                           'move', 'rotate', 'delete', 'include']

    def __init__(self, properties={}):
        if isinstance(properties, Properties):
            self._properties = properties
        else:
            self._properties = self._default_properties.copy()
            self._properties.update(properties)

    def __getattr__(self, name):

        if name in self._BOOLEAN_PROPERTIES:
            return self._properties[name] == '1'
        elif name in self._properties:
            return self._properties[name]

        raise AttributeError("No property named {} defined".format(name))

    @property
    def is_source(self):
        """Whether this shape is flagged 'source'"""
        return self._properties.get('sourcebackground', 'source') == 'source'

    @property
    def is_background(self):
        """Whether this shape is flagged 'background'"""
        return not self.is_source


class Shape(object):
    """A DS9/CIAO Shape

    Parameters
    ----------
    properties : dict
        Properties of the shape
    coord_system : str
        Coordinate system used for angles and radii

    Attributes
    ----------
    properties :
        Properties of the shape.
    coord_system : `~astropy.coordinates.BaseCoordinateFrame`
        Coordinate system used for angles and radii
    """
    def __init__(self, *args, **kwargs):
        self.coord_system = kwargs.get('coord_system', None)
        self.properties = Properties(kwargs.get('properties', {}))
        for argument, value in zip(self._arguments, args):
            setattr(self, argument.name, value)

    @property
    def coord_format(self):
        """Name of coordinate system

        See Also
        --------
        coord_system
        """
        return self.coord_system.name

    @property
    def name(self):
        """name of this shape"""
        return type(self).__name__.lower()

    @property
    def tag(self):
        """List of tags"""
        return self.properties.tag

    @property
    def exclude(self):
        """Whether to exclude this shape from the region"""
        return not self.properties.include

    @classmethod
    def from_coordlist(cls, coordlist, coord_system, properties={}):
        """Create new shape from coordinate list

        This function parses a list of strings of a known coordinate system
        into a shape

        Parameters
        ----------
        coordlist : array_like
            List of strings giving each argument to the shape constructor
        coord_system : `~astropy.coordinates.BaseCoordinateFrame`
            Coordinate frame for parsing coordlist
        properties : dict, optional
            Dict of properties to initialize shape with

        Returns
        -------
        A new instance. The type depends on which subclass of `Shape`
        this is called from.
        """

        coords = deque(coordlist)
        try:
            args = [argument.from_coords(coords, coord_system)
                    for argument in cls._arguments]
        except UnitsError:
            raise DS9InconsistentArguments('{} created with incorrect units'
                                           ' for frame {}: {}'
                                           .format(repr(cls), coord_system,
                                                   coordlist))

        if len(coords) > 0:
            raise DS9InconsistentArguments(
                "{} created with too many coordinates: {}"
                .format(repr(cls), coordlist))

        return cls(*args, coord_system=coord_system, properties=properties)

    @property
    def coord_list(self):
        """List of coordinates

        This is the coordinates as floats in the current coord_system
        """
        coordlist = []
        for argument in self._arguments:
            coordlist.extend(argument.to_coords(getattr(self, argument.name)))

        return coordlist

    def transform_to(self, new_frame):
        """Transform into a new shape with a different coordinate system

        Parameters
        ----------
        new_frame : `~astropy.coordinates.BaseCoordinateFrame`
            Coordinate frame

        Returns
        -------
        A new instance in the specified coordinate system. The type depends on
        which subclass of `Shape` this is called from.
        """

        new_attributes = []
        for argument in self._arguments:
            new_attributes.append(argument.transform_to(
                getattr(self, argument.name),
                self.coord_system,
                new_frame))

        return self.__class__(*new_attributes, coord_system=new_frame,
                              properties=self.properties)


class Circle(Shape):
    """Circle Shape

    Parameters
    ----------
    origin : `~astropy.coordinates.SkyCoord`
        Center of this shape
    radius : `~astropy.units.Quantity` or `~astropy.coordinates.Angle`
        Radius of circle
    properties : dict
        Properties of the shape
    coord_system : `~astropy.coordinates.BaseCoordinateFrame`
        Coordinate system used for angles and radii
    """
    _arguments = [SkyCoordArgument('origin'), SizeArgument('radius')]


class Ellipse(Shape):
    """Ellipse Shape

    Parameters
    ----------
    origin : `~astropy.coordinates.SkyCoord`
        Center of this shape
    levels : list of tuple pairs of `~astropy.units.Quantity`
        List of semi-major and semi-minor axes for each annulus
    angle : `~astropy.coordinates.Angle`
        Rotation angle
    properties : dict
        Properties of the shape
    coord_system : `~astropy.coordinates.BaseCoordinateFrame`
        Coordinate system used for angles and radii
    """
    _arguments = [SkyCoordArgument('origin'),
                  RepeatedArgument([SizeArgument(), SizeArgument()], 'levels'),
                  AngleArgument('angle')]


class Box(Shape):
    """Box Shape

    Parameters
    ----------
    origin : `~astropy.coordinates.SkyCoord`
        Center of this shape
    levels : list of tuple pairs of `~astropy.units.Quantity`
        List of widths and heights for each annulus
    angle : `~astropy.coordinates.Angle`
        Rotation angle
    properties : dict
        Properties of the shape
    coord_system : `~astropy.coordinates.BaseCoordinateFrame`
        Coordinate system used for angles and sizes
    """
    _arguments = [SkyCoordArgument('origin'),
                  RepeatedArgument([SizeArgument(), SizeArgument()], 'levels'),
                  AngleArgument('angle')]

    @property
    def width(self):
        """Width of Box or smallest Box in annulus"""
        return self.levels[0][0]

    @property
    def height(self):
        """Height of Box or smallest Box in annulus"""
        return self.levels[0][1]


class Polygon(Shape):
    """Polygon Shape

    Parameters
    ----------
    points : array_like of `~astropy.coordinates.SkyCoord`
        Vertices of this polygon
    properties : dict
        Properties of the shape
    """
    _arguments = [RepeatedArgument([SkyCoordArgument()], 'points')]


class Panda(Shape):
    """Pie and Annulus Shape

    Parameters
    ----------
    origin : `~astropy.coordinates.SkyCoord`
        Center of this shape
    start_angle : `~astropy.coordinates.Angle`
        First angle of the shape, as measured counter-clockwise from the X axis
    stop_angle : `~astropy.coordinates.Angle`
        Last angle of the shape, as measured counter-clockwise from the X axis
    nangle : int
        Number of angles between start_angle and stop_angle to use
    inner : `~astropy.units.Quantity` or  `~astropy.coordinates.Angle`
        Inner radius of the annulus
    outer : `~astropy.units.Quantity` or  `~astropy.coordinates.Angle`
        Outer radius of the annulus
    nradius : int
        Number of radii between inner and outer to use
    properties : dict
        Properties of the shape
    coord_system : `~astropy.coordinates.BaseCoordinateFrame`
        Coordinate system used for angles and radii
    """
    _arguments = [SkyCoordArgument('origin'),
                  AngleArgument('start_angle'),
                  AngleArgument('stop_angle'),
                  IntegerArgument('nangle'),
                  SizeArgument('inner'),
                  SizeArgument('outer'),
                  IntegerArgument('nradius'),
                  ]


class Point(Shape):
    """Point Shape

    Parameters
    ----------
    origin : `~astropy.coordinates.SkyCoord`
        Location of this point
    properties : dict
        Properties of the shape

    Notes
    -----
    The type and size of this point is currently stored only as a property
    passed to the constructor.
    """
    _arguments = [SkyCoordArgument('origin')]

    @property
    def point_type(self):
        """Visualization of the point in DS9. Can be one of 'circle',\
        'box', 'diamond', 'cross', 'x', 'arrow', or 'boxcircle' """
        return self.properties.point[0]

    @property
    def point_size(self):
        """Size of the point. None if unset."""
        if self.properties.point[1] is not None:
            return float(self.properties.point[1])


class Epanda(Shape):
    """Ellipse Pie and Annulus Shape

    Parameters
    ----------
    origin : `~astropy.coordinates.SkyCoord`
        Center of this shape
    start_angle : `~astropy.coordinates.Angle`
        First angle of the shape, as measured counter-clockwise from the X axis
    stop_angle : `~astropy.coordinates.Angle`
        Last angle of the shape, as measured counter-clockwise from the X axis
    nangle : int
        Number of angles between start_angle and stop_angle to use
    major_inner : `~astropy.units.Quantity` or  `~astropy.coordinates.Angle`
        Inner semi-major axis of the annulus
    minor_inner : `~astropy.units.Quantity` or  `~astropy.coordinates.Angle`
        Inner semi-minor axis of the annulus
    major_outer : `~astropy.units.Quantity` or  `~astropy.coordinates.Angle`
        Outer semi-major axis of the annulus
    minor_outer : `~astropy.units.Quantity` or  `~astropy.coordinates.Angle`
        Outer semi-minor axis of the annulus
    nradius : int
        Number of radii between inner and outer to use
    angle : `~astropy.coordinates.Angle`
        Rotation angle
    properties : dict
        Properties of the shape
    coord_system : `~astropy.coordinates.BaseCoordinateFrame`
        Coordinate system used for angles and radii
    """
    _arguments = [SkyCoordArgument('origin'),
                  AngleArgument('start_angle'),
                  AngleArgument('stop_angle'),
                  IntegerArgument('nangle'),
                  SizeArgument('major_inner'),
                  SizeArgument('minor_inner'),
                  SizeArgument('major_outer'),
                  SizeArgument('minor_outer'),
                  IntegerArgument('nradius'),
                  AngleArgument('angle'),
                  ]


class Bpanda(Shape):
    """Box Pie and Annulus Shape

    Parameters
    ----------
    origin : `~astropy.coordinates.SkyCoord`
        Center of this shape
    start_angle : `~astropy.coordinates.Angle`
        First angle of the shape, as measured counter-clockwise from the X axis
    stop_angle : `~astropy.coordinates.Angle`
        Last angle of the shape, as measured counter-clockwise from the X axis
    nangle : int
        Number of angles between start_angle and stop_angle to use
    inner1 : `~astropy.units.Quantity` or  `~astropy.coordinates.Angle`
        Inner radius of the box annulus in the first direction
    inner2 : `~astropy.units.Quantity` or  `~astropy.coordinates.Angle`
        Inner radius of the box annulus in the second direction
    outer1 : `~astropy.units.Quantity` or  `~astropy.coordinates.Angle`
        Outer radius of the box annulus in the first direction
    outer2 : `~astropy.units.Quantity` or  `~astropy.coordinates.Angle`
        Outer radius of the box annulus in the second direction
    nradius : int
        Number of radii between inner and outer to use
    angle : `~astropy.coordinates.Angle`
        Rotation angle to the first direction
    properties : dict
        Properties of the shape
    coord_system : `~astropy.coordinates.BaseCoordinateFrame`
        Coordinate system used for angles and radii
    """
    _arguments = [SkyCoordArgument('origin'),
                  AngleArgument('start_angle'),
                  AngleArgument('stop_angle'),
                  IntegerArgument('nangle'),
                  SizeArgument('inner1'),
                  SizeArgument('inner2'),
                  SizeArgument('outer1'),
                  SizeArgument('outer2'),
                  IntegerArgument('nradius'),
                  AngleArgument('angle'),
                  ]


class Line(Shape):
    """Line Shape

    Parameters
    ----------
    start_position, last_position : `~astropy.coordinates.SkyCoord`
        Endpoints of the line segment
    properties : dict
        Properties of the shape
    coord_system : `~astropy.coordinates.BaseCoordinateFrame`
        Coordinate system used for angles and radii
    """
    _arguments = [SkyCoordArgument('start_position'),
                  SkyCoordArgument('last_position')]

    @property
    def start_arrow(self):
        """Boolean indicting an arrow at the starting location of this line"""
        return self.properties.line[0] == '1'

    @property
    def end_arrow(self):
        """Boolean indicting an arrow at the ending location of this line"""
        return self.properties.line[1] == '1'


class Annulus(Shape):
    """Circular Annulus Shape

    Parameters
    ----------
    origin : `~astropy.coordinates.SkyCoord`
        Center of this shape
    radii : list of `~astropy.units.Quantity` or `~astropy.coordinates.Angle`
        Radii of each annulus
    properties : dict
        Properties of the shape
    coord_system : `~astropy.coordinates.BaseCoordinateFrame`
        Coordinate system used for angles and radii
    """
    _arguments = [SkyCoordArgument('origin'),
                  RepeatedArgument([SizeArgument()], 'radii')
                  ]
