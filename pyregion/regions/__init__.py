"""
This subpackage contains classes for different shapes that show up in CIAO
and DS9 region files
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .core import *
from . import frames
from ._parsing_helpers import DS9ParsingException, DS9InconsistentArguments
