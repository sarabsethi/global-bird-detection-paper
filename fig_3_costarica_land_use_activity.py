import os 
import pickle 
import matplotlib.pyplot as plt
from utils import get_costarica_site_info, get_opt_spec_bn_threshs
import numpy as np

def do_plot(target_spec='Yellow-throated Toucan', force_compute=False):

    ds = {'short_name': 'costa-rica', 'name': 'Costa Rica', 'mins_per_f': 1}

    temp_fig_data_path = os.path.join('temp_fig_data', 'fig3_{}.pickle'.format(ds['short_name']))

    if not os.path.exists(temp_fig_data_path) or force_compute:
        comb_data_dir = 'combined_detection_data'
        comb_dets_path = os.path.join(comb_data_dir, '{}_combined_dets_0-8_thresh.pickle'.format(ds['short_name']))

        spec_opt_threshs, _, _, _ = get_opt_spec_bn_threshs(ds['short_name'])

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

        unq_habs = np.unique(unq_site_habitats)
        
        hab_det_rates = []
        hab_site_day_counts = []
        for hab in unq_habs:
            hab_site_day_det_rates = []
            hab_num_site_days = 0

            hab_site_names = unq_sites[np.where((unq_site_habitats == hab))[0]]
            hab_match_fd_ixs = np.where((np.isin(all_fd_sites, hab_site_names)))[0]
            hab_match_fds = all_valid_fds[hab_match_fd_ixs]

            all_hab_sites = np.asarray([fd['site'] for fd in hab_match_fds])
            unq_hab_sites = np.unique(all_hab_sites)

            print('{}: {} sites, {} files'.format(hab, len(hab_site_names), len(hab_match_fds)))

            for hab_site in unq_hab_sites:
                hab_site_match_fds = hab_match_fds[all_hab_sites == hab_site]

                all_hab_site_days = np.asarray([fd['dt'].strftime('%Y-%m-%d') for fd in hab_site_match_fds])
                unq_hab_site_days = np.unique(all_hab_site_days)

                for hab_day in unq_hab_site_days:
                    hab_num_site_days += 1

                    hab_site_day_match_fds = hab_site_match_fds[all_hab_site_days == hab_day]

                    num_dets = 0
                    for fd in hab_site_day_match_fds:
                        for d in fd['dets']:
                            if d['common_name'] == target_spec and d['confidence'] > spec_opt_threshs[target_spec]:
                                num_dets += 1
                    
                    hab_site_day_det_rates.append(num_dets / (len(hab_site_day_match_fds)*ds['mins_per_f']))

            hab_site_day_counts.append(hab_num_site_days)
            hab_det_rates.append(hab_site_day_det_rates)
        
        hab_site_day_counts = np.asarray(hab_site_day_counts)

        with open(temp_fig_data_path, 'wb') as handle:
            pickle.dump([hab_det_rates, unq_habs, hab_site_day_counts], handle)

    else:
        with open(temp_fig_data_path, 'rb') as f_handle:
            hab_det_rates, unq_habs, hab_site_day_counts = pickle.load(f_handle)
    
    # "Grasslands" in the dataframe should actually more accurately described as "Pastures" 
    for ix, u in enumerate(unq_habs):
        if u == 'Grassland': unq_habs[ix] = 'Pasture'

    all_hab_chosen_stat = hab_det_rates
    meds = [np.mean(daily_r) for daily_r in all_hab_chosen_stat]
    sort_ix = np.argsort(meds)

    all_hab_chosen_stat = [all_hab_chosen_stat[ix] for ix in sort_ix] 
    unq_habs = unq_habs[sort_ix]
    hab_site_day_counts = hab_site_day_counts[sort_ix]

    plt.gca().violinplot(all_hab_chosen_stat, showmeans=True, showmedians=False, showextrema=False)

    #bxplt = plt.boxplot(all_hab_chosen_stat, notch=False, whis=[15,85], showfliers=False, positions=range(len(unq_habs)))
    #for el in np.hstack([bxplt['boxes'], bxplt['whiskers'], bxplt['medians'], bxplt['caps']]):
    #    el.set_color('k')
    #    #el.set_linewidth(1.5)

    plt.xticks([i+1 for i in range(len(unq_habs))], unq_habs, fontsize=14)
    [plt.text(x+1, -0.007, s='N = {}'.format(cnt), ha='center', va='top') 
        for x, cnt in zip(range(len(unq_habs)), hab_site_day_counts)]
    plt.gca().set_ylim([-0.02, np.quantile([x for xs in all_hab_chosen_stat for x in xs], 0.90)])
    plt.xlabel('Habitat')
    plt.ylabel('Daily vocalisation rate (dets/min)'.format(target_spec))
    plt.tight_layout()

if __name__ == '__main__':
    plt.figure(figsize=((8,4)))
    do_plot()
    plt.savefig(os.path.join('figs', 'fig_3_costa-rica_land_use.png'))   
    plt.show()