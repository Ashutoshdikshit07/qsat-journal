#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 14:18:13 2024

@author: nitish
"""
import matplotlib.pyplot as plt

def plot_rates_for_pairs(primary_ratesum, primary_maxmin, primary_ratesum_frac, primary_maxmin_frac, pair_max,primary_ratesum_greedy,  no_of_gs_pairs):
    fig = plt.figure(figsize =(10, 7))
    plt.plot(range(no_of_gs_pairs), sorted(primary_ratesum), 'rs-', linewidth=1, label='PRIMARY-RATESUM')
    plt.plot(range(no_of_gs_pairs), sorted(primary_maxmin), 'gs-', linewidth=1, label='PRIMARY-MAXMIN') 
    plt.plot(range(no_of_gs_pairs), sorted(primary_ratesum_frac), 'cs-', linewidth=1, label='PRIMARY-RATESUM-FRAC') 
    plt.plot(range(no_of_gs_pairs), sorted(primary_maxmin_frac), 'bs-', linewidth=1, label='PRIMARY-MAXMIN-FRAC')
    plt.plot(range(no_of_gs_pairs), sorted(primary_ratesum_greedy), 'ys-', linewidth=1, label='PRIMARY-RATESUM-GREEDY')
    plt.plot(range(no_of_gs_pairs), sorted(pair_max), 'ms-', linewidth=1, label='PAIR-MAX')

    plt.yscale('log')
    # plt.xscale('log')
    plt.grid('on')
    # plt.xlim([110,140])
    plt.xlabel('Pair id',fontsize=18)
    plt.ylabel('Fraction Rate',fontsize=18)
    plt.legend(prop={'size': 12})
    plt.tight_layout()
    plt.savefig('plots/pair_rate_log_frac.pdf')   
    plt.show()
# def plot_rates_for_pairs_maxmin(rates_iter1, rates_iter2, rates_iter3,  no_of_gs_pairs):
#     fig = plt.figure(figsize =(10, 7))
#     plt.plot(range(no_of_gs_pairs), sorted(rates_iter1), 'rs-', linewidth=1, label='1 iteration')
#     plt.plot(range(no_of_gs_pairs), sorted(rates_iter2), 'gs-', linewidth=1, label='2 iterations') 
#     plt.plot(range(no_of_gs_pairs), sorted(rates_iter3), 'bs-', linewidth=1, label='3 iterations') 

#     plt.yscale('log')
#     # plt.xscale('log')
#     plt.grid('on')
#     # plt.xlim([110,140])
#     plt.xlabel('Pair id',fontsize=18)
#     plt.ylabel('Rate',fontsize=18)
#     plt.legend(prop={'size': 12})
#     plt.tight_layout()
#     plt.savefig('plots/pair_rate_maxmin_iters_updated2.pdf')   
#     plt.show()

def plot_rates_for_pairs_maxmin(rates_iter1,no_of_gs_pairs):
    fig = plt.figure(figsize =(10, 7))
    plt.plot(range(no_of_gs_pairs), sorted(rates_iter1), 'rs-', linewidth=1, label='1 iteration')
    
    plt.yscale('log')
    # plt.xscale('log')
    plt.grid('on')
    # plt.xlim([110,140])
    plt.xlabel('Pair id',fontsize=18)
    plt.ylabel('Rate',fontsize=18)
    plt.legend(prop={'size': 12})
    plt.tight_layout()
    plt.savefig('plots/pair_rate_maxmin_iters_updated2.pdf')
    print("showing graph")
    plt.show()
    # plt.savefig('plots/pair_rate_maxmin_iters_updated2.pdf')