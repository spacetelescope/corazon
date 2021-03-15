#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 29 09:18:01 2020

@author: smullally

Generate light curves. Each function is a different way to generate a light curve.

"""



import lightkurve as lk


def eleanor_pca(ticid, sector, pxsize = 19):
    import eleanor
    star = eleanor.Source(tic = ticid, sector = sector)
    
    data = eleanor.TargetData(star, height=pxsize, width=pxsize, bkg_size=31, 
                              do_psf=False, do_pca=True)
    
    return data.time, data.pca_flux, data.quality

#Could do a single sector FFI light curve wiih lightkurve

def eleanor_corr(ticid, sector, pxsize = 19):
    import eleanor
    star = eleanor.Source(tic = ticid, sector = sector)
    
    data = eleanor.TargetData(star, height=pxsize, width=pxsize, bkg_size=31, 
                              do_psf=False, do_pca=True)
    
    return data.time, data.corr_flux, data.quality


def hlsp(ticid, sector, author="tess-spoc", local_dir = None):
    """
    

    Parameters
    ----------
    ticid : int
        DESCRIPTION.
    sector : int
        Sector of observations to vet
    author : string, OPTIONAL
        options include tess-spoc and tess-qlp.
        The default is "tess-spoc".
    loocaldir : string
        local directory to read from None: Default

    Returns
    -------
    lc : lightkurve object
        lightkurve object of the data requested.

    """
    
    #print(f'TIC {ticid}')
    
    if local_dir is None:
    
        lc = lk.search_lightcurve(f"TIC {ticid}", sector=sector,
                              cadence="ffi",author=author).download()
    else:
        
        filename  = get_hlsp_filename(ticid, sector, author)
        
        lc = lk.io.read(local_dir + "/" + filename)
    
    
    return lc
    

def get_hlsp_filename(ticid, sector, author):
    
    if author == "tess-spoc":
        filename = "hlsp_tess-spoc_tess_phot_%016u-s%04u_tess_v1_lc.fits" % (ticid, sector)
        
    if author == "qlp":
        filename = "hlsp_qlp_tess_ffi_s%04u-%016u_tess_v01_llc.fits" % (sector,ticid)
    
    return filename