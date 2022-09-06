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

local_path = "D:\\plot\\Validation\\" + str(exp_number) + "\\Others" +  "\\"
local_path_raw = local_path + "\\output"
local_path_input = local_path + "\\input"

config_df = pd.read_csv(os.path.join(local_path_input,'inputs.csv'),index_col=False)
config_df.set_index('Index', inplace=True)

# tm,kappa,z,gamma_sd = (0.0, 0.2, 4.6,10)
tm,kappa,z,gamma_sd = (0.5, 0.3, 5.4,10)

#%%
n_run = 100
data = []
for index,config in config_df.iterrows():
    # print(index,config)
    for run in range(n_run):
        # print(run)
        if float(config.treatment) == float(tm) and float(config.kappa) == float(kappa) \
        and float(config.z) == float(z) and float(config.gamma_sd) == float(gamma_sd):
            filename_summary = "validation_summary_%d.txt"%(index*1000 + run)
            filename_monthly = "validation_monthly_data_%d.txt"%(index*1000 + run)
            kappa = config.kappa
            z = config.z
            beta = config.beta
            # print(beta,ifr)        
            file_path_summary = os.path.join(local_path_raw, filename_summary)
            file_path_monthly = os.path.join(local_path_raw, filename_monthly)
            try:
                csv_summary = pd.read_csv(file_path_summary,sep='\t',header=None,index_col=None)  
                row = csv_summary.iloc[0,[4,6,*range(19,79)]]
                r_summary = row.to_list()
                r_summary.append((float)(kappa))
                r_summary.append((float)(z))
                r_summary.append((float)(beta))
            except Exception as e:
                print(csv_summary + " error reading " + str(e))
            # try:
            #     csv_monthly = pd.read_csv(file_path_monthly,sep='\t',header=None,index_col=None)
            #     #clinical episode per person per year
            #     # row = csv_monthly.iloc[-13:-1,[*range(140,200)]].div(csv_monthly.iloc[-13:-1,[*range(79,139)]].values,axis=0).sum()
            #     row = csv_summary.iloc[0,[17,77]]
            #     # row = csv_monthly.iloc[-1:,[*range(140,200)]].sum()
            #     r_monthly = row.to_list()
            #     r_monthly.append((float)(kappa))
            #     r_monthly.append((float)(z))
            #     r_monthly.append((float)(beta))
            # except Exception as e:
            #     print(csv_monthly + " error reading " + str(e))
            
            data.append(r_summary) 
            # data.append(r_summary + r_monthly) 
        
data_plot = pd.DataFrame(data)
data_plot.columns = ["eir","pfpr",*[str(x+1) for x in range(60)],"kappa","z","beta"]
#%%
data_plot.to_csv(local_path + str(exp_number) + '_S5-6_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + ".csv",index=False)  
#%%
data_plot = pd.read_csv(local_path + str(exp_number) + '_S5-6_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + ".csv")

#%%
betas = data_plot.beta.unique()

ages = [1,2,3,4,5,6,7,8,9,10,11,17,40,60]

fig, axes = plt.subplots(4,5,sharex=True,sharey=False, squeeze=True)
for index,beta in enumerate(betas):
    r = index // 5
    c = index % 5
    data_beta = data_plot[((data_plot.beta == beta))]
    data_clinical = data_beta[[str(x) for x in ages]]
    data_clinical.columns=[*ages]
    data_clinical_melt = pd.melt(data_clinical)
    data_clinical_melt.columns = ["age","#cli.ep./person/year"]
    sns.boxplot(data=data_clinical_melt,x="age",y="#cli.ep./person/year",ax=axes[r,c],
                showfliers=False)
    eir_percentile = np.percentile(data_beta["eir"],[25,50,75])
    pfpr_percentile = np.percentile(data_beta["pfpr"],[25,50,75])    
    if r < 5:
        axes[r,c].set_xlabel("")
    if c > 0:
        axes[r,c].set_ylabel("")    
    axes[r,c].set_title("EIR: %.2f - PFPR: %.2f"%(eir_percentile[1],pfpr_percentile[1]))   
figure = plt.gcf() # get current figure
figure.set_size_inches(18, 12)
plt.savefig(local_path + str(exp_number) + '_S5-6_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + '.png', dpi=300)