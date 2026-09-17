#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 11:20:07 2024

@author: nitish
"""

from utils import *
from all_plots import *
import numpy as np
import math as mt 
import multiprocessing as mp
import random
import time
import sys
import os
import pickle
import itertools
import psutil
import json

list_of_locations = ['Toronto', 'NewYork', 'London', 'Singapore', 'Sydney', 'Auckland', 'Paris', 'RiodeJaneiro', 'Nice', 'Mumbai', 'Johannesburg', 'Boston', 'Dublin', 'WashingtonDC', 'Lijiang', 'Houston', 'Tucson']
locations_to_id_mapping = {'Toronto':0, 'NewYork':1, 'London':2, 'Singapore':3, 'Sydney':4, 'Auckland':5, 'Paris':6, 'RiodeJaneiro':7, 'Nice':8, 'Mumbai':9, 'Johannesburg':10, 'Boston':11, 'Dublin':12, 'WashingtonDC':13, 'Lijiang':14, 'Houston':15, 'Tucson':16}
list_of_locations_coords = {'Toronto':(-79.38,43.6532), 'NewYork':(-74.00,40.7128),'London':(-0.127,51.5074), 'Singapore':(103.819,1.3521),'Sydney':(151.209,-33.868), 'Auckland':(174.763,-36.848),'Paris':(2.3522,48.86), 'RiodeJaneiro':(-43.17,-22.9068),'Nice':(7.2620, 43.7102), 'Mumbai':(72.877,19.0760),'Johannesburg':(28.04,-26.2041), 'Boston':(-71.06,42.36),'Dublin':(-6.26,53.35), 'WashingtonDC':(-77.0396,38.072),'Lijiang':(100.2277,26.855), 'Houston':(-95.3698,29.7604),'Tucson':(-110.97,32.25)}
# time_diff = {'Toronto':0, 'NewYork':0, 'London':18000, 'Singapore':43200, 'Sydney':54000, 'Auckland':61200, 'Paris':21600, 'RiodeJaneiro':3600, 'Nice':21600, 'Mumbai':34200, 'Johannesburg':21600, 'Boston':0, 'Dublin':18000, 'WashingtonDC':0, 'Lijiang':43200, 'Houston':-3600, 'Tucson':-10800}
# list_of_locations_coords = [(-79.38,43.6532), (-74.00,40.7128),(-0.127,51.5074), (103.819,1.3521),(151.209,-33.868), (174.763,-36.848),(2.3522,48.86), (-43.17,-22.9068),(7.2620, 43.7102), (72.877,19.0760),(28.04,-26.2041), (-71.06,42.36),(-6.26,53.35), (-77.0396,38.072),(100.2277,26.855), (-95.3698,29.7604),(-110.97,32.25)]
time_diff = [0,0,18000,43200, 54000,61200,21600,3600,21600,34200,21600,0,18000,0,43200,-3600,-10800]
_,earth_rad,_,earth_omega,_,_,_=get_constants(1000)
no_of_rings = 20
no_of_sats_in_each_ring = 20
no_of_sats = no_of_rings * no_of_sats_in_each_ring
thetae = (20)*(np.pi/180)
arch_type = 'dd'

G, G_pair_labels, gs_to_pair_mapping, no_of_gs = get_GS_locations(earth_rad, list_of_locations_coords, locations_to_id_mapping)
no_of_gs_pairs = len(G_pair_labels)

date_list = {'03/15/2022':0, '06/15/2022':1,'09/15/2022':2,'12/15/2022':3}
air_trans_vertical_list = {}
air_trans_vertical_list_without_cloud = {}
all_pd_list = {}
print(sys.version) 
for date in date_list:
    date_list_id = date_list[date]
    air_trans_vertical_list[date] = get_vertical_air_trans(list_of_locations, date_list_id, locations_to_id_mapping)
    air_trans_vertical_list_without_cloud[date] = get_vertical_air_trans_without_cloud(list_of_locations, date_list_id, locations_to_id_mapping)
    all_pd_list[date] = get_all_Pds(list_of_locations, date_list_id, locations_to_id_mapping)


def save_data(t, sol_arr, in_range_pair, in_range_sats, file_name):
    # Creating the data dictionary with the current time `t` as key
    data_dict = {
        t: {
            "sol_arr": sol_arr,
            "In_range_pair": in_range_pair,
            "In_range_sats": in_range_sats
        }
    }

        # Check if the file exists
    if os.path.exists(file_name):
        # If file exists, load the existing data
        with open(file_name, "rb") as file:
            try:
                # Read the current data in the pickle file
                existing_data = pickle.load(file)
            except EOFError:
                # If the file is empty, initialize the existing_data as an empty dictionary
                existing_data = {}
    else:
        # If file does not exist, initialize the existing_data as an empty dictionary
        existing_data = {}

    # Append the new data to the existing dictionary
    existing_data.update(data_dict)

    # Write the updated data back to the file
    with open(file_name, "wb") as file:
        pickle.dump(existing_data, file)



Is_discrete = 1
    
def solve_assignment(date,alt,algo_type, t_start, t_end, T, R, L):

    start_time = time.time()
    # print(f"Process {mp.current_process().name} started at {time.strftime('%H:%M:%S', time.localtime(start_time))} with params: {date, alt, algo_type, t_start, t_end, T, R, L}")

    S=generate_network(no_of_rings,no_of_sats_in_each_ring,earth_rad,alt)
    sat_axis_list, sat_loc_list = pre_process_sat(S, no_of_rings*no_of_sats_in_each_ring)
    for t in range(t_start, t_end+1, 10):
        # print(f"CPU Usage: {psutil.cpu_percent()}% at time{t}")
        print("+++++++++++++++++++++")
        print("altitude: ",alt)
        print("t: ",t)
        sat_list, gs_list, gs_pair_list,In_range_pair, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, In_range_pair_reflection, In_range_sats_reflection, In_range_gs_pairs_reflection, In_range_pair_fidelity_reflection = evolve_network(sat_axis_list, sat_loc_list,G,G_pair_labels,t,alt,earth_omega,thetae, algo_type, no_of_sats, time_diff, air_trans_vertical_list[date], all_pd_list[date])
        # print(In_range_pair)

        # print("+++++++++++++++++++++")




        # if algo_type != 'reflection-ratesum':
        #     In_range_pair_fraction = find_fraction_per_pair(In_range_pair, In_range_sats, gs_pair_list)
        
        # if(algo_type == 'primary-ratesum'):
        #     sol_ptd, mmf_ptd, sol_arr = solve_primary(sat_list, gs_list, gs_pair_list, T, R, L, gs_to_pair_mapping, In_range_pair, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, Is_discrete)
        # elif(algo_type == 'primary-maxmin'):
        #     sol_arr = iterative_max_min(G_pair_labels, len(gs_pair_list), sat_list, gs_list, gs_pair_list, T, R, L, gs_to_pair_mapping, In_range_pair_fraction, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, Is_discrete)
        # elif(algo_type == 'reflection-ratesum'):
        #     solution_value = solve_reflection(no_of_sats, no_of_gs_pairs, no_of_gs, T, R, L, gs_to_pair_mapping, In_range_pair, In_range_sats, In_range_gs_pairs,In_range_pair_reflection, In_range_sats_reflection, In_range_gs_pairs_reflection)

        #print(sol_arr)


        # rates_iter3 = get_pairwise_rates_primary(In_range_pair, In_range_sats, gs_pair_list, sol_arr, G_pair_labels)
        # sum_rates_iter3 = sum(rates_iter3)
        # sum_rates_iter3 = sum_rates_iter3/10**6
        # print(f"Timestampp: {t} |Altitudes: {alt} | Sum of Rates: {sum_rates_iter3}")


        # tempDate = date.replace("/", "-")

        # fName = f"dictOP/{tempDate}_{alt}_{algo_type}_{t_start}_{t_end}_{T}_{R}_{L}.pkl"

        # if algo_type == 'reflection-ratesum':
        #     save_data(t,solution_value,In_range_pair, In_range_sats, fName)
        # else:
        #     save_data(t,sol_arr,In_range_pair, In_range_sats, fName)

        
        
        
        
        # final_dict[data_dict]
            
        # rates_iter3 = get_pairwise_rates_primary(In_range_pair, In_range_sats,gs_pair_list,sol_arr,G_pair_labels)

        # sol_pfd, mmf_pfd, sol_arr_pfd = solve_primary_fair(sat_list, gs_list, gs_pair_list, T, R, L, gs_to_pair_mapping, In_range_pair, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, Is_discrete)
        
        # sol_ptfd, mmf_ptfd, sol_arr_ptfd = solve_primary(sat_list, gs_list, gs_pair_list, T, R, L, gs_to_pair_mapping, In_range_pair_fraction, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, Is_discrete)
        # sol_pffd, mmf_pffd, sol_arr_pffd = solve_primary_fair(sat_list, gs_list, gs_pair_list, T, R, L, gs_to_pair_mapping, In_range_pair_fraction, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, Is_discrete)
        
        # sol_ptgd, sol_arr_ptgd = solve_primary_greedy(T, R, L, G_pair_labels, In_range_pair, no_of_sats, no_of_gs,no_of_gs_pairs)
        
        # sol_arr_ptpm={}
        # for i in sol_arr_pfd:
        #     sol_arr_ptpm[i] = T
        

        # primary_ratesum = get_pairwise_rates_primary(In_range_pair, In_range_sats,gs_pair_list,sol_arr_ptd,G_pair_labels)
        # primary_maxmin = get_pairwise_rates_primary(In_range_pair, In_range_sats,gs_pair_list,sol_arr_pfd,G_pair_labels)
        # primary_ratesum_frac = get_pairwise_rates_primary(In_range_pair, In_range_sats,gs_pair_list,sol_arr_ptfd,G_pair_labels)
        # primary_maxmin_frac = get_pairwise_rates_primary(In_range_pair, In_range_sats,gs_pair_list,sol_arr_pffd,G_pair_labels)
        # pair_max = get_pairwise_rates_primary(In_range_pair, In_range_sats,gs_pair_list,sol_arr_ptpm,G_pair_labels)
        # primary_ratesum_greedy = get_pairwise_rates_primary(In_range_pair, In_range_sats,gs_pair_list,sol_arr_ptgd,G_pair_labels)
        # plot_rates_for_pairs(primary_ratesum, primary_maxmin, primary_ratesum_frac, primary_maxmin_frac,pair_max, primary_ratesum_greedy, no_of_gs_pairs)
        
        # sol_arr = iterative_max_min(G_pair_labels, 1, sat_list, gs_list, gs_pair_list, T, R, L, gs_to_pair_mapping, In_range_pair_fraction, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, Is_discrete)
        # rates_iter1 = get_pairwise_rates_primary(In_range_pair, In_range_sats,gs_pair_list,sol_arr,G_pair_labels)

        # sol_arr = iterative_max_min(G_pair_labels, len(gs_pair_list), sat_list, gs_list, gs_pair_list, T, R, L, gs_to_pair_mapping, In_range_pair_fraction, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, Is_discrete)
        # rates_iter2 = get_pairwise_rates_primary(In_range_pair, In_range_sats,gs_pair_list,sol_arr,G_pair_labels)
        # sol_arr = iterative_max_min(G_pair_labels, 3, sat_list, gs_list, gs_pair_list, T, R, L, gs_to_pair_mapping, In_range_pair_fraction, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, Is_discrete)
        # rates_iter3 = get_pairwise_rates_primary(In_range_pair, In_range_sats,gs_pair_list,sol_arr,G_pair_labels)

       
        # print(np.array(rates_iter1))
        # print(np.array(rates_iter2))
        # print(np.array(rates_iter3))
        # plot_rates_for_pairs_maxmin(rates_iter1, rates_iter2, primary_ratesum,  len(gs_pair_list))

        # primary_ratesum = get_pairwise_frac_primary(In_range_pair, In_range_sats,gs_pair_list,sol_arr_ptd,G_pair_labels)
        # primary_maxmin = get_pairwise_frac_primary(In_range_pair, In_range_sats,gs_pair_list,sol_arr_pfd,G_pair_labels)
        # frac_ratesum = get_pairwise_frac_primary(In_range_pair, In_range_sats,gs_pair_list,sol_arr_rtd,G_pair_labels)
        # frac_maxmin = get_pairwise_frac_primary(In_range_pair, In_range_sats,gs_pair_list,sol_arr_rfd,G_pair_labels)
        
        # plot_rates_for_pairs(primary_ratesum, primary_maxmin, frac_ratesum, frac_maxmin, no_of_gs_pairs)
        # print("Printing Ratesum")
        # print(sol_ptd)
        # print("Printing Maxmin")
        # print(sol_pfd)
    end_time = time.time()
        
    # print(f"Process {mp.current_process().name} ended at {time.strftime('%H:%M:%S', time.localtime(end_time))}. Duration: {end_time - start_time:.2f} seconds")




# def write_rate_fid_data_parallel():
#     processes = []
#     for day in days:
#         for time_of_day in times_of_day:
#             for altitude in altitudes:
#                 p = mp.Process(target=generate_satellite_data, args=(day, time_of_day, altitude))
#                 processes.append(p)
#                 p.start()

#     # Ensure all processes are completed
#     for process in processes:
#         process.join()


# def split_range(t_start, t_end, num_chunks):
    
    
#     chunk_size = (t_end - t_start) // num_chunks
#     chunks = []
#     for i in range(num_chunks):
#         start = t_start + i * chunk_size
#         end = start + chunk_size - 1 if i < num_chunks - 1 else t_end - 1
#         chunks.append((start, end))

#     return chunks


############### SPLIT TIME CODE #####################
num_splits = 2
def split_time_range(start, end, num_splits):
    step = (end - start) // num_splits
    return [(start + i * step, start + (i + 1) * step - 1) for i in range(num_splits - 1)] + [(start + (num_splits - 1) * step, end)]
############### SPLIT TIME CODE #####################


# Possible values for each argument
dates = ['09/15/2022']  # 09/15/2022, '03/15/2022', '06/15/2022', '12/15/2022'
altitudes = [1500000] #, 500000, 1000000, 1500000, 2000000
algos = ["primary-maxmin"]  # "primary-maxmin" , "primary-ratesum"
start_time = 500
end_time = 500 # Till 86399
arg_options = [(10, 10, 10)]  # Only 3 possibilities [1,5,10]



param_combinations = [
    (d, alti, algos, st, et, *args) 
    for d, alti, algos, st, et, args in itertools.product(dates, altitudes, algos, [start_time], [end_time], arg_options)
]

# Print the generated combinations
print(param_combinations)





############### SPLIT TIME CODE #####################
# split_param_combinations = []
# for params in param_combinations:
#     d, v, r, st, et, T, R, L = params
#     split_times = split_time_range(st, et, num_splits)
#     for t_start, t_end in split_times:
#         split_param_combinations.append((d, v, r, t_start, t_end, T, R, L))
    
############### SPLIT TIME CODE #####################



if __name__ == "__main__":
    
    
    slurm_cores = int(os.getenv("SLURM_CPUS_PER_TASK", mp.cpu_count() - 1))
    print("slurm cores: ",slurm_cores)
    
    
    # change split_param_combinations to param_combinations when you do not want to split time range
    
    num_workers = min(len(param_combinations), slurm_cores)
    print("num_workers: ",num_workers)
    # print(split_param_combinations)


    start_time = time.time()  # Start time measurement

    with mp.Pool(processes=num_workers) as pool:
        pool.starmap(solve_assignment, param_combinations)
        
    end_time = time.time()  # End time measurement
    elapsed_time = end_time - start_time

    print(f"All processes completed in {elapsed_time:.2f} seconds")
    






    # [('09/15/2022', 500000, 'primary-ratesum', 0, 0, 10, 10, 10), 
    #  ('09/15/2022', 500000, 'primary-maxmin', 0, 0, 10, 10, 10), 

    #  ('09/15/2022', 1000000, 'primary-ratesum', 0, 0, 10, 10, 10), 
    #  ('09/15/2022', 1000000, 'primary-maxmin', 0, 0, 10, 10, 10), 
     
    #  ('09/15/2022', 1500000, 'primary-ratesum', 0, 0, 10, 10, 10), 
    #  ('09/15/2022', 1500000, 'primary-maxmin', 0, 0, 10, 10, 10), 
     
    #  ('09/15/2022', 2000000, 'primary-ratesum', 0, 0, 10, 10, 10), 
    #  ('09/15/2022', 2000000, 'primary-maxmin', 0, 0, 10, 10, 10)]
