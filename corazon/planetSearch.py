#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  9 16:47:22 2019

@author: smullally
"""

from astropy.timeseries import BoxLeastSquares
import numpy as np
from astropy.convolution import convolve, Box1DKernel
from corazon import plateau

import matplotlib.pyplot as plt


def clean_timeseries(time, flux, qflags, sector):
    
    # plt.figure(figsize=(8,4))
    # plt.plot(time, flux)
    # plt.title('input')
    # plt.show()
    
    qbad = qflags != 0
    tgaps = loadGapInfoBySector(time,sector)
    
    flagged = qbad | tgaps  # Indicate bad data

    good_time = time[~flagged]
    good_flux = flux[~flagged]-1 # subtract 1 to make it zero centered
    
    # plt.figure(figsize=(8,4))
    # plt.plot(good_time, good_flux)
    # plt.title('quality flag removed/ gaps removed')
    # plt.show()
    
    return good_time, good_flux

def loadGapInfoBySector(time, sector):
    """Loads a list of bad cadence indices.

    TESS produces quality flags, but  does not populate the FFIs with them.
    Instead we have to look the up in the data release notes.

    Based on the Data release notes, but modified by hand based on
    inspection of Wasp 126

    Inputs
    ---------
    time
        (1d np array) Array of TJDs for the data. See `extractlc.loadSingleSector`.
    sector
        (int)

    Returns
    -----------
    1d boolean np array of length time
    """
    gaps = np.zeros_like(time, dtype=bool)

    if sector == 1:
        # See page 2 of
        #https://archive.stsci.edu/missions/tess/doc/tess_drn/tess_sector_01_drn01_v01.pdf
        gaps |= (time <= 1325.61)
        gaps |= (1338.52153 <= time) & (time <= 1339.65310)  #Inter orbit gap
        gaps |= (1346.95 <= time) & (time <= 1349.75)  #See DRN 1 p3
        gaps |= (time >= 1352.92)  #End of sector usually bad.
    elif sector == 2:
        gaps |= (1367.15347 <= time) & (time <= 1368.59406)  #
    elif sector == 3:
        gaps |= (1381.1 <= time) & (time <= 1385.89663)  #Pre "science start"
        gaps |= (1394.47997 <= time) & (time <= 1395.80497)  #apears to be bad??
        gaps |= (1395.47997 <= time) & (time <= 1396.60497)  #Inter orbit gap
        gaps |= (1406.2 <= time) & (time <= 1409.38829)  #Post science
    elif sector == 4:
        #The bad guide star data may still be usable. Need to check
        gaps |= (1410.89974 <= time) & (time <= 1413.26468)  #Bad Guide star
#        gaps |= (1418.53691 <= time) & (time <= 1421.86)  #Instr. Anom.
#        gaps |= (1422.95 <= time) & (time <= 1424.54897)  #Inter orbit gap
        gaps |= (1418.53691 <= time) & (time <= 1424.54897)
        gaps |= (1436.0 <= time) & (time <= 1439.8)  #Not sure what this is
    elif sector == 5:
        gaps |= (1450.01 <= time) & (time <=  1451.81)  #Inter orbit gap
        #I don't think this means the data is generally bad
        gaps |= (1463.55 <= time) & (time <= 1464.40056)  #Camera 1 guiding
    elif sector == 6:
        gaps |= (1477.0 <= time) & (time <= 1478.41)  #inter orbit gap
        gaps |= (1463.6 <= time) & (time <= 1468.26998)  #before beginning of 6
    elif sector == 7:
        #gaps |= (1517 <= time) & (time <= 1491.62) # orbit range
        gaps |= (1502.5 <= time) & (time <= 1505.01) #inter sector gap
    elif sector == 14:
        gaps |= (1696.2 <= time) & (time <= 1697.2) #inter sector gap
        #gaps |= gaps
    elif sector == 15:
        gaps |= (1723.25 <= time) & (time <= 1725.6)
        gaps |= (1736.01 <= time)
    elif sector == 16:
        gaps |= (1738.65 >= time) 
        gaps |= (time >= 1763.31) # orbit range
        gaps |= (1750.25 <= time) & (time <= 1751.659) #inter sector gap
    elif sector == 26 :
        gaps |= (2010.26209 >= time)
        gaps |= (time >= 2035.1343)
        gaps |= (2021.482 <= time) & (time <= 2023.28936)        

#        gaps |= (<= time) & (time <= )  #

    else:
        gaps = gaps
    # else:
    #     raise ValueError("No gap info available for sector %i" %(sector))

    return gaps
    

def median_subtract(flux, window):
    """
    Fergal's code to median detrend. 
    """
    size = len(flux)
    nPoints = window
    
    filtered = np.zeros(size)
    for i in range(size):
        #This two step ensures that lwr and upr lie in the range [0,size)
        lwr = max(i-nPoints, 0)
        upr = min(lwr + 2*nPoints, size)
        lwr = upr- 2*nPoints

        sub = flux[lwr:upr]

        offset = np.median(sub)
        try:
            filtered[i] = flux[i] - offset
        except ZeroDivisionError:
                filtered[i] = 0

    return filtered


def calcBls(flux,time, bls_durs, minP=None, maxP=None, min_trans=3):
    """
    Take a bls and return the spectrum.
    """
    
    bls = BoxLeastSquares(time, flux)
    period_grid = bls.autoperiod(bls_durs,minimum_period=minP, \
                   maximum_period=maxP, minimum_n_transit=min_trans, \
                   frequency_factor=0.8)
    
    bls_power = bls.power(period_grid, bls_durs, oversample=20)
    
    return bls_power

def findBlsSignal(time, flux, bls_durations, minP=None, maxP=None, min_trans=3):
    
    bls_power = calcBls(flux, time, bls_durations, minP=minP, maxP=maxP, min_trans=min_trans)
    
    index = np.argmax(bls_power.power)
    bls_period = bls_power.period[index]
    bls_t0 = bls_power.transit_time[index]
    bls_depth = bls_power.depth[index]
    bls_duration = bls_power.duration[index]
    bls_snr = bls_power.depth_snr[index]
    
    return np.array([bls_period, bls_t0, bls_depth, bls_duration, bls_snr])
 
def simpleSnr(time,flux,results):
    """
    calculate a simple snr on the planet based on the depth and scatter
    after you remove the planet model from the data and meidan detrend.
    """
    
    model = BoxLeastSquares(time,flux)
    fmodel =  model.model(time,results[0],results[3],results[1])
    flatten = median_subtract(flux-fmodel, 12)
    
    noise = np.std(flatten)
    snr = results[2]/noise
    
    return snr

   
def identifyTces(time, flux, bls_durs_hrs=[1,2,4,8,12], minSnr=3, fracRemain=0.5, \
                 maxTces=10, minP=None, maxP=None):
    """
    Find highest point in the bls.
    remove that signal, median detrend again
    Find the next signal.
    Stop when less than half the original data set remains.
    Or, when depth of signal is less than snr*running_std 
    
    returns period, t0, depth, duration, snr for each signal found.
    """
    
    keepLooking = True
    counter = 0
    results = []
    stats = []
    bls_durs_day=np.array(bls_durs_hrs)/24
    
    t=time.copy()
    f=flux.copy()
    

    while keepLooking:
        
        bls_results = findBlsSignal(t, f, bls_durs_day, minP=minP, maxP=maxP)
        #print(bls_results)
        #simple ssnr because the BLS depth snr is acting strangely
        bls_results[4] = simpleSnr(t, f, bls_results)
        
        
        results.append(bls_results)
        bls = BoxLeastSquares(t,f)
        bls_stats = bls.compute_stats(bls_results[0], bls_results[3],bls_results[1])
        stats.append(bls_stats)
        #signal_snr = bls_stats['depth'][0]/bls_stats['depth'
        transit_mask = bls.transit_mask(t, bls_results[0],\
                                        bls_results[3]*1.1, bls_results[1])
        #plt.figure()
        #plt.plot(t,f,'ko',ms=3)
        
        t=t[~transit_mask]
        f=f[~transit_mask]
        
        #plt.plot(t,f,'r.')
        #Conditions to keep looking
        if (len(t)/len(time) > fracRemain) & \
               (bls_results[4] >= minSnr) & \
               (counter <= maxTces) :
                
            counter=counter + 1
            keepLooking = True
            
        else:          
            keepLooking = False
 

    return np.array(results), np.array(stats)