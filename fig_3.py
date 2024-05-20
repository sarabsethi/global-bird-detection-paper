import fig_3_brazil_diurnal
import fig_3_norway_species_latitudinal
import fig_3_taiwan_seasonal
import fig_3_costarica_land_use_activity
import matplotlib.pyplot as plt 
import os 

title_font_sz = 18
plt.rc('axes', labelsize=15)    
plt.rc('xtick', labelsize=12)    
plt.rc('ytick', labelsize=12)    

SPEC_PREC_THR = 0.9
MIN_DETS_PER_SPEC = 20

COSTA_RICA_SPEC = 'Yellow-throated Toucan'
NORWAY_SPEC = 'Willow Warbler'

fig3 = plt.figure(figsize=((18,17)), constrained_layout=True)
gs = fig3.add_gridspec(12, 2)

f3_ax1 = fig3.add_subplot(gs[0:4, 0])
plt.sca(f3_ax1)
fig_3_brazil_diurnal.do_plot(spec_prec_thresh=SPEC_PREC_THR, min_dets_per_spec=MIN_DETS_PER_SPEC)
f3_ax1.set_title('Brazil', fontsize=title_font_sz)

f3_ax2 = fig3.add_subplot(gs[0:4, 1])
plt.sca(f3_ax2)
fig_3_costarica_land_use_activity.do_plot(COSTA_RICA_SPEC)
f3_ax2.set_title('Costa Rica: {}'.format(COSTA_RICA_SPEC), fontsize=title_font_sz)

f3_ax3 = fig3.add_subplot(gs[4:7, :])
plt.sca(f3_ax3)
fig_3_norway_species_latitudinal.do_plot(NORWAY_SPEC)
f3_ax3.set_title('Norway: {}'.format(NORWAY_SPEC), fontsize=title_font_sz)

f3_ax4 = fig3.add_subplot(gs[7:, :])
plt.sca(f3_ax4)
fig_3_taiwan_seasonal.do_plot(spec_prec_thresh=SPEC_PREC_THR, min_dets_per_spec=MIN_DETS_PER_SPEC)
f3_ax4.set_title('Taiwan', fontsize=title_font_sz)

plt.tight_layout()

plt.savefig(os.path.join('figs', 'fig_3.pdf'))   
plt.savefig(os.path.join('figs', 'fig_3.svg'))   
plt.savefig(os.path.join('figs', 'fig_3.png'))   
