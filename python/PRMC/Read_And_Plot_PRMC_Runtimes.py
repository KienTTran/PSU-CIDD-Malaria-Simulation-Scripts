# -*- coding: utf-8 -*-
"""
Created on Tue May  3 11:07:17 2022

@author: kient
"""

import os
import re
import pandas as pd
import numpy as np
import math

exp_number = 7

local_path = "D:\\plot\\PRMC_2_Genotypes_Exp_" + str(exp_number) + "\\"
local_path_raw = local_path + "\\raw"
local_path_bin = local_path + "\\bin"

config_df = pd.read_csv(local_path_bin + '\\configs.csv',index_col=False)
config_df.set_index('Index', inplace=True)

runtimes_df = pd.read_csv(local_path + "\\runtimes.csv",sep='\t', header=None,index_col=None)
runtimes_df.columns = ["time","run_index"]

n_run = 10

data = []

for index,config in config_df.iterrows(): 
    for run in range(n_run):
        # print(filename_db) 
        beta = config.beta 
        prmc_size = config.prmc_size      
        ifr = config.ifr
        
        r = runtimes_df[runtimes_df.run_index == index*1000 + run]
        r["beta"] = beta
        r["prmc_size"] = prmc_size
        r["ifr"] = ifr
        
        
        data.append(r)            
        
data_plot = pd.concat(data,ignore_index=True, axis = 0)
#%%

data_plot.to_csv(local_path + "data_plot_runtime_exp_" + str(exp_number) + ".csv",index=False)
#%%

import seaborn as sns

data_plot = pd.read_csv(local_path + "data_plot_runtime_exp_" + str(exp_number) + ".csv")


plot = sns.catplot(data = data_plot, 
            x = 'prmc_size',
            y = 'time',
            row = 'beta',            
            col = 'ifr',
            kind = "box",            
            
            )

#%%
plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + ".png", dpi=300)


            
