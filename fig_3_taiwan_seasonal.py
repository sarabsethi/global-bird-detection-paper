import os 
import pickle
import numpy as np
import matplotlib.pyplot as plt
from utils import expand_to_valid_dets, get_spec_precisions
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.signal import convolve2d

def do_plot(spec_prec_thresh=1):
    ds = {'short_name': 'taiwan', 'name': 'Taiwan', 'mins_per_f': 5}

    # Plotting this figure takes a while so make a temporary data file so we don't have to repeat every plot
    temp_fig_data_dir = 'temp_fig_data'
    if not os.path.exists(temp_fig_data_dir): os.makedirs(temp_fig_data_dir)
    temp_fig_data_path = os.path.join(temp_fig_data_dir, 'fig3_{}.pickle'.format(ds['short_name']))
    
    # If we've not done the plot before once though we need to churn first...
    if not os.path.exists(temp_fig_data_path):
        print('Loading detections')
        comb_data_dir = 'combined_detection_data'
        comb_dets_path = os.path.join(comb_data_dir, '{}_combined_dets_0-8_thresh.pickle'.format(ds['short_name']))
        with open(comb_dets_path, 'rb') as f_handle:
            all_f_dets = pickle.load(f_handle)

        all_valid_dets = expand_to_valid_dets(all_f_dets)

        print('Getting species precisions')
        annotated_xlsx_path = os.path.join('precision_labelled_data', '{}_labelled_clips.xlsx'.format(ds['short_name']))
        bars, labs = get_spec_precisions(annotated_xlsx_path)
        allowed_specs = []
        for lab_ix, lab in enumerate(labs):
            if bars[lab_ix][0] >= spec_prec_thresh: allowed_specs.append(lab)
        allowed_specs = np.asarray(allowed_specs)

        # Get days on which species were detected
        all_valid_specs = np.asarray([d['common_name'] for d in all_valid_dets])
        all_det_dts = np.asarray([d['det_dt'] for d in all_valid_dets])
        all_det_days = np.asarray([dt.strftime('%Y-%m-%d') for dt in all_det_dts])
        unq_days = np.unique(all_det_days)
        unq_days = sorted(unq_days)

        # Build matrix which summarises occurrence per species per day across all sites
        print('Building detections matrix')
        dets_mat = np.empty((len(allowed_specs), len(unq_days)))
        for spec_ix, spec in enumerate(allowed_specs):
            match_spec_ixs = np.where((all_valid_specs == spec))[0]
            
            for day_ix, day in enumerate(unq_days):
                match_site_ixs = np.where((all_det_days == day))[0]
                match_det_ixs = np.intersect1d(match_spec_ixs, match_site_ixs)

                # We are just concerned with occurrence so 1 if anything detected, 0 if not 
                val = 1 if len(match_det_ixs) > 0 else 0
                dets_mat[spec_ix, day_ix] = val

        with open(temp_fig_data_path, 'wb') as handle:
            pickle.dump([dets_mat, unq_days, allowed_specs], handle)

    else:
        with open(temp_fig_data_path, 'rb') as f_handle:
            dets_mat, unq_days, allowed_specs = pickle.load(f_handle)

    # Cluster species (rows) using hierarchical clustering 
    row_clusters = linkage(pdist(dets_mat, metric='euclidean'), method='complete')
    row_dendr = dendrogram(row_clusters, no_plot=True)
    spec_ord_ix = row_dendr['leaves']
    dets_mat = dets_mat[spec_ord_ix, :]
    allowed_specs = allowed_specs[spec_ord_ix]

    # Smooth data per row - across time - on a weekly timescale
    dets_mat = convolve2d(dets_mat,np.ones((1,7)),'same')
    dets_mat = dets_mat/np.max(dets_mat)

    # Plot data, labels, and formatting etc.
    plt.matshow(dets_mat, aspect='auto', fignum=0, cmap='Blues')
    plt.ylabel('Species')
    plt.xlabel('Date')
    plt.colorbar(label='Smoothed daily occurrence', pad=0.022, fraction=0.07)
    plt.yticks(range(len(allowed_specs)), allowed_specs)

    unq_days_labs = []
    tick_ixs = []
    last_yr_lab = 0
    for d_ix, d in enumerate(unq_days):
        if d[-2:] in ['01']: 
            tick_ixs.append(d_ix)
            unq_days_labs.append('/'.join(d[2:7].split('-')[::-1]))

    plt.xticks(tick_ixs, unq_days_labs, ha='center')
    plt.gca().tick_params(bottom=True, top=False, left=True, right=False)
    plt.gca().tick_params(labelbottom=True, labeltop=False, labelleft=True, labelright=False)
    
    plt.tight_layout()
    

if __name__ == '__main__':
    plt.figure(figsize=((16,6)))
    do_plot()
    plt.savefig(os.path.join('figs', 'fig_3_taiwan_seasonal.png'))
    plt.show()