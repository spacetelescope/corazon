#%%
import dask
from dask import delayed
import pandas as pd
import ast
import re
from corazon import run_pipeline
import coiled
#%%
# Read in first 1000 TICs of the 200,000
""" df = pd.read_csv('kic_s3_paths.csv', nrows=1000)
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
 """
# Set up a BLS config
# config = {
#     "max_period_days": 12,
#     "min_period_days": 0.6,
#     "bls_durs_hrs": [1, 2, 4, 8, 12, 14],
#     "minSnr": [1],
#     "maxTces": 6,
#     "fracRemain": 0.7
# }



#%%
#I have verified that genlc works to get tglc data from s3.

def runone_s3_search(tinfo):
    try:
        run_tag =  '20250428'
        lc_author = 'TGLC'
        out_dir = 'corazon-search-2025/search-test'
        sector = tinfo[2]
        tic = tinfo[0]
        s3_path = tinfo[1]
        config = {
                "max_period_days": 12,
                "min_period_days": 0.8,
                "bls_durs_hrs": [1, 2, 4, 8, 12],
                "minSnr": [1],
                "maxTces": 6,
                "fracRemain": 0.7
            }
        result = my_run_write_one(ticid=tic, 
                                            s3_location=s3_path, 
                                   run_tag=run_tag, 
                                   lc_author=lc_author,
                               sector=sector, config_file=config,
                            local=False,
                            out_dir=out_dir, plot=False)

    except Exception as e:
        return str(e)
    
    return result


@coiled.function()
def wrapped_runone_s3_search(tinfo):
    try:
        run_tag =  '20250428'
        lc_author = 'TGLC'
        out_dir = 'corazon-search-2025/search-test'
        sector = tinfo[2]
        tic = tinfo[0]
        s3_path = tinfo[1]
        config = {
                "max_period_days": 12,
                "min_period_days": 0.8,
                "bls_durs_hrs": [1, 2, 4, 8, 12],
                "minSnr": [1],
                "maxTces": 6,
                "fracRemain": 0.7
            }
        result = my_run_write_one(ticid=tic, 
                                    s3_location=s3_path, 
                                   run_tag=run_tag, 
                                   lc_author=lc_author,
                               sector=sector, config_file=config,
                            local=False,
                            out_dir=out_dir, plot=False)

    except Exception as e:
        return str(e)
    
    return result

# #%%
# num=2
# result = runone_s3_search(targetinfo[num])

# ###--------
# #%%

# num=10
# search_result = list(wrapped_runone_s3_search.map(targetinfo[0:num]))

#%%
#%%

import corazon.pipeline as pipeline
from datetime import datetime
import os
from exovetter import vetters
import matplotlib.pyplot as plt
import corazon.gen_lightcurve as genlc
import s3fs
import json
from fsspec.implementations.local import LocalFileSystem
from astropy.utils.misc import JsonCustomEncoder
#sys.path[2] = '/Users/smullally/Python_Code/lightkurve/lightkurve'


