import os
from utils import get_datasets_dict, get_opt_spec_bn_threshs, expand_to_valid_dets
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

all_datasets = get_datasets_dict()

comb_data_dir = 'combined_detection_data'
TARGET_PREC = 0.90
MIN_DETS_PER_SPEC = 20

fig, axs = plt.subplots(1, 4, figsize=(25,14))
axs = np.ravel(axs)

for ds_ix, ds in enumerate(all_datasets):
    plt.sca(axs[ds_ix])

    annotated_xlsx_path = os.path.join('precision_labelled_data', '{}_labelled_clips.xlsx'.format(ds['short_name']))

    bn_threshs, spec_precs, num_spec_dets, num_valid_spec_dets = get_opt_spec_bn_threshs(ds['short_name'], TARGET_PREC)
    specs = np.asarray(list(bn_threshs.keys()))
    
    print('Corr between calibrated thresholds and precisions: {}'.
          format(stats.pearsonr(list(bn_threshs.values()), spec_precs)))

    # First sort species by precisions then alphabetically
    spec_ord = np.lexsort((np.argsort(specs)[::-1], spec_precs))
    specs = specs[spec_ord]
    spec_precs = spec_precs[spec_ord]
    num_valid_spec_dets = num_valid_spec_dets[spec_ord]

    spec_labs = []
    num_low_samp_sizes = 0
    for sp_ix, sp in enumerate(specs): 
        #print('{}: {}'.format(sp, num_valid_spec_dets[sp_ix]))
        if num_valid_spec_dets[sp_ix] < MIN_DETS_PER_SPEC: 
            spec_labs.append('{}*'.format(sp))
            num_low_samp_sizes += 1
        else:
            spec_labs.append(sp)
        
    #print(['{}: {}'.format(sp, sp_pr) for sp, sp_pr in zip(specs, spec_precs)])

    print('{}: {} total; >{}% {} specs ({} < {} dets); 0% {}'.format(ds['name'], len(specs), int(TARGET_PREC*100),
                len(np.where(spec_precs>=TARGET_PREC)[0]), num_low_samp_sizes, MIN_DETS_PER_SPEC, len(np.where(spec_precs==0)[0])))

    # Plot bars showing true and false positive proportions
    w = 0.5
    plt.gca().barh(spec_labs, spec_precs, label='True pos. ($T_{p}$)', height=w, color='green')
    plt.gca().barh(spec_labs, 1-spec_precs, left=spec_precs, label='False pos. ($F_{p}$)', height=w, color='red')
    
    if ds_ix == 0:
        plt.legend(loc='upper left', framealpha=0.95, fontsize=15)
    
    #if ds_ix == 0:
    #    plt.ylabel('Species', fontsize=20)
    
    plt.xlabel('Prop. labelled', fontsize=18)
    plt.xlim([0,1])
    plt.xticks([0, 0.2, 0.4, 0.6, 0.8, 1], ['0', '.2', '.4', '.6', '.8', '1'])
    plt.gca().tick_params(axis='y', labelsize=16)
    plt.gca().tick_params(axis='x', labelsize=16)

    plt.ylim([-0.5, len(spec_labs)])
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.title(ds['name'], fontsize=24)
    
plt.tight_layout()

# Manually shove subplots about a bit to condense things in further
bbox=axs[2].get_position()
offset= -0.026
axs[2].set_position([bbox.x0 + offset, bbox.y0, bbox.x1-bbox.x0, bbox.y1 - bbox.y0])

bbox=axs[3].get_position()
offset= -0.049
axs[3].set_position([bbox.x0 + offset, bbox.y0, bbox.x1-bbox.x0, bbox.y1 - bbox.y0])

figs_dir = 'figs'
if not os.path.exists(figs_dir): os.makedirs(figs_dir)
plt.savefig(os.path.join(figs_dir,'fig_2.pdf'))
plt.savefig(os.path.join(figs_dir,'fig_2.svg'))
plt.savefig(os.path.join(figs_dir,'fig_2.png'))