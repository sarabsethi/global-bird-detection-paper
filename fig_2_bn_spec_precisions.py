import os
from utils import get_spec_precisions
import numpy as np
import matplotlib.pyplot as plt

all_datasets = [{'short_name': 'norway', 'name': 'Norway'},
                {'short_name': 'taiwan', 'name': 'Taiwan'},
                {'short_name': 'costa-rica', 'name': 'Costa Rica'},
                {'short_name': 'brazil', 'name': 'Brazil'},]

fig, axs = plt.subplots(1, 4, figsize=(25,14))

axs = np.ravel(axs)
ax_labs = ['a.', 'b.', 'c.', 'd.']

# Loop through all datasets
for ds_ix, ds in enumerate(all_datasets):
    # Setup and label subplot
    plt.sca(axs[ds_ix])
    axs[ds_ix].text(-1, 1.01, ax_labs[ds_ix], transform=axs[ds_ix].transAxes, size=24, weight='bold')

    # Measure per species precisions from annotated data
    annotated_xlsx_path = os.path.join('precision_labelled_data', '{}_labelled_clips.xlsx'.format(ds['short_name']))
    bars, labs = get_spec_precisions(annotated_xlsx_path)

    prop_right = bars[:,0]
    print('{}: {} total; 100% {} specs; >80% {} specs; 0% {}'.format(ds['name'], bars.shape[0], len(np.where(prop_right==1)[0]), len(np.where(prop_right>=0.8)[0]), len(np.where(prop_right==0)[0])))

    # First sort by proportion correct
    spec_ord = np.lexsort((np.argsort(labs)[::-1], bars[:,1] + bars[:,0], bars[:,0]))
    labs = labs[spec_ord]
    bars = bars[spec_ord, :]

    # Plot bars summarising precision data per species
    w = 0.5
    plt.gca().barh(labs, bars[:,0], label='Correct', height=w, color='green')
    plt.gca().barh(labs, bars[:,1], left=bars[:,0], label='Unsure',  height=w, color='blue')
    plt.gca().barh(labs, bars[:,2], left=bars[:,1] + bars[:,0], label='Incorrect',  height=w, color='red')

    # Plot labelling/formatting etc
    if ds_ix == 0:
        plt.legend(loc='upper left', framealpha=0.95, fontsize=15)
    if ds_ix == 0:
        plt.ylabel('Species', fontsize=20)
    plt.xlabel('Prop. labelled', fontsize=18)
    plt.xlim([0,1])
    plt.xticks([0, 0.2, 0.4, 0.6, 0.8, 1], ['0', '.2', '.4', '.6', '.8', '1'])
    plt.gca().tick_params(axis='y', labelsize=16)
    plt.gca().tick_params(axis='x', labelsize=16)

    plt.ylim([-0.5, len(labs)])
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

# Save figure to file as vector and raster
figs_dir = 'figs'
if not os.path.exists(figs_dir): os.makedirs(figs_dir)
plt.savefig(os.path.join(figs_dir,'fig_2_bn_spec_precisions.pdf'))
plt.savefig(os.path.join(figs_dir,'fig_2_bn_spec_precisions.png'))