def my_run_write_one(ticid, s3_location, sector, 
                     out_dir, lc_author = 'TGLC', 
                     config_file = None, run_tag = None, 
                     local=True, plot=False):
    """
    Run the full bls search on a list of ticids stored in a file.

    Parameters
    ----------
    ticid : int
       tess input catalog number
    s3_location : str
        string of MAST s3 location of TGLC lightcurve
    sector : int
       tess sector of the data being used
    out_dir : string
        directory to store all the results. One dir per ticid will be created.
    lc_author : string
        Currently using TGLC lightcurves
    config_file : Dictionary
        Dictionary of gapping values
    run_tag : string, optional
        directory name and string to attach to output file names. 
    local : bool
        Specifies the file system to use
    plot : bool
        create plot of the pre and post cleaned lightcurve corazon ran on
    Returns
    -------
    None.

    """
    
    if run_tag is None:
        now = datetime.now()
        run_tag = now.strftime("crz%m%d%Y") + "_"+lc_author
    
    if config_file is None:
        config = load_def_config()
    else:
        config = config_file
    
    if not local:
        fs = s3fs.S3FileSystem(anon=False)
    else:
        fs = LocalFileSystem()
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        try:
            os.mkdir(out_dir+target_dir)   
        except FileExistsError:
            pass
        except PermissionError as e:
            log_obj = open(log_name,'w+')
            log_obj.write("Permission Error on Target Directory ")
            log_obj.write(e)
            log_obj.close()

    vetter_list = [vetters.LeoTransitEvents(), vetters.Sweet(), vetters.TransitPhaseCoverage()]
    
    
    target_dir = "/tic%09is%02i/" % (int(ticid), sector)
    log_name = out_dir + target_dir + "tic%09i-%s.log" % (ticid, run_tag)
    output_file = out_dir + target_dir + "tic%09i-%s-tcesum.csv" % (ticid, run_tag)


    try:
        
        lcdata = genlc.tglc_from_S3(s3_location)
        
        tce_list, result_strings, metrics_list = pipeline.search_and_vet_one(ticid, sector, 
                                                                                lcdata, config, 
                                                                                vetter_list, 
                                                                                plot=plot)
        print(result_strings)

        print("I did a search")
        
        if plot:
        
            plotfilename = "tic%09i-%s-plot.png" % (ticid, 
                                                    run_tag)
            #plotfilename = "s3://" + out_dir + target_dir + plotfilename
            plotfilename = out_dir + target_dir + plotfilename 
            print(f"Writing to {plotfilename}")
            with fs.open(plotfilename, 'wb') as fp:
                plt.savefig(fp, bbox_inches='tight')
        


        with fs.open(output_file, 'w') as fp: 
            fp.write('Target, BLS_event, Sector, BLS_period, BLS_epoch, BLS_depth, BLS_duration, BLS_snr, LEO_MES, LEO_SHP, LEO_CHI, LEO_med_chases, LEO_mean_chases, LEO_max_SES, LEO_DMM, SWEET_halfperiod, SWEET_period, SWEET_2period, transit_phase_coverage\n')
            for i,r in enumerate(result_strings):
                newstr = ", %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f\n" % (metrics_list[i]['MES'],
                                            metrics_list[i]['SHP'],
                                            metrics_list[i]['CHI'],
                                            metrics_list[i]['med_chases'],
                                            metrics_list[i]['mean_chases'],
                                            metrics_list[i]['max_SES'],
                                            metrics_list[i]['DMM'],
                                            metrics_list[i]['amp'][2][0], # last array in Sweet (amplitude to uncertainty ratio): half-period
                                            metrics_list[i]['amp'][2][1], # period
                                            metrics_list[i]['amp'][2][2], # twice the period
                                            metrics_list[i]['transit_phase_coverage'])
                newr = r[:-1]+newstr
                fp.write(newr)
        
        #Write TCEs
        for tce in tce_list:
            tcefilename = "tic%09i-%02i-%s.json" % (ticid, 
                                                    int(tce['event']), 
                                                    run_tag)

            full_filename = out_dir + target_dir + tcefilename
            tce['lc_author'] = lc_author
            with fs.open(full_filename, 'w') as fp:
                json.dump(tce, fp, cls=JsonCustomEncoder)

        with fs.open(log_name, 'w') as fp:
            fp.write("Success!")
        
        return tce_list

    except Exception as e:
        import traceback
        traceback.print_exc()
        with fs.open(log_name,'w') as fp:
            fp.write("Failed to create TCEs for TIC %i for Sector %i \n" % (ticid, sector))
            fp.write(str(e))
            print(output_file)
            print(str(e))
        raise e

def load_def_config():
    """
    Get the default configuration dictionary.
    Returns
    -------
    config : dict
       dictionary of default values that are required to run corazon pipeline

    """
    
    config = dict()
    
    # Here were the inherited defaults
    config = {
        "max_period_days" : 11,
        "min_period_days" : 0.8,
        "bls_durs_hrs" : [1,2,4,8,12,14],
        "minSnr" : [1],
        "maxTces" : 20,
        "fracRemain" : 0.7
        }
    
    return config
# %%
