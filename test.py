#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 17:06:48 2024

@author: nitish
"""

arr1 = {1:[1,2,3]}
arr2 = arr1.copy()
arr1[1].remove(2)
print(arr2)