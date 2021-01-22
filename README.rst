corazon
=======

.. image:: https://readthedocs.org/projects/corazon/badge/?version=latest
    :target: https://corazon.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://github.com/spacetelescope/corazon/workflows/CI/badge.svg
    :target: https://github.com/spacetelescope/corazon/actions
    :alt: GitHub Actions CI Status

.. image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org
    :alt: Powered by Astropy Badge

`corazon` is a Python package to run a simple BLS exoplanet search on TESS FFIs.
It retrievs TESS light curves, detrends a light curve,
runs a box-least-squares fit search algorithm and vets the signal using
`exovetter` (https://github.com/spacetelescope/exovetter/).

This package depends on the next yet released (as of Jan 22, 2021) Lightkurve v2.0 (https://github.com/KeplerGO/lightkurve)to allow it to retrieve high-level-science
products from the MAST. It must be locally installed from git to run corazon.

To run corazon on one target do the following:

```python
from corazon import run_pipeline
ticid = 383724012
sector = 14
outdir = "/Users/username/local/directory/to/store/output/"
run_pipeline.run_write_one(ticid, sector, outdir)
```
