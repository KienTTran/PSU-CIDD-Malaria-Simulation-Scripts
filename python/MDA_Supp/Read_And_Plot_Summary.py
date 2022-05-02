# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 21:02:18 2022

@author: kient
"""
import os
import re
import pandas as pd
import numpy as np
import math

local_path = "D:\\plot\\MDA_Supp_S3_S10_Exp_3\\raw"

config_df = pd.read_csv('configs.csv',index_col=False)
config_df.set_index('Index', inplace=True)

n_run = 1

data = []

for index,config in config_df.iterrows(): 
    for run in range(n_run):
        # print(run)
        filename = "summary_%d.txt"%(index)
        # print(filename)        
        kappa = config.kappa
        z = config.z
        beta = config.beta
        # print(beta,ifr)        
        file_path = os.path.join(local_path, filename)
        try:
            csv = pd.read_csv(file_path,sep='\t',header=None,index_col=None)
            row = csv.iloc[0,[4,6] + [*range(13,73)]]            
            r = row.to_list()
            r.append((float)(kappa))
            r.append((float)(z))
            r.append((float)(beta))
            data.append(r)        
        except Exception as e:
            print(filename + " error reading " + str(e))
            
data_plot = pd.DataFrame(data)
data_plot.columns = ["eir","pfpr",*["age"+str(x) for x in range(60)],"kappa","z","beta"]  
data_plot.to_csv("data.csv",index=False)

#%%
import seaborn as sns
from matplotlib import pyplot as plt
import math
   
fig, axes = plt.subplots(2,5,sharex=True,sharey=True, squeeze=True)
for index,kappa in enumerate(data_plot.kappa.unique()):
    data_plot_by_kappa = data_plot[data_plot.kappa == kappa]
    data_plot_by_kappa["2to10"] = data_plot_by_kappa.age2/data_plot_by_kappa.age10
    r = index//5
    c = index % 5
    sns.scatterplot(data=data_plot_by_kappa ,x="eir",y="2to10",hue="z", palette=sns.color_palette("husl",9)[:4], ax=axes[r,c])
        
    if r < 5:
        axes[r,c].set_xlabel("")
    if c > 0:
        axes[r,c].set_ylabel("")
        
    axes[r,c].set_title("Kappa: %.2f"%(kappa))
    axes[r,c].set_xscale('log')
    # axes[r,c].set_xlim([0, 200])
    
    