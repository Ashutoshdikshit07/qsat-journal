from utils import *
import numpy as np
import matplotlib.pyplot as plt
import math as mt 
import networkx as nx

def box_plot(data, label):
    fig = plt.figure(figsize =(10, 7))
     
    # Creating plot
    plt.boxplot(data)
     
    plt.grid('on')
    # plt.xlabel('Probability',fontsize=16)
    plt.ylabel('Ent. Distribution Rate',fontsize=18)
    plt.title("t = 1 ("+label+")",fontsize=16)

    # plt.title("Ground Stations: "+gs1+ ", "+gs2+ "("+label+")",fontsize=16)
    plt.tight_layout()
    plt.savefig("plots/t1_"+label+'.pdf')   
    plt.show()

def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color)
    plt.setp(bp['caps'], color=color)
    plt.setp(bp['medians'], color=color)

def box_plot_rate_fid_primary(data1, data2, x_arr, label):
    fig = plt.figure(figsize =(14, 7))
    bpl1 = plt.boxplot(data1, positions=x_arr*2+0.4, sym='', widths=0.3) 
    bpl2 = plt.boxplot(data2, positions=x_arr*2-0.4, sym='', widths=0.3)

    set_box_color(bpl1, '#D7191C')
    set_box_color(bpl2, '#2C7BB6')


    plt.plot([], c='#D7191C', label='Primary (Greedy)')
    plt.plot([], c='#2C7BB6', label='Reflection (Greedy)')
    plt.legend()
     
    plt.grid('on')
    plt.xlabel('Time (in hours)',fontsize=16)
    plt.ylabel(label,fontsize=18)
    # plt.title("t = 1 ("+label+")",fontsize=16)

    # plt.title("Ground Stations: "+gs1+ ", "+gs2+ "("+label+")",fontsize=16)
    plt.tight_layout()
    plt.savefig("plots/hourly_metric_"+label+'_greedy.pdf')   
    plt.show()

def plot_time_series(t_range, data1, data2, label1, label2,date, plot_type, altitude):
    date_to_text = {'03/15/2022':'March 15, 2022', '06/15/2022':'June 15, 2022', '09/15/2022':'September 15, 2022', '12/15/2022':'December 15, 2022'}
    file_name = {'03/15/2022':'march', '06/15/2022':'june', '09/15/2022':'september', '12/15/2022':'december'}
    fig = plt.figure(figsize =(10, 7))
    plt.plot(t_range, data1, 'rs-', linewidth=2, label=label1)
    plt.plot(t_range, data2, 'gs-', linewidth=2, label=label2) 
     
    plt.grid('on')
    plt.xlabel('t',fontsize=18)
    plt.ylabel('Ent. Distribution Rate',fontsize=18)
    plt.legend(prop={'size': 12})

    plt.title("Date: "+date_to_text[date],fontsize=16)
    plt.tight_layout()
    plt.savefig('plots/'+file_name[date]+'/time_series_altitude'+str(altitude)+'_'+plot_type+'_rate.pdf')   
    plt.show()
