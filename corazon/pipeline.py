__all__ = ['search_and_vet_one', 'vet_tce','vet_all_tces']

import corazon.planetSearch as ps
import matplotlib.pyplot as plt
import exovetter.tce as TCE
import astropy.units as u
import exovetter.const as const
import lightkurve as lk


def search_and_vet_one(ticid, sector, lcdata, config, vetter_list, plot=True):
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
    
    # Perform gapping on the light curve:
    time = lcdata['time'].value
    flux = lcdata['flux'].value
    flags = lcdata['quality'].value

    good_time, meddet_flux = ps.clean_timeseries(time, flux, flags,
                                          config["det_window"], 
                                          config["noise_window"], 
                                          config["n_sigma"], 
                                          sector)
        
    # Run BLS
    tce_list, stats = ps.identifyTces(good_time, meddet_flux, 
                                      bls_durs_hrs=config["bls_durs_hrs"],
                                      minSnr=config["minSnr"], 
                                      fracRemain=config["fracRemain"], 
                                      maxTces=config["maxTces"], 
                                      minP=config["min_period_days"], 
                                      maxP=config["max_period_days"])
    
    if plot:
        # plot_lc_tce(ticid, tce_list, time, flux, flags, good_time, meddet_flux, stats, sector)
        plot_lc_tce(ticid, time, flux, good_time, meddet_flux, flags, stats, sector)
    
    lcformat = lcdata['time'].format
    tce_lc = lk.LightCurve(time=good_time, flux=meddet_flux+1, time_format=lcformat, meta={'sector':sector})
    
    result_strings, metrics_list, tce_tces = vet_all_tces(tce_lc, tce_list, ticid, vetter_list, plot=False)
    
    return tce_tces, result_strings, metrics_list

def vet_all_tces(lc, tce_dict_list, ticid, vetter_list, plot=False):
    lcformat = lc['time'].format
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

        metrics = vet_tce(tce, lc, vetter_list, plot=plot) # dictionary of all vetting metrics

        metrics['snr'] = tce['snr']

        result_string = make_result_string(tce)

        tce_list.append(tce)
        result_list.append(result_string)
        metrics_list.append(metrics)
        pn=pn+1
        
    return result_list, metrics_list, tce_list

def vet_tce(tce, tce_lc, vetter_list, plot=False):
    """Create a dictionary with all vetting parameters returned by each vetter in vetter_list"""
    metrics = dict()
    for v in vetter_list:
        vetter = v
        
        try:
            vetter_dict = vetter.run(tce, tce_lc)
        except ValueError:
            print('Did not Vet')
            pass
        if plot:
            vetter.plot()
        metrics.update(vetter_dict)
        
    return metrics

def make_result_string(tce):
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
    st = "%s, %s, %i, %8.4f, %9.4f, %8.3f, %5.3f, %5.2f\n" % \
                                        (tce['target'], tce['event'],
                                               tce['sector'],
                                               tce['period'].value, 
                                               tce['epoch'].value,
                                               tce['depth'].value*1e6,
                                               tce['duration'].value*24.0,
                                               tce['snr'])

    return st

    
def plot_lc_tce(ticid, time, flux, cleaned_time, cleaned_flux, flags, stats, sector):
    col = ['tab:orange','tab:green','tab:purple','tab:brown', 'gold','magenta','lightpink']
    fig, (ax1,ax2,ax3) = plt.subplots(nrows=3,ncols=1,figsize=(10,9))
    
    
    ax1.plot(time, flux, label='Original lc', color='tab:red')
    ax2.plot(cleaned_time, cleaned_flux, label='BLS searched cleaned lc', color='tab:blue')
    ax3.plot(cleaned_time, cleaned_flux, color='tab:blue')
    
    #plt.plot(time[flags!=0], flux[flags!=0],'o', ms=3, label='flagged')

    for n,s in enumerate(stats):
        labeled=False
        for transit_time in stats[n]['transit_times']:
            ax3.axvline(x=transit_time, color=col[n], zorder=1, label=f'BLS TCE {str(n+1)}' if not labeled else '__nolegend__', alpha=0.7, ls='-' if n%2==0 else '--')
            labeled=True


    for ax in (ax1,ax2,ax3):
        ax.legend()
    
    fig.suptitle("Lightcurve for TIC %i in S%i" % (int(ticid), int(sector)))

def open_output_file(filename, headerlist):
    fobj = open(filename, 'a')

    header = headerlist[0]
    for h in headerlist[1:]:
        header = header + ", " + h

    fobj.write(header + '\n')
    
    return fobj