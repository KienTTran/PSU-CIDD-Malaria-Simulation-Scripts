# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 14:26:57 2021

@author: ktt5121
"""
import os

def read_simulations(localpath,plot_keywords,delay):
    #Read folders
    rep_files = []  
    for root, folders, files in os.walk(localpath, topdown=False):
        for file in files:
            if file.endswith(".txt") and all(x in file for x in plot_keywords):
                rep_files.append(os.path.join(root, file))
    print(rep_files)            
    return rep_files