def plot_alt_perf(alt, primary_d, primary_fair_d, primary_c, primary_fair_c, mmf_primary_d, mmf_primary_fair_d, mmf_primary_c, mmf_primary_fair_c,T, R, L):
    # fig = plt.figure(figsize =(10, 7))
    color = 'tab:red'
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('altitude (in km)',fontsize=18)
    ax1.set_ylabel('Throughput',fontsize=18)
    ax1.set_title("T = "+str(T)+', R = '+str(R)+', L = '+str(L),fontsize=16)

    ax1.plot(alt, primary_d, 'rs-', linewidth=2, label='Aggregate (Binary)')
    ax1.plot(alt, primary_c, 'bs-', linewidth=2, label='Aggregate (Continuous)')
    ax1.plot(alt, primary_fair_d, 'gs-', linewidth=2, label='Max-min (Binary)') 
    ax1.plot(alt, primary_fair_c, 'ms-', linewidth=2, label='Max-min (Continuous)') 

    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('MMF index', color=color)  # we already handled the x-label with ax1

    ax2.plot(alt, mmf_primary_d, 'rs--', linewidth=2, label='Aggregate (Binary)')
    ax2.plot(alt, mmf_primary_c, 'bs--', linewidth=2, label='Aggregate (Continuous)')
    ax2.plot(alt, mmf_primary_fair_d, 'gs--', linewidth=2, label='Max-min (Binary)') 
    ax2.plot(alt, mmf_primary_fair_c, 'ms--', linewidth=2, label='Max-min (Continuous)') 

     
    # plt.grid('on')
    # plt.xlabel('altitude (in km)',fontsize=18)
    # plt.ylabel('Ent. Distribution Rate',fontsize=18)
    plt.legend(prop={'size': 12})
    # plt.xticks(xrange(0, len(ticks) * 2, 2), ticks)
    # plt.xlim(-2, len(ticks)*2)
    # plt.title("T = "+str(T)+', R = '+str(R)+', L = '+str(L),fontsize=16)
    # plt.tight_layout()
    plt.savefig('plots/alt_perf_fairness_all_T'+str(T)+'_R'+str(R)+'_L'+str(L)+'_dual_axis.pdf')   
    # plt.savefig('plots/alt_perf_fairness_continuous.pdf')   
    plt.show()

def get_rate_fidelity_from_solution(sol_arr,In_range_pair, In_range_pair_fidelity, In_range_pair_reflection, In_range_pair_fidelity_reflection):
    var_list = list(sol_arr.keys())
    fid_arr = [] 
    rate_arr = []
    for key in var_list:
        if(sol_arr[key] == 1):
            if(len(key) == 2):
                fid_arr.append(In_range_pair_fidelity[key])
                rate_arr.append(In_range_pair[key])
            else:
                rate_arr.append(In_range_pair_reflection[key])    
                fid_arr.append(In_range_pair_fidelity_reflection[key])
    return rate_arr, fid_arr

def get_rate_fidelity_from_solution(gs_pair_id, sol_arr,In_range_pair, In_range_pair_fidelity, In_range_pair_reflection, In_range_pair_fidelity_reflection):
    var_list = list(sol_arr.keys())
    for key in var_list:        
        if(sol_arr[key] == 1 and key[-1] == gs_pair_id):
            if(len(key) == 2):
                return In_range_pair[key], In_range_pair_fidelity[key]
            else:
                return In_range_pair_reflection[key], In_range_pair_fidelity_reflection[key]
    return 0, 0

def plot_rates_for_pairs(In_range_pair, In_range_sats,no_of_gs_pairs, sol_arr_pd,sol_arr_pfd):
    rate_arr_pair = []
    rate_arr_pair_fair = []
    for j in range(no_of_gs_pairs): 
        sum_ = 0
        sum_fair = 0
        if(In_range_sats[j]):
            for i in In_range_sats[j]:
                sum_ += In_range_pair[(i,j)]*sol_arr_pd[(i,j)] 
                sum_fair += In_range_pair[(i,j)]*sol_arr_pfd[(i,j)]
        # if(sum_>10 and sum_<5000):        
            rate_arr_pair.append(sum_)
        # if(sum_fair > 10 and sum_fair<5000):    
            rate_arr_pair_fair.append(sum_fair)
    fig = plt.figure(figsize =(10, 7))
    plt.plot(range(len(rate_arr_pair)), sorted(rate_arr_pair), 'rs-', linewidth=1, label='Throughput')
    plt.plot(range(len(rate_arr_pair_fair)), sorted(rate_arr_pair_fair), 'gs-', linewidth=1, label='Fair') 
    plt.yscale('log')
    plt.grid('on')
    plt.xlabel('Pair id',fontsize=18)
    plt.ylabel('Ent. Distribution Rate',fontsize=18)
    plt.legend(prop={'size': 12})
    plt.tight_layout()
    plt.savefig('plots/pair_rate_log.pdf')   
    plt.show()

