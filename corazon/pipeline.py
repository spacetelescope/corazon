__all__ = ['search_and_vet_one', 'vet_tce','vet_all_tces','get_disposition',
           'load_def_config','load_def_vetter']

import corazon.planetSearch as ps
import corazon.gen_lightcurve as genlc
import matplotlib.pyplot as plt
import exovetter.tce as TCE
import astropy.units as u
import exovetter.const as const
import lightkurve as lk
from exovetter import vetters

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


def search_and_vet_one(ticid, sector, lcdata, config, vetter_list,
                       thresholds, plot=True):
    """
    Search and vet one ticid using config and vetter list
    
    Parameters
    ----------
    ticid : int
         TIC Identification number
    sector : int
        Sector of the TESS data to use for analysis
    lcdata : lightkkurve obect
        time and flux and quality flags populated
    config : dict
        configuration dictionary
    vetter_list : list
        list of vetters from exovetter to run

    Returns
    -------
    tce_tces : list
        list of exovetter TCEs for this target
    result_strings : str
       string version of tce and decision
      
    metrics_list : list
        all metrics, one per tce

    
    """
    
    time = lcdata['time'].value
    flux = lcdata['flux'].value
    flags = lcdata['quality']

    good_time, meddet_flux = ps.clean_timeseries(time, flux, flags,
                                          config["det_window"], 
                                          config["noise_window"], 
                                          config["n_sigma"], 
                                          sector)
        
    
    tce_list, stats = ps.identifyTces(good_time, meddet_flux, 
                                      bls_durs_hrs=config["bls_durs_hrs"],
                                      minSnr=config["minSnr"], 
                                      fracRemain=config["fracRemain"], 
                                      maxTces=config["maxTces"], 
                                      minP=config["min_period_days"], 
                                      maxP=config["max_period_days"])
    
    if plot:
        plot_lc_tce(ticid, tce_list, time, flux, good_time, meddet_flux, stats)
    
    lcformat = lcdata['time'].format
    tce_lc = lk.LightCurve(time=good_time, flux=meddet_flux+1,
                        time_format=lcformat, meta={'sector':sector})
    
    result_strings, disp, reason, metrics_list, tce_tces = vet_all_tces(tce_lc, 
                                                    tce_list, ticid, 
                                                    vetter_list, thresholds,
                                                    plot=False)
    
    return tce_tces, result_strings, metrics_list


def vet_tce(tce, tce_lc, vetter_list, plot=False):

    metrics = dict()
    for v in vetter_list:
        vetter = v
        
        try:
            _ = vetter.run(tce, tce_lc)
        except ValueError:
            pass
        if plot:
            vetter.plot()
        metrics.update(vetter.__dict__)
        
    return metrics

def get_disposition(metrics, thresholds):
    """Apply thresholds to get a passfail"""
    
    disp = 'PASS' 
    reason = ''
    if metrics['snr'] < thresholds['snr']:
        disp = 'FAIL'
        reason = reason + "-LowSNR-"
    if metrics['norm_lpp'] > thresholds['norm_lpp']:
        disp = 'FAIL'
        reason = reason + "-NormLPP-"
    if metrics['tp_cover'] < thresholds['tp_cover']:
        disp = 'FAIL'
        reason = reason + "-PoorTransitCoverage-"
    if metrics['oe_sigma'] > thresholds['oe_sigma']:
        disp = 'FAIL'
        reason = reason + "-OddEvenDetected-"
    if metrics['sweet']['amp'][0, -1] > thresholds['sweet']:
        disp = 'FAIL'
        reason = reason + "-SWEETHalfPeriod"
    if metrics['sweet']['amp'][1, -1] > thresholds['sweet']:
        disp = 'FAIL'
        reason = reason + "-SWEETAtPeriod"
    if metrics['sweet']['amp'][2,-1] > thresholds['sweet']:
        disp = 'FAIL'
        reason = reason + "-SWEETTwicePeriod-"
    
    
    return disp,reason
    
def make_result_string(tce, disposition, reason):
    """
   Create a string that summarizes the TCE and its disposition
    Parameters
    ----------
    tce : TYPE
        DESCRIPTION.
    disposition : string
        DESCRIPTION.
    reason : string
        DESCRIPTION.

    Returns
    -------
    None.

    """
    st = "%s, %s, %i, %8.4f, %9.4f, %8.3f, %5.3f, %5.2f, %s, %s\n" % \
                                        (tce['target'], tce['event'],
                                               tce['sector'],
                                               tce['period'].value, 
                                               tce['epoch'].value,
                                               tce['depth'].value*1e6,
                                               tce['duration'].value*24.0,
                                               tce['snr'],
                                               disposition, reason)             
    return st


def vet_all_tces(lc, tce_dict_list, ticid, vetter_list, thresholds, plot=False):
    lcformat = lc['time'].format
    disp_list = []
    reason_list = []
    result_list = []
    metrics_list = []
    tce_list = []
    pn = 1
    for item in tce_dict_list:
        tce = TCE.Tce(period = item[0]*u.day, epoch=item[1]*u.day, 
                      depth=item[2] * const.frac_amp,
                      duration=item[3]*u.day, 
                      epoch_offset=const.string_to_offset[lcformat],
                      snr=item[4],
                      target = f"TIC {ticid}",
                      sector = lc.sector,
                      event = f"{pn}")
        
        metrics = vet_tce(tce, lc, vetter_list, plot=plot)
        metrics['snr'] = tce['snr']
        disposition, reason = get_disposition(metrics, thresholds)
        result_string = make_result_string(tce, disposition, reason)
        tce['disposition'] = disposition
        tce['reason'] = reason
        tce_list.append(tce)
        disp_list.append(disposition)
        reason_list.append(reason)
        result_list.append(result_string)
        metrics_list.append(metrics)
        pn=pn+1
        
        
    return result_list, disp_list, reason_list, metrics_list, tce_list

    
def plot_lc_tce(ticid, tce_list, time, flux, good_time, good_flux, stats):
    col = ['tab:orange','tab:green','tab:purple','tab:brown',
               'gold','magenta','lightpink']
    plt.figure(figsize=(10,6))
    plt.subplot(211)
    plt.plot(good_time, good_flux,'.')
    plt.title("Lightcurve for TIC %i" % int(ticid))
   
    axes = plt.gca()
    y_min, y_max = axes.get_ylim()
    for n,s in enumerate(stats):
        plt.vlines(stats[n]['transit_times'], y_min, y_max, 
                   colors=col[n], zorder=1, label=str(n+1))
    plt.legend()
    plt.subplot(212)
    plt.plot(time, flux,'.', label="original lc")
    plt.legend()

def open_output_file(filename, headerlist, thresholds):
    fobj = open(filename, 'a')
    
    fobj.write("# thresholds: " + str(thresholds)+"\n")
    
    header = headerlist[0]
    for h in headerlist[1:]:
        header = header + ", " + h
        
    fobj.write(header + '\n')
    
    return fobj

