import os 
import pickle 
import matplotlib.pyplot as plt
from utils import get_costarica_site_info, get_opt_spec_bn_threshs
import numpy as np

def do_plot(spec_prec_thresh=1, force_compute=False):

    ds = {'short_name': 'costa-rica', 'name': 'Costa Rica', 'mins_per_f': 1}

    temp_fig_data_path = os.path.join('temp_fig_data', 'fig3_{}.pickle'.format(ds['short_name']))

    if not os.path.exists(temp_fig_data_path) or force_compute:
        comb_data_dir = 'combined_detection_data'
        comb_dets_path = os.path.join(comb_data_dir, '{}_combined_dets_0-8_thresh.pickle'.format(ds['short_name']))

        spec_opt_threshs, spec_precisions = get_opt_spec_bn_threshs(ds['short_name'])
        specs = np.asarray(list(spec_opt_threshs.keys()))
        allowed_specs = specs[np.where((spec_precisions >= spec_prec_thresh))[0]]

        with open(comb_dets_path, 'rb') as f_handle:
            all_f_dets = pickle.load(f_handle)

        sites_with_hab_info = get_costarica_site_info(all_f_dets)

        all_fd_site_names = np.asarray([fd['site'] for fd in all_f_dets])
        keep_fd_ixs = []
        for s in sites_with_hab_info:
            match_ixs = np.where((all_fd_site_names == s['name']))[0]
            keep_fd_ixs.extend(match_ixs)

        all_valid_fds = np.asarray(all_f_dets[keep_fd_ixs])

        all_fd_sites = [d['site'] for d in all_valid_fds]

        unq_sites = np.asarray([s['name'] for s in sites_with_hab_info])
        unq_site_habitats = np.asarray([s['habitat'] for s in sites_with_hab_info])

        unq_habs, hab_counts = np.unique(unq_site_habitats, return_counts=True)

        all_hab_stats = {'daily_dets_per_min': [], 'daily_richnesses': [], 'minutely_spec_richness': [], 'minutely_dets': []}
        for hab_ix, hab in enumerate(unq_habs):
            hab_site_names = unq_sites[np.where((unq_site_habitats == hab))[0]]

            hab_match_fd_ixs = np.where((np.isin(all_fd_sites, hab_site_names)))[0]
            hab_match_fds = all_valid_fds[hab_match_fd_ixs]

            fd_days = np.asarray([fd['dt'].strftime('%Y-%m-%d') for fd in hab_match_fds])

            print('{}: {} sites, {} fds'.format(hab, len(hab_site_names), len(hab_match_fds)))

            unq_hab_days = np.unique(fd_days)

            hab_day_dets_per_min = []
            hab_daily_richnesses = []
            hab_minutely_dets = []
            hab_minutely_richnesses = []

            for hab_day in unq_hab_days:
                daily_spec_comm = []
                hab_day_match_fds = hab_match_fds[np.where((fd_days == hab_day))[0]]

                for fd in hab_day_match_fds:
                    fd_spec_comm = []
                    for d in fd['dets']:
                        if d['common_name'] in allowed_specs and d['confidence'] > spec_opt_threshs[d['common_name']]:
                            daily_spec_comm.append(d['common_name'])
                            fd_spec_comm.append(d['common_name'])

                    hab_minutely_dets.append(len(fd_spec_comm))
                    hab_minutely_richnesses.append(len(np.unique(fd_spec_comm)))

                hab_day_dets_per_min.append(len(daily_spec_comm)/len(hab_day_match_fds))
                hab_daily_richnesses.append(len(np.unique(daily_spec_comm))/len(hab_day_match_fds))

            all_hab_stats['daily_richnesses'].append(hab_daily_richnesses)
            all_hab_stats['daily_dets_per_min'].append(hab_day_dets_per_min)
            all_hab_stats['minutely_dets'].append(hab_minutely_dets)
            all_hab_stats['minutely_spec_richness'].append(hab_minutely_richnesses)
        
        with open(temp_fig_data_path, 'wb') as handle:
            pickle.dump([all_hab_stats, unq_habs, hab_counts], handle)

    else:
        with open(temp_fig_data_path, 'rb') as f_handle:
            all_hab_stats, unq_habs, hab_counts = pickle.load(f_handle)

    all_hab_chosen_stat = all_hab_stats['daily_richnesses']
    meds = [np.median(daily_r) for daily_r in all_hab_chosen_stat]
    sort_ix = np.argsort(meds)

    all_hab_chosen_stat = [all_hab_chosen_stat[ix] for ix in sort_ix] 
    unq_habs = unq_habs[sort_ix]
    hab_counts = hab_counts[sort_ix]

    bxplt = plt.boxplot(all_hab_chosen_stat, notch=False, whis=[5,95], showfliers=False, positions=range(len(unq_habs)))
    for el in np.hstack([bxplt['boxes'], bxplt['whiskers'], bxplt['medians'], bxplt['caps']]):
        el.set_color('k')
        #el.set_linewidth(1.5)

    plt.xticks(range(len(unq_habs)), unq_habs, fontsize=14)
    [plt.text(x, plt.gca().get_ylim()[0], s='N = {}'.format(cnt), ha='center', va='top') for x, cnt in zip(range(len(unq_habs)), hab_counts)]
    plt.gca().set_ylim([plt.gca().get_ylim()[0]-0.0004, plt.gca().get_ylim()[1]])
    plt.xlabel('Habitat')
    plt.ylabel('Species diversity / minute')
    plt.tight_layout()

if __name__ == '__main__':
    plt.figure(figsize=((8,4)))
    do_plot()
    plt.savefig(os.path.join('figs', 'fig_3_costa-rica_land_use.png'))   
    plt.show()