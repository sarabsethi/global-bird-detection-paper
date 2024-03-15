import os 
import pandas as pd 
import numpy as np 
from datetime import timedelta
import csv 

def get_opt_spec_bn_threshs(ds_short_name):
    annotated_xlsx_path = os.path.join('precision_labelled_data', '{}_labelled_clips.xlsx'.format(ds_short_name))
    bn_thresh_vals = np.linspace(0.8, 0.99, 20)

    _, all_specs = get_spec_precisions(annotated_xlsx_path, bn_thresh_vals[0])
    all_specs_precs = np.ones((len(bn_thresh_vals), len(all_specs))) * -1

    for bn_thresh_ix, bn_thresh in enumerate(bn_thresh_vals):
        bars, labs = get_spec_precisions(annotated_xlsx_path, bn_thresh)
        prop_right = bars[:,0]
        
        for spec_ix, spec in enumerate(labs):
            spec_match_ix = np.where((all_specs == spec))[0]
            all_specs_precs[bn_thresh_ix, spec_match_ix] = prop_right[spec_ix]

    opt_spec_bn_threshs = {}
    prec_at_opt_threshs = []

    for spec_ix, spec in enumerate(all_specs):
        spec_precs = all_specs_precs[:, spec_ix]
        best_thresh = bn_thresh_vals[np.argmax(spec_precs)]
        prec_at_opt_threshs.append(max(spec_precs))
        opt_spec_bn_threshs[spec] = np.round(best_thresh, 3)
    
    return opt_spec_bn_threshs, np.asarray(prec_at_opt_threshs)


def get_datasets_dict():
    return [{'short_name': 'norway', 'name': 'Norway', 'mins_per_f': 5},
            {'short_name': 'taiwan', 'name': 'Taiwan'},
            {'short_name': 'costa-rica', 'name': 'Costa Rica', 'mins_per_f': 1},
            {'short_name': 'brazil', 'name': 'Brazil', 'mins_per_f': 1}]


def expand_to_valid_dets(all_f_dets, bn_conf_thresh=0.80):
    all_valid_dets = []
    for f_dets in all_f_dets:
        for d in f_dets['dets']:
            if isinstance(bn_conf_thresh, dict):
                if d['common_name'] not in bn_conf_thresh.keys(): continue
                else: min_det_conf = bn_conf_thresh[d['common_name']]
            else: min_det_conf = bn_conf_thresh

            if d['confidence'] >= min_det_conf:

                d['site'] = f_dets['site']
                d['file_dt'] = f_dets['dt']
                d['det_dt'] = f_dets['dt'] + timedelta(seconds=d['start_time'])
                if 'lat' in f_dets.keys(): 
                    d['lat'] = f_dets['lat']
                    d['long'] = f_dets['long']

                all_valid_dets.append(d)

    return np.asarray(all_valid_dets)


def convert_norway_site_to_lat_group(lat, site):
    lat = float(lat)
    thresh_south = 61
    thresh_north = 65

    if lat < thresh_south:
        return 'South'
    if lat > thresh_south and lat < thresh_north:
        return 'Central'
    if lat > thresh_north:
        return 'North'


def get_costarica_site_info(all_f_dets):
    all_fd_site_names = np.asarray([fd['site'] for fd in all_f_dets])
    unq_site_names = np.unique(all_fd_site_names)

    unq_sites = []
    for s in unq_site_names:
        _loc = ''.join(s.split('_')[:-1]).replace('-','').lower()
        _sn = s.split('-')[-1].lower()
        unq_sites.append({'name': s, 'loc_site_str': '{}{}'.format(_loc, _sn)})

    all_site_loc_site_strs = np.asarray([s['loc_site_str'] for s in unq_sites])

    site_info_csv_path = os.path.join('raw_data_costa-rica', 'costa_rica_site_info.csv')
    with open(site_info_csv_path, newline='') as csvfile:
        rdr = csv.reader(csvfile, delimiter=',')
        for row_ix, row in enumerate(rdr):
            if row_ix != 0:
                _lat = row[8]
                _long = row[9]
                _habitat = row[2]
                _loc_and_site = row[1].strip().lower().replace(' ','').replace('-','')

                _loc = _loc_and_site.split('_')[0]
                if _loc == 'sq260': _loc = 'sq2601'
                if _loc == 'mangrove': _loc = 'mangroves'
                if _loc == 'palma': _loc = 'lapalma'
                if _loc == 'elsi': _loc = 'elsicroc'
                if _loc == 'rancho': _loc = 'ranchobajo'
                if _loc == 'miramar': _loc = 'mirenmar'
                if _loc == 'nuevo': _loc = 'rionuevo'
                if _loc == 'gamba': _loc = 'lagamba'
                if _loc == 'tarde': _loc = 'latarde'
                if _loc == 'lareserva': _loc = 'indigenousreserve'
                if _loc == 'sendero': _loc = 'golfito'

                _site_num = _loc_and_site.split('_')[-1]

                match_site_ix = np.where((all_site_loc_site_strs == '{}{}'.format(_loc, _site_num)))[0]
                if len(match_site_ix) > 0:
                    unq_sites[match_site_ix[0]]['lat'] = _lat
                    unq_sites[match_site_ix[0]]['long'] = _long
                    unq_sites[match_site_ix[0]]['habitat'] = _habitat

    w_habitat_sites = [s for s in unq_sites if 'habitat' in s.keys()]
    print('Total sites {}, {} with habitat data'.format(len(unq_sites), len(w_habitat_sites)))
    
    return w_habitat_sites

def get_spec_precisions(annotated_xlsx_path, bn_thresh=0.8):
    annotated_xlsx = os.path.join(annotated_xlsx_path)

    df = pd.read_excel(annotated_xlsx, index_col=None)
    df = df.where(pd.notnull(df), '')
    
    bn_confs = np.asarray(df['Confidence'].to_list())
    over_thresh_ixs = np.where((bn_confs >= bn_thresh))[0]
    df = df.loc[over_thresh_ixs]

    all_specs = np.asarray(df['Common name'].to_list())
    all_decisions = np.asarray(df['BirdNET correct?'].to_list())

    unq_specs = np.unique(all_specs)

    labs = []
    bars = []
    for spec in unq_specs:
        match_ixs = np.where((all_specs == spec))[0]
        spec_decisions = all_decisions[match_ixs]

        spec_decisions = np.asarray([s.strip().lower() for s in spec_decisions])
        tot_decs = len(spec_decisions)

        s_prop_right = len(np.where((spec_decisions == 'yes'))[0])/tot_decs
        s_prop_maybe = len(np.where((spec_decisions == 'maybe'))[0])/tot_decs  
        s_prop_no = len(np.where((spec_decisions == 'no'))[0])/tot_decs 

        labs.append(spec)
        bars.append([s_prop_right, s_prop_maybe, s_prop_no])

    bars = np.asarray(bars)
    labs = np.asarray(labs)

    return bars, labs