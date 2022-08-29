# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 16:50:51 2022

@author: kient
"""

import os
import re
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

exp_number = 'Calibrate_beta'

local_path = "D:\\plot\\Validation\\" + str(exp_number) + "\\"
local_path_raw = local_path + "\\output"
local_path_input = local_path + "\\input"

config_df = pd.read_csv(os.path.join(local_path_input,'inputs.csv'),index_col=False)
config_df.set_index('Index', inplace=True)

tm,kappa = {0.0, 0.1}
# tm,kappa = {0.5, 0.1}
z = 5.2

#%%
n_run = 1
data = []
for index,config in config_df.iterrows():
    # print(index,config)
    for run in range(n_run):
        # print(run)
        if config.treatment == tm and config.kappa == kappa and config.z == z:
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
                #clinical episode per person per year
                # row = csv_monthly.iloc[-13:-1,[*range(140,200)]].div(csv_monthly.iloc[-13:-1,[*range(79,139)]].values,axis=0).div(12,axis=0).sum()
                row = csv_monthly.iloc[-1:,[*range(140,200)]].div(csv_monthly.iloc[-1:,[*range(79,139)]].values,axis=0).div(12,axis=0).sum()
                # row = csv_monthly.iloc[-1:,[*range(140,200)]].div(csv_monthly.iloc[-1:,[*range(79,139)]].values,axis=0).sum()
                r_monthly = row.to_list()
                r_monthly.append((float)(kappa))
                r_monthly.append((float)(z))
                r_monthly.append((float)(beta))
            except Exception as e:
                print(csv_summary + " error reading " + str(e))
            
            data.append(r_summary + r_monthly) 
        
data_plot = pd.DataFrame(data)
data_plot.columns = ["eir","pfpr",*[str(x+1) for x in range(60)],"kappa","z","beta"]
#%%
data_plot.to_csv(local_path + str(exp_number) + '_S5-6_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + ".csv",index=False)  
#%%
data_plot = pd.read_csv(local_path + str(exp_number) + '_S5-6_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + ".csv")
#%%

pfpr_index_to_plot = [
                        2,
                        4,
                        6,
                        8,
                        11,
                        13,
                        15,
                        16,
                        18
                        ]

data_reduced = []
for index,row in data_plot.iterrows():
    if index in pfpr_index_to_plot:
        data_reduced.append(row)
        
data_plot_reduced = pd.DataFrame(data_reduced)
age_class = data_plot_reduced.columns[2:62]

# id_vars=['beta', 'z', 'kappa', 'eir','pfpr'], var_name=[*age_class], value_name='freq'
data_plot_reduced_melt = data_plot_reduced.melt(id_vars=['beta', 'z', 'kappa', 'eir','pfpr'],var_name='age_class', value_name='value')

#%%
# plot = sns.relplot(data=data_plot_reduced_melt,
#                 x='age_class',
#                 y='value',
#                 col='eir',
#                 col_wrap=3,
#                 facet_kws=dict(sharey=False))
plot = sns.catplot(data=data_plot_reduced_melt,
                x='age_class',
                y='value',
                col='eir',
                col_wrap=3,
                kind='box',
                sharey=False)
plot.set(xscale="log")

plot.set(xlim=(0,60))
# plot.set_yticks(range(0,100,10))
plot.set(xlabel='Age Class')
plot.set(ylabel='Clinical episode per person per year')
# plot.set(xlim=(0, 10))

plot.figure.savefig(local_path + str(exp_number) + '_S5-6_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + '.png', dpi=300)