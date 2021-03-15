import corazon.pipeline as pipe
import lightkurve as lk


def test_pipeline_1():
    # TODO: Implement me
    ticid = 377780790
    sector = 14
    
    lcdata =lk.search_lightcurve("Kepler-10", mission='TESS',sector=14)[0].download()
    
    config = pipe.load_def_config()
    vetter_list = pipe.load_def_vetter()
    thresholds = {'snr' : 1,
              'norm_lpp' : 2.0,
              'tp_cover' : 0.6,
              'oe_sigma' : 3,
              'sweet' : 3}
    
    tce_tces, result_strings, metrics_list = pipe.search_and_vet_one(ticid, 
                        sector, lcdata, config, vetter_list,
                        thresholds, plot=False)
    
    assert lk.__version__ =='2.0b5'
    assert tce_tces[0]['snr']< 1
    
    

import corazon.simulate as sim

def test_simulate_1():
    numberlc = 5
    noise_range = [100, 200]
    outputfilename = None
    results, tces = sim.simulate_gaussian_tces(numberlc, noise_range, outputfilename)
    
    assert len(results) == numberlc
    assert len(tces) == numberlc