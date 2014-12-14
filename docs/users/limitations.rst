.. _limitations:

**********
Limitations
**********

*pyregion* is not complete. There are valid region files accepted by ds9 which
are not parsed by the current code, and implementation differences.

Currently, the following is not supported in region files parsed by *pyregion*:

#. Composite regions
#. Template regions
#. Region files that specify the tile in a mosaic image
#. Region files that specify a specific WCS in an image with multiple

The continous integration testing of *pyregion* only tests a handful of
headers. Heavily distorted headers may be treated differently then in ds9 if
there are no test cases for their distortion.

Contributions on `Github <https://github.com/astropy/pyregion/>`__ for the
above issues are welcome.

Aditionally, any unit conversions will have differences based on the different
models used by Astropy and AST. The differences in unit conversions are
quantified by the `Astropy Coordinate Benchmark
<http://www.astropy.org/coordinates-benchmark/summary_matrix.html#astropy>`__
project. The differences between ds9 and *pyregion* should be reflected in the
column comparing astropy and pyast.
