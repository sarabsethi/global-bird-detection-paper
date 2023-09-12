import os 
import pickle
import numpy as np
import matplotlib.pyplot as plt
from utils import expand_to_valid_dets
from datetime import datetime, timedelta

def do_plot(chosen_spec = 'Willow Warbler'):
    ds = {'short_name': 'norway', 'name': 'Norway', 'mins_per_f': 5}

    # Only look at data between this timeframe (to get relevant part of migration)
    start_dt = datetime(year=2022, month=4, day=30)
    end_dt = datetime(year=2022, month=6, day=15)

    # Load detection data 
    comb_data_dir = 'combined_detection_data'
    comb_dets_path = os.path.join(comb_data_dir, '{}_combined_dets_0-8_thresh.pickle'.format(ds['short_name']))
    with open(comb_dets_path, 'rb') as f_handle:
        all_f_dets = pickle.load(f_handle)

    all_valid_dets = expand_to_valid_dets(all_f_dets)

    # Get detections for chosen species
    all_valid_specs = np.asarray([d['common_name'] for d in all_valid_dets])
    match_spec_dets_ixs = np.where((all_valid_specs == chosen_spec))[0]
    chosen_spec_dets = [d for d in all_valid_dets[match_spec_dets_ixs] if start_dt <= d['det_dt'] <= end_dt]
    chosen_spec_dets = np.asarray(chosen_spec_dets)

    # Get sites and their latitudes where this species was detected
    all_det_sites = np.asarray([d['site'].split(' ')[1] for d in chosen_spec_dets])
    all_det_sites_lats = np.asarray([d['lat'] for d in chosen_spec_dets])

    # Sort sites by latitude
    unq_sites, unq_site_ixs = np.unique(all_det_sites, return_index=True)
    unq_site_lats = all_det_sites_lats[unq_site_ixs]
    sort_ix = np.argsort(unq_site_lats)
    unq_sites = unq_sites[sort_ix][::-1]

    # Get a list of all days in our target period
    unq_days = []
    day_dt = start_dt
    while day_dt <= end_dt:
        unq_days.append(day_dt)
        day_dt += timedelta(days=1)

    # Create an empty matrix that will store calling activity on each site x day
    dets_mat = np.empty((len(unq_sites), len(unq_days)))

    # Populate calling activity matrix
    for site_ix, site in enumerate(unq_sites):
        match_spec_site_det_ixs = np.where((all_det_sites == site))[0]
        spec_site_dets = chosen_spec_dets[match_spec_site_det_ixs]
        spec_site_days = np.asarray([d['det_dt'].strftime('%Y-%m-%d') for d in spec_site_dets])

        cumulative_dets = 0
        cumulative_occs = 0
        for day_ix, day_dt in enumerate(unq_days):
            match_site_spec_day_det_ixs = np.where((spec_site_days == day_dt.strftime('%Y-%m-%d')))[0]
            
            n_dets = len(match_site_spec_day_det_ixs)
            occ = 0 if n_dets == 0 else 1 
            cumulative_dets += n_dets
            cumulative_occs += occ

            # Number of detections is what we measure per day per site
            dets_mat[site_ix, day_ix] = n_dets

    # Normalise matrix by site (row)
    norm_dets_mat = []
    for det_row in dets_mat:
        norm_dets = det_row/np.max(det_row)
        norm_dets_mat.append(norm_dets)

    # Plot normalised detection numbers per site
    norm_dets_mat = np.asarray(norm_dets_mat)
    plt.matshow(norm_dets_mat, aspect='auto', fignum=0, cmap='Blues')
    plt.colorbar(label='Daily vocal activity', pad=0.022, fraction=0.07)
    plt.ylabel('Region\n(ordered by latitude)')
    plt.xlabel('Date')
    plt.title('Norway: {} migration'.format(chosen_spec))
    plt.yticks(range(len(unq_sites)), unq_sites)

    # Plot labels/formatting etc
    unq_days_labs = []
    for d_ix, d in enumerate(unq_days):
        if d_ix%8 == 0: unq_days_labs.append(d.strftime('%d/%m/%Y'))
        else: unq_days_labs.append('')
    plt.xticks(range(len(unq_days_labs)), unq_days_labs)
    plt.gca().tick_params(bottom=True, top=False, left=True, right=False)
    plt.gca().tick_params(labelbottom=True, labeltop=False, labelleft=True, labelright=False)
    
    plt.tight_layout()


if __name__ == '__main__':
    plt.figure(figsize=((16,4)))
    do_plot()
    plt.savefig(os.path.join('figs', 'fig_3_norway_species_arrival_time.png'))   
    plt.show()