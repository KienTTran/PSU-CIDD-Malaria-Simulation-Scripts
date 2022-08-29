# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 21:30:30 2022

@author: kient
"""

import os
import re
import pandas as pd
import numpy as np
import math

exp_number = 'Calibrate_beta'

local_path = "D:\\plot\\Validation\\" + str(exp_number) + "\\"
local_path_raw = local_path + "\\output"
local_path_input = local_path + "\\input"

config_df = pd.read_csv(os.path.join(local_path_input,'inputs.csv'),index_col=False)
config_df.set_index('Index', inplace=True)


#%%

n_run = 1
data = []
for index,config in config_df.iterrows():
    for run in range(n_run):
        # print(run)
        filename_summary = "validation_summary_%d.txt"%(index*1000 + run)
        filename_monthly = "validation_monthly_data_%d.txt"%(index*1000 + run)
        # print(filename)        
        kappa = config.kappa
        z = config.z
        beta = config.beta
        # print(beta,ifr)        
        file_path_summary = os.path.join(local_path_raw, filename_summary)
        file_path_monthly = os.path.join(local_path_raw, filename_monthly)
        try:
            csv_summary = pd.read_csv(file_path_summary,sep='\t',header=None,index_col=None)  
            row = csv_summary.iloc[0,[4,6]]
            r_summary = row.to_list()
        except Exception as e:
            print(csv_summary + " error reading " + str(e))
        try:
            csv_monthly = pd.read_csv(file_path_monthly,sep='\t',header=None,index_col=None)
            row = csv_monthly.iloc[-13:-1,[*range(139,199)]].div(csv_monthly.iloc[-13:-1,[*range(79,139)]].values,axis=0).sum()
            r_monthly = row.to_list()
            r_monthly.append((float)(kappa))
            r_monthly.append((float)(z))
            r_monthly.append((float)(beta))
        except Exception as e:
            print(csv_summary + " error reading " + str(e))
        
        data.append(r_summary + r_monthly) 
        
data_plot = pd.DataFrame(data)
data_plot.columns = ["eir","pfpr",*["age"+str(x) for x in range(60)],"kappa","z","beta"]

data_plot["eir_log10"] = data_plot.eir.apply(lambda x: 0 if x == 0 else math.log10(x))
#%%
data_plot.to_csv(local_path + str(exp_number) + ".csv",index=False)