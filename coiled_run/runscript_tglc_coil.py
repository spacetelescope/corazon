from script_run_tglc_pl_coil import wrapped_runone_s3_search, runone_s3_search
import pandas as pd
import ast
import re

df = pd.read_csv('kic_s3_paths.csv', nrows=10000)
df['s3_paths'] = df['s3_paths'].apply(ast.literal_eval)
df['sectors'] = df['sectors'].apply(ast.literal_eval)

tics = df['TIC']
s3_paths = df['s3_paths']

targetinfo = []
# Create a list of lists called targetinfo
# This is a list of lists with the TIC, s3 location, and sector
for i, row in enumerate(df['s3_paths']):
    tic = df['TIC'][i]
    for s3_path in row: 
        s3p = s3_path
        info = [tic, s3p, int(s3p[33:35])]
        targetinfo.append(info)
print(len(targetinfo))

#%%
# targetinfo = [[270860359,
#   's3://stpubdata/mast/hlsp/tglc/s0014/cam2-ccd4/0020/7819/9232/7496/hlsp_tglc_tess_ffi_gaiaid-2078199232749616512-s0014-cam2-ccd4_tess_v1_llc.fits',
#   14],[270860359,
#   's3://stpubdata/mast/hlsp/tglc/s0014/cam2-ccd4/0020/7819/9232/7496/hlsp_tglc_tess_ffi_gaiaid-2078199232749616512-s0014-cam2-ccd4_tess_v1_llc.fits',
#   14]]

#%%
#Run One
num=10
#result = runone_s3_search(targetinfo[num])

#%%

#Run Many with coiled

search_result = list(wrapped_runone_s3_search.map(targetinfo[1000:10000]))



#%%
import itertools
import matplotlib.pyplot as plt
import numpy as np
from astropy.table import QTable
flatresults = list(itertools.chain.from_iterable(search_result))
df = QTable(flatresults).to_pandas()
#ah = plt.hist(df['period'],300)

#ah = plt.hist(df['snr'],np.arange(0,20,.5))
#plt.xlim(0,20)

plt.figure()
want = df['sector'] == 15
ah = plt.hist(df[want]['snr'], np.arange(0,15,0.2), label='sector 15',histtype='step')
want = df['sector'] == 14
ah = plt.hist(df[want]['snr'], np.arange(0,15,0.2), label='sector 14',histtype='step')
plt.legend()
plt.close()
# %%
