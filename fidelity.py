#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 21:08:15 2024

@author: nitish
"""
import numpy as np
from arch_types.compute_fidelity_rate_new import fid_dd, psucc_dd
import matplotlib.pyplot as plt

def plot_fidelity():
    NsS = 0.01
    transA = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
    transB = transA
    y = []
    Pd = 10**(-2)
    for transA_comp in transA:
        y.append(fid_dd(NsS,transA_comp,transA_comp, Pd))
    plt.plot(transA, y)
    plt.savefig('fidelity')
    plt.show()
    
if __name__ == "__main__":
    plot_fidelity()