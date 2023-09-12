import os 
import pickle
import numpy as np
import matplotlib.pyplot as plt
from utils import expand_to_valid_dets, get_spec_precisions
import pytz
from suntime import Sun

def do_plot(spec_prec_thresh=1):
    ds = {'short_name': 'brazil', 'name': 'Brazil', 'mins_per_f': 1}

    # Load all detections
    comb_data_dir = 'combined_detection_data'
    comb_dets_path = os.path.join(comb_data_dir, '{}_combined_dets_0-8_thresh.pickle'.format(ds['short_name']))
    with open(comb_dets_path, 'rb') as f_handle:
        all_f_dets = pickle.load(f_handle)

    all_valid_dets = expand_to_valid_dets(all_f_dets)

    # Load precision per species from annotation data and filter species based on precision threshold
    annotated_xlsx_path = os.path.join('precision_labelled_data', '{}_labelled_clips.xlsx'.format(ds['short_name']))
    bars, labs = get_spec_precisions(annotated_xlsx_path)
    unq_specs = []
    for lab_ix, lab in enumerate(labs):
        if bars[lab_ix][0] >= spec_prec_thresh: unq_specs.append(lab)

    unq_specs = np.asarray(unq_specs)
    all_det_specs = np.asarray([d['common_name'] for d in all_valid_dets])

    # Get times in local timezones (default is UTC)
    all_det_hrs_local_tz = np.asarray([d['det_dt'].astimezone(pytz.timezone('Brazil/East')).hour for d in all_valid_dets])
    all_det_dts_local_tz = np.asarray([d['det_dt'].astimezone(pytz.timezone('Brazil/East')) for d in all_valid_dets])

    # Get sunrise and sunset times at the middle of the recording period
    mid_dt = sorted(all_det_dts_local_tz)[int(len(all_det_dts_local_tz)/2)]
    nom_lat_long = [-2.080786484477367, -47.48532049576227]
    sunrise_calc = Sun(nom_lat_long[0], nom_lat_long[1])
    sunrise_time = sunrise_calc.get_local_sunrise_time(mid_dt).astimezone(pytz.timezone('Brazil/East'))
    sunset_time = sunrise_calc.get_local_sunset_time(mid_dt).astimezone(pytz.timezone('Brazil/East'))
    print('{}: sunrise at {}, sunset at {}'.format(mid_dt.strftime('%Y-%m-%d'), sunrise_time.strftime('%H:%M'), sunset_time.strftime('%H:%M')))

    # Get activity data by hour for each species
    y_ticks = np.asarray(range(len(unq_specs))) * 1.2
    plt_data = []
    max_activity_hrs = []
    for spec in unq_specs:
        match_det_ixs = np.where((all_det_specs == spec))[0]
        match_det_hrs = all_det_hrs_local_tz[match_det_ixs]

        hist_data, hist_bins = np.histogram(np.asarray(match_det_hrs), np.asarray(range(25)))
        hist_data = hist_data / np.max(hist_data)

        max_activity_hrs.append(np.argmax(hist_data))
        plt_data.append(hist_data)

    plt_data = np.asarray(plt_data)

    # We want to sort species by the hour that they are most active in the plot
    sort_ix = np.argsort(max_activity_hrs)[::-1]
    unq_specs = unq_specs[sort_ix]
    plt_data = plt_data[sort_ix, :]

    # Draw lines for each hour and each species
    [plt.gca().axvline(x, alpha=0.1, c='k', ls='--', linewidth='1') for x in range(24)]
    [plt.gca().axhline(y, alpha=0.1, c='k', ls='--', linewidth='1') for y in y_ticks]

    # Fill in colours for daytime and night time hours
    _ylim = [-0.5, np.max(y_ticks)+2]
    sunrise_dec = sunrise_time.hour + (sunrise_time.minute/60)
    sunset_dec = sunset_time.hour + (sunset_time.minute/60)
    plt.gca().fill_betweenx(_ylim, 0, sunrise_dec, facecolor='#13385C', alpha=0.2)
    plt.gca().fill_betweenx(_ylim, sunrise_dec, sunset_dec, facecolor='#FFFF99', alpha=0.2, label='Day')
    plt.gca().fill_betweenx(_ylim, sunset_dec, 24, facecolor='#13385C', alpha=0.2, label='Night')
    plt.gca().set_ylim(_ylim)

    # Plot detection density per species
    for plt_ix, plt_d in enumerate(plt_data):
        lab = 'Detection density' if plt_ix == 0 else None
        plt.plot(range(24), plt_d + y_ticks[plt_ix], label=lab, c='k')

    # Plot labels/formatting etc
    plt.legend(framealpha=1, loc='best')
    plt.yticks(y_ticks, unq_specs)
    plt.xticks([0, 6, 12, 18, 23])
    plt.ylabel('Species\nHourly vocal activity')
    plt.xlabel('Hour of day')
    plt.xlim([0,23])
    
    plt.tight_layout()



if __name__ == '__main__':
    plt.figure(figsize=((8,4)))
    do_plot()
    plt.savefig(os.path.join('figs', 'fig_3_brazil_diurnal.png'))   
    plt.show()
