import os 
import pickle
import numpy as np
import matplotlib.pyplot as plt
from utils import expand_to_valid_dets, get_opt_spec_bn_threshs
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.signal import convolve2d

def do_plot(spec_prec_thresh=1, force_compute=False):
    ds = {'short_name': 'taiwan', 'name': 'Taiwan', 'mins_per_f': 5}

    temp_fig_data_path = os.path.join('temp_fig_data', 'fig3_{}.pickle'.format(ds['short_name']))

    if not os.path.exists(temp_fig_data_path) or force_compute:

        comb_data_dir = 'combined_detection_data'
        comb_dets_path = os.path.join(comb_data_dir, '{}_combined_dets_0-8_thresh.pickle'.format(ds['short_name']))

        spec_opt_threshs, spec_precisions = get_opt_spec_bn_threshs(ds['short_name'])
        specs = np.asarray(list(spec_opt_threshs.keys()))
        allowed_specs = specs[np.where((spec_precisions >= spec_prec_thresh))[0]]

        print('Loading detections')
        with open(comb_dets_path, 'rb') as f_handle:
            all_f_dets = pickle.load(f_handle)
        all_dets = expand_to_valid_dets(all_f_dets)

        print('Applying species specific optimal thresholds')
        all_valid_dets = []
        for det in all_dets:
            if det['common_name'] in allowed_specs and det['confidence'] > spec_opt_threshs[det['common_name']]:
                all_valid_dets.append(det)

        all_valid_specs = np.asarray([d['common_name'] for d in all_valid_dets])

        all_det_dts = np.asarray([d['det_dt'] for d in all_valid_dets])
        all_det_days = np.asarray([dt.strftime('%Y-%m-%d') for dt in all_det_dts])
        unq_days = np.unique(all_det_days)
        unq_days = sorted(unq_days)

        print('Building detections matrix')
        dets_mat = np.empty((len(allowed_specs), len(unq_days)))
        for spec_ix, spec in enumerate(allowed_specs):
            match_spec_ixs = np.where((all_valid_specs == spec))[0]
            
            for day_ix, day in enumerate(unq_days):
                match_site_ixs = np.where((all_det_days == day))[0]
                match_det_ixs = np.intersect1d(match_spec_ixs, match_site_ixs)

                val = 1 if len(match_det_ixs) > 0 else 0
                dets_mat[spec_ix, day_ix] = val

        with open(temp_fig_data_path, 'wb') as handle:
            pickle.dump([dets_mat, unq_days, allowed_specs], handle)

    else:
        with open(temp_fig_data_path, 'rb') as f_handle:
            dets_mat, unq_days, allowed_specs = pickle.load(f_handle)


    row_clusters = linkage(pdist(dets_mat, metric='euclidean'), method='complete')
    row_dendr = dendrogram(row_clusters, no_plot=True)
    spec_ord_ix = row_dendr['leaves']

    dets_mat = dets_mat[spec_ord_ix, :]
    allowed_specs = allowed_specs[spec_ord_ix]

    dets_mat = convolve2d(dets_mat,np.ones((1,7)),'same')
    dets_mat = dets_mat/np.max(dets_mat)

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