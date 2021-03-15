#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 16:47:59 2021

@author: smullally
"""
from corazon import run_pipeline
import numpy as np

filename = "/Users/smullally/Science/tess_false_alarms/keplerTargets/target_selection/rsync_target_lists/qlpFilenames_noebplanets_mag13.txt"
filelist = list(np.loadtxt(filename, dtype=str))

num = 20

outdir = "/Users/smullally/Science/tess_false_alarms/vet_results/March122021/"
run_tag = "2021Mar12qlp"

for file in filelist[0:num]:
    
    sp = file.split("/")[-1].split("_")
    lc_author = sp[1]
    if lc_author == "tess-spoc":
        sector = int(sp[4].split("-")[1][-3:])
        ticid = int(sp[4].split("-")[0])
    if lc_author == "qlp":
        sector = int(sp[4].split("-")[0][-3:])
        ticid = int(sp[4].split("-")[1])
        
    run_pipeline.run_write_one(ticid, sector, outdir, lc_author=lc_author,
                               plot=True, run_tag = run_tag)
    

#%%
    
    
    
    