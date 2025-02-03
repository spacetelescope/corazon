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


def run_write_one(ticid, s3_location, sector, out_dir, lc_author = 'TGLC', config_file = None, run_tag = None, local=True, plot=False):
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
    
    if not local:
        fs = s3fs.S3FileSystem(anon=False, profile="default")
    else:
        fs = LocalFileSystem()

    vetter_list = [vetters.LeoTransitEvents(), vetters.Sweet(), vetters.TransitPhaseCoverage()]
    
    
    target_dir = "/tic%09is%02i/" % (int(ticid), sector)
    log_name = out_dir + target_dir + "tic%09i-%s.log" % (ticid, run_tag)
    output_file = out_dir + target_dir + "tic%09i-%s-tcesum.csv" % (ticid, run_tag)
    
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
        
    try:
        
        lcdata = genlc.tglc_from_S3(s3_location)
        
        tce_list, result_strings, metrics_list = pipeline.search_and_vet_one(ticid, sector, lcdata, config, vetter_list, plot=plot)

        if plot:
            plotfilename = "tic%09i-%s-plot.png" % (ticid, 
                                                    run_tag)
            plt.savefig(out_dir + target_dir + plotfilename, bbox_inches='tight')
            plt.close()
        
        with fs.open(output_file, 'w') as fp: 
            for i,r in enumerate(result_strings):
                newstr = ", %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f\n" % (metrics_list[i]['MES'],
                                           metrics_list[i]['SHP'],
                                           metrics_list[i]['CHI'],
                                           metrics_list[i]['med_chases'],
                                           metrics_list[i]['mean_chases'],
                                           metrics_list[i]['mean_chases'],
                                           metrics_list[i]['max_SES'],
                                           metrics_list[i]['DMM'],
                                           metrics_list[i]['amp'][2][0], # last array in Sweet (amplitude to uncertainty ratio): half-period
                                           metrics_list[i]['amp'][2][1], # period
                                           metrics_list[i]['amp'][2][2], # twice the period
                                           metrics_list[i]['transit_phase_coverage'],
                                           metrics_list[i]['snr'])
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

    except Exception as e:
        with fs.open(log_name,'w') as fp:
            fp.write("Failed to create TCEs for TIC %i for Sector %i \n" % (ticid, sector))
            fp.write(str(e))
            return ["failed", output_file, str(e)]

def load_def_config():
    """
    Get the default configuration dictionary.
    Returns
    -------
    config : dict
       dictionary of default values that are required to run corazon pipeline

    """
    
    config = dict()
    
    config = {
        "det_window" : 95,  #window used for detrending
        "noise_window" : 19, #window used for running outlier rejection
        "n_sigma" : 4.5,  #noise/outlier reject sigma
        "max_period_days" : 11,
        "min_period_days" : 0.8,
        "bls_durs_hrs" : [1,2,4,8,12,14],
        "minSnr" : [1],
        "maxTces" : 20,
        "fracRemain" : 0.7
        }
    
    return config