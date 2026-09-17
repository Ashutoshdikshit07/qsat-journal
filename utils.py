#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 18:48:01 2022

@author: nitish
"""
from docplex.mp.model import Model
import numpy as np
from itertools import combinations
from scipy.linalg import expm
from arch_types.compute_fidelity_rate_new import fid_dd, psucc_dd
import math as mt
from numpy.linalg import norm
from scipy.optimize import minimize
import datetime
import pandas as pd
from operator import itemgetter
import copy

thetae = 20*(np.pi/180) #Elevation angle in radian
thetainc = 0 #Inclination angle in radian
rep_rate = 10**9
sat_coupling_eff = 0.707
ground_coupling_eff  = 0.707
rad_apr_sat = 0.1
rad_apr_gd = 1
lambda_= 737*(10**(-9))
deff  = 0.9
coupleGnd = 0.9
NsS = 0.0078
fid_min = 0
prefact = sat_coupling_eff*ground_coupling_eff*(np.pi*(rad_apr_sat**2)*np.pi*(rad_apr_gd**2))
dijstar_t = 5e3
trans_air = mt.e**(-0.028125*(dijstar_t/1000))
rate_th_primary = 1
rate_th_reflection = 1
list_of_locations = ['Toronto', 'NewYork', 'London', 'Singapore', 'Sydney', 'Auckland', 'Paris', 'RiodeJaneiro', 'Nice', 'Mumbai', 'Johannesburg', 'Boston', 'Dublin', 'WashingtonDC', 'Lijiang', 'Houston', 'Tucson']


def get_background_photon_flux(solar_irradiance):
    solar_irradiance = (10**7) * solar_irradiance # initial unit micro W cm-2 sr-1 nm-1, now chhanged to W m-2 sr-1 m-1
    # r = 0.5 # in m
    delta_t = 1*(10**(-9)) # in s
    delta_lambda = 1*(10**(-9)) # in m
    lambda_ = 737*(10**(-9)) # in m
    omega_fov = 10**(-10) # in sr
    h = 6.62607015*(10**(-34)) # in J·s
    c = 3*(10**8) # in m/s

    return solar_irradiance*omega_fov*mt.pi*(rad_apr_gd**2)*delta_lambda*delta_t/(h*c/lambda_)

def get_all_Pds(list_of_locations, date_list_id, locations_to_id_mapping):
    folder_dir = "weather-data/solar-irradiance-updated/"
    all_PDs = {}
    for location_name in list_of_locations:
        df = pd.read_excel(folder_dir+location_name+'.xlsx', header = None)
        location_id = locations_to_id_mapping[location_name]
        all_PDs[location_id] = []
        for j in range(4):
            all_PDs[location_id].append(get_background_photon_flux(df.iat[date_list_id+1, j+1]))
    return all_PDs

def get_vertical_air_trans(list_of_locations, date_list_id, locations_to_id_mapping):
    air_trans_vertical_list = {}
    for location_name in list_of_locations:
        df = pd.read_csv('weather-data/vertical-air-transmissivities-with-cloud-cover/'+location_name+'.csv').to_numpy()
        location_id = locations_to_id_mapping[location_name]
        air_trans_vertical_list[location_id] = list(df[:,date_list_id])
    return air_trans_vertical_list

def get_vertical_air_trans_without_cloud(list_of_locations, date_list_id, locations_to_id_mapping):
    air_trans_vertical_list_without_cloud = {}
    df = pd.read_csv('weather-data/vertical-air-transmissivities-without-cloud-cover.csv').to_numpy()
    for i in range(len(list_of_locations)):
        location_name = df[i,0]
        location_id = locations_to_id_mapping[location_name]
        air_trans_vertical_list_without_cloud[location_id] = [df[i,date_list_id+1]]*24
    return air_trans_vertical_list_without_cloud

def pre_process_sat(S, no_of_sats):
    sat_axis_list = []
    sat_loc_list = []
    for i in list(S.keys()):
        ring_axis_i=S[i]['axis']
        for j in list(S[i].keys()):
            if j=='axis':
                continue
            sat_axis_list.append(ring_axis_i)
            sat_loc_list.append(S[i][j])
    return sat_axis_list, sat_loc_list

def generate_network(num_rings,num_sats,R,h):
    S={}
    for m in range(num_rings):
        S[m]={}
        for k in range(num_sats):
            S[m][k]=generate_point(R+h,m*np.pi/num_rings,k*2*np.pi/num_sats)
        S[m]['axis']=[-np.sin(m*np.pi/num_rings),np.cos(m*np.pi/num_rings),0]
    return S

def get_constants(h):
    '''
    h is the altitude of the satellites in meters
    '''

    G=6.67408e-11 # Gravitational constant in SI units
    R=6.371e6 # Radius of the Earth in meters
    M=5.972e24 # Mass of the earth in kg
    Omega=2*np.pi/86400.  # Rotation speed of the Earth in radians/s
    t=5e3 # Thickness of the atmosphere in meters

    #Earth_axis=[0,0,1]  # Axis of rotation of the earth: taken to be along the z-axis.

    #h=1000e3 # Altitude of the satellites in meters
    omega=np.sqrt(G*M)/(R+h)**(3./2.)  # Rotation speed of the satellites in radians/s

    #period=2*np.pi/omega # Period of each satellite in seconds.

    return G,R,M,Omega,t,h,omega

def generate_point(R,theta,phi):
    return [R*np.sin(phi)*np.cos(theta),R*np.sin(phi)*np.sin(theta),R*np.cos(phi)]

def get_GS_locations(R, list_of_locations_coords, locations_to_id_mapping):
    G_coords={}    
    for location in list_of_locations_coords:
        longt, lat = list_of_locations_coords[location]
        location_id = locations_to_id_mapping[location]
        G_coords[location_id] = generate_point(R,longt*np.pi/180,np.pi/2-(lat*np.pi/180))
    
    g=list(G_coords.keys())        
    no_of_gs = len(g)
    
    combs=list(combinations(g,2))
    
    G_pair_labels=[]
    gs_to_pair_mapping = {}
    for i in g:
        gs_to_pair_mapping[i] = []
    
    for i in range(len(combs)):
        comb = combs[i]
        G_pair_labels.append((comb[0],comb[1]))
        gs_to_pair_mapping[comb[0]].append(i)
        gs_to_pair_mapping[comb[1]].append(i)
    
    return  G_coords, G_pair_labels, gs_to_pair_mapping, no_of_gs


def generate_rotation(axis,angle):
    # Generators of the SO(3) rotations
    Lx=np.matrix([[0,0,0],[0,0,-1],[0,1,0]])
    Ly=np.matrix([[0,0,1],[0,0,0],[-1,0,0]])
    Lz=np.matrix([[0,-1,0],[1,0,0],[0,0,0]])
    
    n1=axis[0]
    n2=axis[1]
    n3=axis[2]
    
    L=n1*Lx+n2*Ly+n3*Lz
    
    return np.matrix(expm(angle*L))

def evolve_vector(init_point,axis,omega,T):
    init_point=np.matrix(init_point).H
    
    R=generate_rotation(axis,omega*T)
    point_t=R*init_point

    point_t_x=np.array(point_t[0])[0][0]
    point_t_y=np.array(point_t[1])[0][0]
    point_t_z=np.array(point_t[2])[0][0]
    
    return [point_t_x,point_t_y,point_t_z]


def get_ent_rates(dA,dB, air_trans1, air_trans2, Pd, h):
    # s1star_t = get_air_dist(6.371e6, 6.371e6 + 5e3, 6.371e6 + h, dA)
    # s2star_t = get_air_dist(6.371e6, 6.371e6 + 5e3, 6.371e6 + h, dB)
    # air_trans1 = mt.e**(-0.028125*(s1star_t/1000))
    # air_trans2 = mt.e**(-0.028125*(s2star_t/1000))

    trnsA = prefact*air_trans1/((lambda_*dA)**2)
    trnsB = prefact*air_trans2/((lambda_*dB)**2)
    succ_prob = psucc_dd(NsS,trnsA,trnsB, Pd)
    fid = fid_dd(NsS,trnsA,trnsB, Pd)           

    return rep_rate*succ_prob, fid


def get_sats_in_range(G, Earth_axis,earth_omega,t, sat_loc_list, sat_axis_list, sat_omega, thetae):
    connectivity = {}
    elev_angle = {}
    for j in range(len(G)):
        connectivity[j] = {}
        elev_angle[j] = {}
        gj_pos_evolve = evolve_vector(G[j],Earth_axis,earth_omega,t)
        for i in range(len(sat_axis_list)):
            sati_pos=evolve_vector(sat_loc_list[i],sat_axis_list[i],sat_omega,t)
            gij_diff=np.array(sati_pos)-np.array(gj_pos_evolve)
            dij=norm(gij_diff)
            cos_angleij=np.dot(gij_diff,gj_pos_evolve)/(norm(gij_diff)*norm(gj_pos_evolve))
            if cos_angleij>=np.cos((np.pi/2)-thetae):
                connectivity[j][i] = dij
                elev_angle[j][i] = (np.pi/2)-np.arccos(cos_angleij)
    return connectivity, elev_angle
                        
def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))
          
def evolve_network(sat_axis_list, sat_loc_list,G,G_pair_labels,t,h,earth_omega,thetae, algo_type, no_of_sats, time_diff, air_trans_vertical_list, all_pd_list):    
    Earth_axis=[0,0,1]    
    _,R_e,_,_,h_air,_,_=get_constants(1000)
      
    In_range_pair = {}
    In_range_sats = {}
    In_range_gs_pairs = {}
    In_range_pair_fidelity = {}

    In_range_pair_reflection = {}
    In_range_sats_reflection = {}
    In_range_gs_pairs_reflection = {}
    In_range_pair_fidelity_reflection = {}

    for i in range(len(sat_axis_list)):
        In_range_gs_pairs[i] = []
        In_range_gs_pairs_reflection[i] = []

    _,_,_,_,_,_,sat_omega=get_constants(h)
    connectivity, elev_angle = get_sats_in_range(G, Earth_axis,earth_omega,t, sat_loc_list, sat_axis_list, sat_omega, thetae)
    
    for j in range(len(G_pair_labels)):
        g1_label, g2_label = G_pair_labels[j]
 
        sats_g1 = list(connectivity[g1_label].keys())
        sats_g2 = list(connectivity[g2_label].keys())

        if(sats_g1 and sats_g2):
            local_time_hour1 = int(((t + time_diff[g1_label])%86400)/3600)
            local_time_hour2 = int(((t + time_diff[g2_label])%86400)/3600)
            local_time_quarter_day1 = int(((t + time_diff[g1_label])%86400)/21600)
            local_time_quarter_day2 = int(((t + time_diff[g2_label])%86400)/21600)
            air_trans1_vertical = air_trans_vertical_list[g1_label][local_time_hour1]
            air_trans2_vertical = air_trans_vertical_list[g2_label][local_time_hour2]
           
            Pd1 = all_pd_list[g1_label][local_time_quarter_day1]
            Pd2 = all_pd_list[g2_label][local_time_quarter_day2]
            Pd = max(Pd1, Pd2)

            primary_sats = intersection(sats_g1, sats_g2)
            # print(primary_sats)
            if(primary_sats):
                In_range_sats[j] = []
                for i in primary_sats:
                    air_trans1 = air_trans1_vertical**(1/np.sin(elev_angle[g1_label][i]))
                    air_trans2 = air_trans2_vertical**(1/np.sin(elev_angle[g2_label][i]))
                    rate, fid = get_ent_rates(connectivity[g1_label][i],connectivity[g2_label][i], air_trans1,air_trans2, Pd, h)
                    if(rate > rate_th_primary):
                        In_range_pair_fidelity[(i,j)] = fid
                        In_range_pair[(i,j)] = rate
                        In_range_sats[j].append(i)
                        In_range_gs_pairs[i].append(j)
                if not In_range_sats[j]:
                    del In_range_sats[j]

            if(algo_type == 'reflection-ratesum' or algo_type == 'reflection-maxmin'):
                In_range_sats_reflection[j] = []
                secondary_sats1 = list(set(sats_g1)-set(primary_sats))
                secondary_sats2 = list(set(sats_g2)-set(primary_sats))
                for i in secondary_sats1:
                    air_trans1 = air_trans1_vertical**(1/np.sin(elev_angle[g1_label][i]))
                    for k in secondary_sats2:
                        air_trans2 = air_trans2_vertical**(1/np.sin(elev_angle[g2_label][k]))
                        sat_pos_i=evolve_vector(sat_loc_list[i],sat_axis_list[i],sat_omega,t)
                        sat_pos_k=evolve_vector(sat_loc_list[k],sat_axis_list[k],sat_omega,t)
                        d_sat_i_k = norm(np.array(sat_pos_i)-np.array(sat_pos_k))
                        const_3 = (h+R_e)**2 - (d_sat_i_k/2)**2 >= R_e**2 # Condition that satellite A and B are in line-of-sight
                        if(const_3):
                            rate, fid = get_ent_rates(connectivity[g1_label][i], connectivity[g2_label][k]+d_sat_i_k, air_trans1,air_trans2, Pd, h)
                            if(rate > rate_th_reflection):
                                In_range_pair_reflection[(i,k,j)] = rate
                                In_range_pair_fidelity_reflection[(i,k,j)] = fid
                                In_range_sats_reflection[j].append((i, k))
                                In_range_gs_pairs_reflection[i].append((1,k,j))
                                In_range_gs_pairs_reflection[k].append((2,i,j))
                if not In_range_sats_reflection[j]:
                    del In_range_sats_reflection[j]
    for key in list(In_range_gs_pairs_reflection):
        if not In_range_gs_pairs_reflection[key]:
            del In_range_gs_pairs_reflection[key]
            
    for key in list(In_range_gs_pairs):
        if not In_range_gs_pairs[key]:
            del In_range_gs_pairs[key]
    
    gs_pair_list = list(set(In_range_sats.keys()) | set(In_range_sats_reflection.keys()))
    sat_list = list(set(In_range_gs_pairs.keys()) | set(In_range_gs_pairs_reflection.keys()))
    gs_list = []
    for j in gs_pair_list:
        g1_label, g2_label = G_pair_labels[j]
        if(g1_label not in gs_list):
            gs_list.append(g1_label)
        if(g2_label not in gs_list):
            gs_list.append(g2_label) 
    return sat_list, gs_list, gs_pair_list, In_range_pair, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, In_range_pair_reflection, In_range_sats_reflection, In_range_gs_pairs_reflection, In_range_pair_fidelity_reflection

def get_max_min_fairness_index(In_range_pair, solution, In_range_sats,gs_pair_list):
    var_list = list(In_range_pair.keys())
    mmf_min = 10**10
    mmf_max = -1000000 
    for j in gs_pair_list: 
        if(j in In_range_sats):
            sum_ = 0
            for i in In_range_sats[j]:
                sum_ += In_range_pair[(i,j)]*solution[(i,j)]
            if(sum_ < mmf_min):
                mmf_min = sum_   
            if(sum_ > mmf_max):
                mmf_max = sum_       
    return mmf_min

    # return (mmf_min**2)/(mmf_max**2)

def solve_primary(sat_list, gs_list, gs_pair_list, T, R, L, gs_to_pair_mapping, In_range_pair, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, Is_discrete):  
    var_list = list(In_range_pair.keys())
    # print("Number of non-zero primary: "+str(len(var_list)))
    primary_model = Model('primary')
    if(Is_discrete):
        x = primary_model.integer_var_dict(var_list, lb = 0, name="x")
    else:
        x = primary_model.continuous_var_dict(var_list, lb = 0, name="x")    
    obj = [In_range_pair[(i,j)]*x[(i,j)] for (i,j) in var_list]
    primary_model.maximize(sum(obj))

    for g in gs_list:
        const1 = []
        for j in gs_to_pair_mapping[g]:
            if j in In_range_sats:
                for i in In_range_sats[j]:
                    const1.append(x[(i,j)])
        if(const1):
            primary_model.add_constraint(sum(const1) <= R)
    for i in sat_list: 
        const2 = []
        if i in In_range_gs_pairs:
            for j in In_range_gs_pairs[i]:
                const2.append(x[(i,j)])
        if(const2):
            primary_model.add_constraint(sum(const2) <= T)
    for j in gs_pair_list: 
        const3 = []
        if j in In_range_sats:
            for i in In_range_sats[j]: 
                const3.append(x[(i,j)])
        if(const3):
            primary_model.add_constraint(sum(const3) <= L)
        
    sol = primary_model.solve()
    if sol is None:
        return 0, {}
    else:
        solution = {}
        for (i,j) in var_list:
            solution[(i,j)] = x[(i,j)].solution_value
        max_min_index = get_max_min_fairness_index(In_range_pair, solution, In_range_sats,gs_pair_list)
        return sol.get_objective_value(), max_min_index, solution

def solve_primary_fair(sat_list, gs_pair_list, gs_list, T_arr, R_arr, L_arr, gs_to_pair_mapping, In_range_pair, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, Is_discrete):  
    var_list = list(In_range_pair.keys())
    primary_model = Model('primary')
    if(Is_discrete):
        x = primary_model.integer_var_dict(var_list,lb = 0, name="x")
    else:
        x = primary_model.continuous_var_dict(var_list, lb = 0, name="x")
    variable_theta = primary_model.continuous_var(name='theta')
    primary_model.maximize(variable_theta)
    
    for g in gs_list:
        const1 = []
        for j in gs_to_pair_mapping[g]:
            if j in In_range_sats:
                for i in In_range_sats[j]:
                    const1.append(x[(i,j)])
        if(const1): 
            primary_model.add_constraint(sum(const1) <= R_arr[g])
    for i in sat_list: 
        const2 = []
        if i in In_range_gs_pairs:
            for j in In_range_gs_pairs[i]:
                const2.append(x[(i,j)])
        if(const2): 
            primary_model.add_constraint(sum(const2) <= T_arr[i])
    for j in gs_pair_list: 
        const3 = []
        if j in In_range_sats:
            for i in In_range_sats[j]: 
                const3.append(x[(i,j)])
        if(const3):  
            primary_model.add_constraint(sum(const3) <= L_arr[j])
        
    for j in gs_pair_list: 
        const4 = []
        if j in In_range_sats:
            for i in In_range_sats[j]: 
                const4.append(-1*In_range_pair[(i,j)]*x[(i,j)])    
        if(const4): 
            const4.append(variable_theta)   
            primary_model.add_constraint(sum(const4) <= 0)

    sol = primary_model.solve()
    if sol is None:
        return 0, 0, {}
    else:
        solution = {}
        throughput_fair = 0
        for (i,j) in var_list:
            solution[(i,j)] = x[(i,j)].solution_value
            throughput_fair += In_range_pair[(i,j)]*x[(i,j)].solution_value
        solution['theta'] = variable_theta.solution_value
        # max_min_index = get_max_min_fairness_index(In_range_pair, solution, In_range_sats,gs_pair_list)
        return throughput_fair, 0, solution
        # return throughput_fair, solution

def solve_primary_greedy(T, R, L, G_pair_labels, In_range_pair, no_of_sats, no_of_gs,no_of_gs_pairs):
    T_arr = [T]*no_of_sats
    R_arr = [R]*no_of_gs
    L_arr = [L]*no_of_gs_pairs
    solution = {}
    sorted_rates = {k: v for k,v in sorted(In_range_pair.items(), key=itemgetter(1), reverse=True)}
    rate_keys = list(sorted_rates.keys())
    sum_rate = 0
    for (i,j) in rate_keys:
        solution[(i,j)] = 0
        g1, g2 = G_pair_labels[j]
        if(T_arr[i] > 0 and R_arr[g1] > 0 and R_arr[g2] > 0 and L_arr[j] > 0):
            resources = min(T_arr[i], R_arr[g1],R_arr[g2],L_arr[j] )
            solution[(i,j)] = resources
            sum_rate += In_range_pair[(i,j)]*resources
            T_arr[i] -= resources
            R_arr[g1] -= resources
            R_arr[g2] -= resources
            L_arr[j] -= resources
    return  sum_rate, solution   

# def solve_reflection_greedy(T, R, L, G_pair_labels, In_range_pair, In_range_pair_reflection, no_of_sats, no_of_gs,no_of_gs_pairs):
#     T_arr = [T]*no_of_sats
#     R_arr = [R]*no_of_gs
#     L_arr = [L]*no_of_gs_pairs

#     merged_dict = In_range_pair | In_range_pair_reflection
#     solution = {}
#     sorted_rates = {k: v for k,v in sorted(merged_dict.items(), key=itemgetter(1), reverse=True)}
#     rate_keys = list(sorted_rates.keys())
#     sum_rate = 0
#     for key in rate_keys:
#         solution[key] = 0
#         if(len(key) == 2):
#             (i,j) = key
#             g1, g2 = G_pair_labels[j]
#             if(T_arr[i] > 0 and R_arr[g1] > 0 and R_arr[g2] > 0 and L_arr[j] > 0):
#                 solution[(i,j)] = 1
#                 sum_rate += In_range_pair[(i,j)]
#                 T_arr[i] -= 1
#                 R_arr[g1] -= 1
#                 R_arr[g2] -= 1
#                 L_arr[j] -= 1
#         else:
#             (i,k,j) = key
#             g1, g2 = G_pair_labels[j]
#             if(T_arr[i] > 0 and T_arr[k] > 0 and R_arr[g1] > 0 and R_arr[g2] > 0 and L_arr[j] > 0):
#                 solution[(i,k,j)] = 1
#                 sum_rate += In_range_pair_reflection[(i,k,j)]
#                 T_arr[i] -= 1
#                 T_arr[k] -= 1
#                 R_arr[g1] -= 1
#                 R_arr[g2] -= 1
#                 L_arr[j] -= 1

#     return  sum_rate, solution 

def solve_reflection(no_of_sats, no_of_gs_pairs, no_of_gs, T, R, L, gs_to_pair_mapping, In_range_pair, In_range_sats, In_range_gs_pairs,In_range_pair_reflection, In_range_sats_reflection, In_range_gs_pairs_reflection):  
    var_list_primary = list(In_range_pair.keys())
    var_list_reflection = list(In_range_pair_reflection.keys())
    
    print("Number of non-zero primary: "+str(len(var_list_primary)))
    print("Number of non-zero reflection: "+str(len(var_list_reflection)))                
                
    secondary_model = Model('secondary')
    print("Inside secondary")
    x = secondary_model.binary_var_dict(var_list_primary + var_list_reflection, name="x")
    
    obj1 = [In_range_pair[(i,j)]*x[(i,j)] for (i,j) in var_list_primary]
    obj2 = [In_range_pair_reflection[(i,k,j)]*x[(i,k,j)]for (i,k,j) in var_list_reflection]
    
    secondary_model.maximize(sum(obj1+obj2))
    for g in range(no_of_gs):
        const1 = []
        for j in gs_to_pair_mapping[g]:
            for i in In_range_sats[j]:
                const1.append(x[(i,j)])
            for l in In_range_sats_reflection[j]:
                i,k = l
                const1.append(x[(i,k,j)])
        if(const1):
            secondary_model.add_constraint(sum(const1) <= R)


    for i in range(no_of_sats): 
        const2 = []
        for j in In_range_gs_pairs[i]:
            const2.append(x[(i,j)])
        for l in In_range_gs_pairs_reflection[i]:
            idp, k, j = l    
            if(idp == 1):
                const2.append(x[(i,k,j)])
            else:
                const2.append(x[(k,i,j)])   
        if(const2):
            secondary_model.add_constraint(sum(const2) <= T)


    for j in range(no_of_gs_pairs):
        const3 = []
        for i in In_range_sats[j]:
            const3.append(x[(i,j)])
        for l in In_range_sats_reflection[j]:
            i,k = l
            const3.append(x[(i,k,j)])
        if(const3):
            secondary_model.add_constraint(sum(const3) <= L)
        
    sol = secondary_model.solve()
    if sol is None:
        return 0
    else:
        return sol.get_objective_value()

def get_air_dist(re, ra, ro, s):
    theta1 = np.arccos((re**2 + s**2 - ro**2)/(2*re*s))
    G1t = np.arcsin(re*np.sin(theta1)/(ra))
    thetastar1 = np.pi - theta1 - G1t
    
    return np.sqrt(ra**2 + re**2 - (2*ra*re*np.cos(thetastar1)))

def get_pairwise_frac_primary(In_range_pair, In_range_sats,gs_pair_list,sol_arr,G_pair_labels):
    frac_arr_pair = []
    for j in gs_pair_list: 
        sum_ = 0.0
        sum_could_have = 0.0
        if(In_range_sats[j]):
            for i in In_range_sats[j]:
                sum_ += In_range_pair[(i,j)]*sol_arr[(i,j)] 
                sum_could_have += In_range_pair[(i,j)]
        if(sum_could_have > 0):
            frac_arr_pair.append(sum_/sum_could_have)
        else:
            frac_arr_pair.append(0)
    return frac_arr_pair

def get_pairwise_rates_primary(In_range_pair, In_range_sats,gs_pair_list,sol_arr,G_pair_labels):
    rate_arr_pair = []
    for j in gs_pair_list: 
        sum_ = 0.0
        if(In_range_sats[j]):
            for i in In_range_sats[j]:
                sum_ += In_range_pair[(i,j)]*sol_arr[(i,j)] 
        rate_arr_pair.append(sum_)
    return rate_arr_pair

def get_pairwise_rates_reflection(In_range_pair, In_range_sats,gs_pair_list,sol_arr):
    rate_arr_pair = []
    for j in gs_pair_list: 
        sum_ = 0
        if(In_range_sats[j]):
            for i in In_range_sats[j]:
                sum_ += In_range_pair[(i,j)]*sol_arr[(i,j)] 
        rate_arr_pair.append(sum_)
    return rate_arr_pair

def find_fraction_per_pair(In_range_pair, In_range_sats, gs_pair_list):
    In_range_pair_could_have = {}
    Sum_rates_pairs = {}
    for j in gs_pair_list:
        Sum_rates_j = 0
        for i in In_range_sats[j]:
            Sum_rates_j += In_range_pair[(i,j)]
        Sum_rates_pairs[j] = Sum_rates_j
    for (i,j) in In_range_pair:
        In_range_pair_could_have[(i,j)] = In_range_pair[(i,j)]/Sum_rates_pairs[j]
    return In_range_pair_could_have

def find_mininmum_set(sol_arr_pfd,In_range_pair_base, G_pair_labels, In_range_sats_base):
    Sum_rates_pairs = {}
    for j in In_range_sats_base:
        Sum_rates_j = 0
        for i in In_range_sats_base[j]:
            Sum_rates_j += In_range_pair_base[(i,j)]
        Sum_rates_pairs[j] = Sum_rates_j
    temp = min(Sum_rates_pairs.values())
    pair_min_set = [key for key in Sum_rates_pairs if Sum_rates_pairs[key] == temp]
    
    return pair_min_set
def iterative_max_min(G_pair_labels, max_iters, sat_list, gs_list, gs_pair_list, T, R, L, gs_to_pair_mapping, In_range_pair, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, Is_discrete): 
    T_arr = {}
    L_arr = {}
    R_arr = {}
    for i in sat_list:
        T_arr[i] = T
    for j in gs_pair_list:
        L_arr[j] = L
    for g in gs_list:
        R_arr[g] = R
    
    In_range_pair_base =  In_range_pair.copy()
    In_range_sats_base =  In_range_sats.copy()
    In_range_gs_pairs_base = copy.deepcopy(In_range_gs_pairs)

    sol_pfd, mmf_pfd, sol_arr_pfd = solve_primary_fair(sat_list, gs_pair_list, gs_list,T_arr, R_arr, L_arr, gs_to_pair_mapping, In_range_pair_base, In_range_sats_base, In_range_gs_pairs_base, In_range_pair_fidelity, Is_discrete)
    sol_arr = sol_arr_pfd.copy()
    
    for iteration in range(max_iters-1):
        pair_min_set = find_mininmum_set(sol_arr_pfd,In_range_pair_base, G_pair_labels,In_range_sats_base)    
       
        # print("----")
        # print(pair_min_set)
        # print("----")
       
        for j in pair_min_set:
            g1,g2 = G_pair_labels[j]
            for i in In_range_sats_base[j]:
                del In_range_pair_base[(i,j)]
                In_range_gs_pairs_base[i].remove(j)
                T_arr[i] -= sol_arr_pfd[(i,j)]
                L_arr[j] -= sol_arr_pfd[(i,j)]
                R_arr[g1] -= sol_arr_pfd[(i,j)]
                R_arr[g2] -= sol_arr_pfd[(i,j)]
            del In_range_sats_base[j]   
        sol_pfd, mmf_pfd, sol_arr_pfd = solve_primary_fair(sat_list, gs_pair_list, gs_list,T_arr, R_arr, L_arr, gs_to_pair_mapping, In_range_pair_base, In_range_sats_base, In_range_gs_pairs_base, In_range_pair_fidelity, Is_discrete)
        if(not sol_arr_pfd):
            return sol_arr
        if(sol_arr_pfd['theta'] == 0):
            return sol_arr
        for key in In_range_pair_base:
            sol_arr[key] = sol_arr_pfd[key]
    return sol_arr
