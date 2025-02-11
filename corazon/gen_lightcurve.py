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
from astropy.io import fits


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

    fs = s3fs.S3FileSystem(anon=True)

    lc = lk.io.tglc.read_tglc_lightcurve(s3_location)
    
    idx = ~np.isnan(lc['flux'])
    if len(lc['flux'][idx]) == 0: # Ideally use the calibrated psf flux (the default of read_tglc_lightcurve), but if it is all nans use the calibrated aperture flux
        lc = lk.io.tglc.read_tglc_lightcurve(s3_location, flux_column='CAL_APER_FLUX') 
        
        # The calibrated fluxes have nans in the error arrays so populate them with the appropriate header: (see https://iopscience.iop.org/article/10.3847/1538-3881/acaaa7/pdf)
        with fs.open(s3_location, 'rb') as f:
            with fits.open(f) as hdul:
                aper_error = hdul[1].header['CAPE_ERR']
        lc['flux_err'] = aper_error
   
    else:
        with fs.open(s3_location, 'rb') as f:
            with fits.open(f) as hdul:
                psf_error = hdul[1].header['CPSF_ERR']
        lc['flux_err'] = psf_error
    
    # Then remove nans
    lc = lc[~np.isnan(lc["flux"])]

    # This is done later but possible could remove outliers at this high level
    #lc = lc.remove_outliers(sigma_lower=8, sigma_upper=4)

    return lc