def draw_nx_bipartite(bipartite_node_arr_1,bipartite_node_arr_2,bipartite_edge_arr, type_):
    B = nx.Graph()
    B.add_nodes_from(bipartite_node_arr_1, bipartite=0)
    B.add_nodes_from(bipartite_node_arr_2, bipartite=1)
    B.add_weighted_edges_from(bipartite_edge_arr)

    print(len(bipartite_edge_arr))
    print(bipartite_edge_arr)


    top = [n for n in B.nodes if B.nodes[n]['bipartite'] == 0]
    pos = nx.bipartite_layout(B, top)
    nx.draw(B, pos=pos, node_size = 1)

    # l, r = nx.bipartite.sets(B)
    # pos = {}
    # pos.update((node, (1, index)) for index, node in enumerate(l))
    # pos.update((node, (2, index)) for index, node in enumerate(r))

    # nx.draw(B)

    # labels = nx.get_edge_attributes(B,'weight')
    # nx.draw_networkx_edge_labels(B,pos,edge_labels=labels)

    plt.savefig('plots/pair_sat_bipartite_'+type_+'.pdf')   
    plt.show()

def visualize_pairs_sats(In_range_sats, In_range_pair, sol_arr_pd,sol_arr_pfd, no_of_gs_pairs):
    bipartite_node_arr_1 = []
    bipartite_node_arr_2 = []
    bipartite_edge_arr_all = []
    bipartite_edge_arr_pd = []
    bipartite_edge_arr_pfd = []

    for j in range(no_of_gs_pairs): 
        sum_ = 0
        sum_fair = 0
        if(In_range_sats[j]):
            bipartite_node_arr_1.append('pair_'+str(j))
            for i in In_range_sats[j]:
                if(i not in bipartite_node_arr_2):
                    bipartite_node_arr_2.append('sat_'+str(i))
                bipartite_edge_arr_all.append(('sat_'+str(i),'pair_'+str(j),In_range_pair[(i,j)]))
                if(sol_arr_pd[(i,j)] > 0):
                    bipartite_edge_arr_pd.append(('sat_'+str(i),'pair_'+str(j),In_range_pair[(i,j)]*sol_arr_pd[(i,j)]))
                if(sol_arr_pfd[(i,j)] > 0):
                    bipartite_edge_arr_pfd.append(('sat_'+str(i),'pair_'+str(j),In_range_pair[(i,j)]*sol_arr_pfd[(i,j)]))

    draw_nx_bipartite(bipartite_node_arr_1,bipartite_node_arr_2,bipartite_edge_arr_all, 'all')
    draw_nx_bipartite(bipartite_node_arr_1,bipartite_node_arr_2,bipartite_edge_arr_pd, 'throughput')
    draw_nx_bipartite(bipartite_node_arr_1,bipartite_node_arr_2,bipartite_edge_arr_pfd, 'fair')

