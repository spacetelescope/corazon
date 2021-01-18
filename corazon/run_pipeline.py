import corazon.pipeline as pipeline
from datetime import datetime
import os

def run_write_one(ticid, sector, out_dir, lc_author = 'qlp',
               run_tag = None, config_file = None):
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
        'qlp' or 'spoc'
    run_tag : string, optional
        directory name and string to attach to output file names. 

    Returns
    -------
    None.

    """
    
    if run_tag is None:
        now = datetime.now()
        run_tag = now.strftime("crz%m%d%Y%H%M")
    
    if config_file is None:
        config = pipeline.load_def_config()
    else:
        print("Not implememted read in config file")
        #config = pipeline.load_config_file()
    
    vetter_list = pipeline.load_def_vetter()
    
    output_file = out_dir + run_tag + ".log"
    output_obj = open(output_file, 'w')
    
    target_dir = "/tic%09i/" % int(ticid)
    log_name = out_dir + target_dir + "tic%09i_%s.log" % run_tag
    
    if ~os.path.exists(out_dir):
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
                                vetter_list, plot=False)
        
        for r in result_strings:
            output_obj.write(r)
    
        output_obj.close()
    
        for tce in tce_list:
            tcefilename = "tic%09i-%02i-%s.json" % (int(tce['target'][5:]), 
                                                    int(tce['event']), 
                                                    run_tag)
    
            full_filename = out_dir + tcefilename
            tce.to_json(full_filename)
    except:
        log_obj = open(log_name,'w+')
        log_obj.write("Failed to run this TIC ID.")
        log_obj.close() 
