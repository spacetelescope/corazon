import corazon.pipeline as pipeline
from datetime import datetime
import os
from exovetter import vetters
import matplotlib.pyplot as plt
#sys.path[2] = '/Users/smullally/Python_Code/lightkurve/lightkurve'


def run_write_one(ticid, sector, out_dir, lc_author = 'qlp',
               run_tag = None, config_file = None, plot=False):
    """
    Run the full bls search on a list of ticids stored in a file.

    Parameters
    ----------
    ticid : int
       tess input catalog number
    sector : int
       tess sector to search
    out_dir : string
        directory to store all the results. One dir per ticid will be created.
    lc_author : string
        'qlp' or 'tess-spoc'
    run_tag : string, optional
        directory name and string to attach to output file names. 

    Returns
    -------
    None.

    """
    
    if run_tag is None:
        now = datetime.now()
        run_tag = now.strftime("crz%m%d%Y")
    
    if config_file is None:
        config = load_def_config()
    else:
        print("Not implememted read in config file")
        #config = pipeline.load_config_file()
    
    vetter_list = load_def_vetter()
    thresholds = load_def_thresholds()
    
    
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
        tce_list, result_strings, metrics_list = pipeline.search_and_vet_one(ticid, 
                                sector, lc_author, config, 
                                vetter_list, thresholds, plot=plot)
        
        if plot:
            plotfilename = "tic%09i-%s-plot.png" % (ticid, 
                                                    run_tag)
            plt.savefig(out_dir + target_dir + plotfilename, bbox_inches='tight')
            plt.close()
        
        output_obj = open(output_file, 'w')
        for r in result_strings:
            output_obj.write(r)
    
        output_obj.close()
    
        for tce in tce_list:
            tcefilename = "tic%09i-%02i-%s.json" % (ticid, 
                                                    int(tce['event']), 
                                                    run_tag)
    
            full_filename = out_dir + target_dir + tcefilename
            tce.to_json(full_filename)
 

        log_obj = open(log_name, 'w+')
        log_obj.write("Success.")
        log_obj.close()

    except Exception as e:
        log_obj = open(log_name,'w+')
        log_obj.write("Failed to create TCEs for TIC %i for Sector %i" % (ticid, sector))
        log_obj.write(str(e))
        log_obj.close() 

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
        "det_window" : 65,
        "noise_window" : 27,
        "n_sigma" : 4.5,  #noise reject sigma
        "max_period_days" : 10,
        "min_period_days" : 0.8,
        "bls_durs_hrs" : [1,2,4,8,12],
        "minSnr" : [1],
        "maxTces" : 20,
        "fracRemain" : 0.7
        }
    
    return config
    
def load_def_vetter():
    """
    Load default vetter list of vetters to run.
    """
    
    vetter_list = [vetters.Lpp(),
                   vetters.OddEven(),
                   vetters.TransitPhaseCoverage(),
                   vetters.Sweet()]
    
    return vetter_list

def load_def_thresholds():
    """
    Load a dictionary of the default threshold values for the vetters.

    Returns
    -------
    thresholds : dict

    """
    thresholds = {'snr' : 1,
              'norm_lpp' : 2.0,
              'tp_cover' : 0.6,
              'oe_sigma' : 3,
              'sweet' : 3}

    return thresholds