#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Feb 03 2025

@author: smullally, m-dallas

Generate light curves for TGLC s3 locations.

"""

import lightkurve as lk
import s3fs
import numpy as np


def tglc_from_S3(s3_location):
    """
    Parameters
    ----------
    s3_location : string
        s3 bucket location

    Returns
    -------
    lc : lightkurve object
        lightkurve object of the data requested.

    """

    lc = lk.io.tglc.read_tglc_lightcurve(s3_location)
    
    # Ideally use the calibrated psf flux (the default of read_tglc_lightcurve), but if it is all nans use the calibrated aperture flux 
    idx = ~np.isnan(lc['flux'])
    if len(lc['flux'][idx]) == 0:
        lc = lk.io.tglc.read_tglc_lightcurve(s3_location, flux_column='CAL_APER_FLUX') 

    return lc