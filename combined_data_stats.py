import os 
import pickle 
from utils import expand_to_valid_dets, get_spec_precisions
import numpy as np 

# Number of detections per species 
N_DET_THRESH = 50

# Thresholds of precision for what we consider a "medium" or "high" precision species
MED_SPEC_PREC_THRESH = 0.8
HIGH_SPEC_PREC_THRESH = 1

all_datasets = [{'short_name': 'taiwan', 'name': 'Taiwan'},
                {'short_name': 'norway', 'name': 'Norway', 'mins_per_f': 5},    
                {'short_name': 'costa-rica', 'name': 'Costa Rica', 'mins_per_f': 1},
                {'short_name': 'brazil', 'name': 'Brazil', 'mins_per_f': 1}]

comb_data_dir = 'combined_detection_data'
labelled_data_dir = 'precision_labelled_data'

totals = dict({'hrs': 0, 'sites': 0, 'specs': [], 'valid_specs': [], 'dets': 0, 
               'valid_spec_dets': 0, 'high_prec_specs': [], 'med_prec_specs': [], 'high_prec_dets': 0})

# Loop through datasets counting key stats
for ds in all_datasets:
    comb_dets_path = os.path.join(comb_data_dir, '{}_combined_dets_0-8_thresh.pickle'.format(ds['short_name']))
    annotated_xlsx_path = os.path.join('precision_labelled_data', '{}_labelled_clips.xlsx'.format(ds['short_name']))

    # Load dataset
    with open(comb_dets_path, 'rb') as f_handle:
        all_f_dets = pickle.load(f_handle)

    # Get datetime information 
    all_fd_dts = np.asarray([fd['dt'] for fd in all_f_dets if fd['dt'].year > 1970])
    
    # Get sampling effort (in hours). Taiwan has different times per file, but other datasets are standardised
    if ds['short_name'] == 'taiwan':
        tot_mins = 0
        for f in all_f_dets:
            tot_mins += f['f_len_mins']
        ds_hours = int(np.round(tot_mins / 60))
    else:
        ds_hours = int(np.round(ds['mins_per_f'] * len(all_f_dets) / 60))
    totals['hrs'] += ds_hours

    # Count number of detections
    all_valid_dets = expand_to_valid_dets(all_f_dets)
    totals['dets'] += len(all_valid_dets)

    # Count number of sites
    unq_sites = np.unique([fd['site'] for fd in all_f_dets])
    totals['sites'] += len(unq_sites)

    # Count species
    all_specs = np.asarray([d['common_name'] for d in all_valid_dets])
    unq_specs, unq_spec_inv_ixs, unq_spec_counts = np.unique(all_specs, return_inverse=True, return_counts=True)
    totals['specs'].extend(unq_specs)

    # Count species with more than N_DET_THRESH detections
    unq_valid_spec_ixs = np.where((unq_spec_counts > N_DET_THRESH))[0]
    unq_valid_specs = unq_specs[unq_valid_spec_ixs]
    totals['valid_specs'].extend(unq_valid_specs)

    # Count detections of just the valid species
    valid_spec_dets = np.where((np.isin(unq_spec_inv_ixs, unq_valid_spec_ixs) == True))[0]
    totals['valid_spec_dets'] += len(valid_spec_dets)

    # Get precisions for the valid species
    bars, labs = get_spec_precisions(annotated_xlsx_path)

    # Count species with medium precision (nominally 80%)
    med_prec_specs = []
    for lab_ix, lab in enumerate(labs):
        if bars[lab_ix][0] >= MED_SPEC_PREC_THRESH: med_prec_specs.append(lab)
    totals['med_prec_specs'].extend(med_prec_specs)

    # Count species with high precision (nominally 100%)
    high_prec_specs = []
    for lab_ix, lab in enumerate(labs):
        if bars[lab_ix][0] >= HIGH_SPEC_PREC_THRESH: high_prec_specs.append(lab)
    totals['high_prec_specs'].extend(high_prec_specs)

    # Count detections for the high precision species
    high_prec_dets = [d for d in all_valid_dets if d['common_name'] in high_prec_specs]
    perc_high_prec_dets = int(np.round(len(high_prec_dets)/len(all_valid_dets)*100))
    totals['high_prec_dets'] += len(high_prec_dets)

    # Print information for given dataset
    print('{}:'.format(ds['name']))
    print('---- {} sites'.format(len(unq_sites)))
    print('---- {} - {}'.format(np.min(all_fd_dts).strftime('%Y-%m-%d'), np.max(all_fd_dts).strftime('%Y-%m-%d')))
    print('---- {} hours ({} files)'.format(f'{ds_hours:,}', f'{len(all_f_dets):,}'))    
    print('---- {} species'.format(len(unq_specs)))
    print('---- {} raw detections'.format(f'{len(all_valid_dets):,}'))
    print('---- {} species with over {} detections'.format(len(unq_valid_spec_ixs), N_DET_THRESH))
    print('---- {} detections after filtering species'.format(f'{len(valid_spec_dets):,}'))
    print('---- {} species with precision >= {}'.format(len(med_prec_specs), MED_SPEC_PREC_THRESH))
    print('---- {} species with precision >= {}'.format(len(high_prec_specs), HIGH_SPEC_PREC_THRESH))
    print('---- {} detections of species with precision >= {} ({}%)'.format(f'{len(high_prec_dets):,}', HIGH_SPEC_PREC_THRESH, perc_high_prec_dets))

# Print totals across all datasets
print('Totals: {} hrs, {} sites, {} specs, {} valid_specs, {} dets, {} valid_spec_dets, {} med_prec_specs, {} high_prec_specs, {} high_prec_dets'
      .format(totals['hrs'], totals['sites'], len(np.unique(totals['specs'])), len(np.unique(totals['valid_specs'])), totals['dets'], 
              totals['valid_spec_dets'], len(np.unique(totals['med_prec_specs'])), len(np.unique(totals['high_prec_specs'])), totals['high_prec_dets']))

# Count valid species which appear in more than one dataset
unq_valid_specs, valid_spec_counts = np.unique(totals['valid_specs'], return_counts=True)
print('Valid - {}'.format(['{} ({})'.format(s, s_c) for s, s_c in zip(unq_valid_specs, valid_spec_counts) if s_c > 1]))

# Count medium/high precision species which appear in more than one dataset
unq_med_prec_specs, med_prec_spec_counts = np.unique(totals['med_prec_specs'], return_counts=True)
print('Prec >= {}: {}'.format(MED_SPEC_PREC_THRESH, ['{} ({})'.format(s, s_c) for s, s_c in zip(unq_med_prec_specs, med_prec_spec_counts) if s_c > 1]))

unq_high_prec_specs, high_prec_spec_counts = np.unique(totals['high_prec_specs'], return_counts=True)
print('Prec >= {}: {}'.format(HIGH_SPEC_PREC_THRESH, ['{} ({})'.format(s, s_c) for s, s_c in zip(unq_high_prec_specs, high_prec_spec_counts) if s_c > 1]))