if __name__=="__main__":
    t = 1
    alt_arr = range(500000, 550000,50000)
    date = '12/15/2022'
    arch_type = 'dd'
    algo_type = 'optimal-primary'
    no_of_rings = 20
    no_of_sats_in_each_ring = 20
    T = 10
    R = 10
    L = 10
    no_of_sats = no_of_rings * no_of_sats_in_each_ring
    list_of_locations = ['Toronto', 'NewYork', 'London', 'Singapore', 'Sydney', 'Auckland', 'Paris', 'RiodeJaneiro', 'Nice', 'Mumbai', 'Johannesburg', 'Boston', 'Dublin', 'WashingtonDC', 'Lijiang', 'Houston', 'Tucson']
    list_of_locations_coords = [(-79.38,43.6532), (-74.00,40.7128),(-0.127,51.5074), (103.819,1.3521),(151.209,-33.868), (174.763,-36.848),(2.3522,48.86), (-43.17,-22.9068),(7.2620, 43.7102), (72.877,19.0760),(28.04,-26.2041), (-71.06,42.36),(-6.26,53.35), (-77.0396,38.072),(100.2277,26.855), (-95.3698,29.7604),(-110.97,32.25)]
    _,earth_rad,_,earth_omega,_,_,_=get_constants(1000)
    time_diff = {}
    for j in range(len(list_of_locations)):
        time_diff[j] = get_time_difference(list_of_locations_coords[j])
    G, G_pair_labels, gs_to_pair_mapping, no_of_gs = get_GS_locations(earth_rad, list_of_locations_coords)
    air_trans_vertical_list = get_vertical_air_trans(G, list_of_locations, date)
    # resource_list = [(1,1,1), (5,5,5), (10,10,10)]
    resource_list = [(2,2,2)]

    # print(alt_arr)
    for resource in resource_list:
        print(resource)
        T, R, L = resource
        total_rate_arr_primary_discrete = []
        total_rate_arr_primary_fair_discrete = []
        total_rate_arr_primary_continuous = []
        total_rate_arr_primary_fair_continuous = []
        mmf_primary_discrete = []
        mmf_primary_fair_discrete = []
        mmf_primary_continuous = []
        mmf_primary_fair_continuous = []
        for alt in alt_arr:
            S=generate_network(no_of_rings,no_of_sats_in_each_ring,earth_rad,alt)
            sat_axis_list, sat_loc_list = pre_process_sat(S, no_of_rings*no_of_sats_in_each_ring)

            no_of_gs_pairs = len(G_pair_labels)
            g1_label, g2_label = G_pair_labels[0]
            
            In_range_pair, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, In_range_pair_reflection, In_range_sats_reflection, In_range_gs_pairs_reflection, In_range_pair_fidelity_reflection = evolve_network(sat_axis_list, sat_loc_list,G,G_pair_labels,t,alt,earth_omega,thetae, arch_type, algo_type, no_of_sats, time_diff, air_trans_vertical_list)
            print(In_range_pair)

            sol_pd, mmf_pd, sol_arr_pd = solve_primary(no_of_sats, no_of_gs_pairs, no_of_gs, T, R, L, gs_to_pair_mapping, In_range_pair, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, 1)
            # sol_pc, mmf_pc,sol_arr_pc = solve_primary(no_of_sats, no_of_gs_pairs, no_of_gs, T, R, L, gs_to_pair_mapping, In_range_pair, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, 0)
            sol_pfd, mmf_pfd, sol_arr_pfd = solve_primary_fair(no_of_sats, no_of_gs_pairs, no_of_gs, T, R, L, gs_to_pair_mapping, In_range_pair, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, 1)
            # sol_pfc, mmf_pfc,sol_arr_pfc = solve_primary_fair(no_of_sats, no_of_gs_pairs, no_of_gs, T, R, L, gs_to_pair_mapping, In_range_pair, In_range_sats, In_range_gs_pairs, In_range_pair_fidelity, 0)
            visualize_pairs_sats(In_range_sats, In_range_pair, sol_arr_pd,sol_arr_pfd, no_of_gs_pairs)
            plot_rates_for_pairs(In_range_pair, In_range_sats,no_of_gs_pairs, sol_arr_pd,sol_arr_pfd)
            # sol_pg, sol_arr_pg = solve_primary_greedy(T, R, L, G_pair_labels, In_range_pair, no_of_sats, no_of_gs,no_of_gs_pairs)
            # print(sol_arr_pf)
            # total_rate_arr_primary_discrete.append(sol_pd)
            # total_rate_arr_primary_fair_discrete.append(sol_pfd)
            # total_rate_arr_primary_continuous.append(sol_pc)z
            # total_rate_arr_primary_fair_continuous.append(sol_pfc)

            # mmf_primary_discrete.append(mmf_pd)
            # mmf_primary_fair_discrete.append(mmf_pfd)
            # mmf_primary_continuous.append(mmf_pc)
            # mmf_primary_fair_continuous.append(mmf_pfc)
        # print('mmf for continuous (aggregate)')
        # print(mmf_primary_continuous)
        # print('mmf for continuous (fair)')
        # print(mmf_primary_fair_continuous)
        # plot_alt_perf((np.array(alt_arr))/1000, total_rate_arr_primary_discrete, total_rate_arr_primary_fair_discrete, total_rate_arr_primary_continuous,total_rate_arr_primary_fair_continuous,mmf_primary_discrete, mmf_primary_fair_discrete, mmf_primary_continuous,mmf_primary_fair_continuous, T, R, L)