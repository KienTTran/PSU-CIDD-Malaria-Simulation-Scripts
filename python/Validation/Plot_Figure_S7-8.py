# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 19:59:13 2022

@author: kient
"""

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

tm,kappa,z,gamma_sd = (0.0, 0.2, 4.6,10)
# tm,kappa,z,gamma_sd = (0.5, 0.3, 5.4,10)

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
                row = csv_monthly.iloc[:-1,[*range(201,216)]].mean()
                r_monthly = row.to_list()
                r_monthly.append((float)(kappa))
                r_monthly.append((float)(z))
                r_monthly.append((float)(beta))
            except Exception as e:
                print(csv_summary + " error reading " + str(e))
            
            data.append(r_summary + r_monthly) 
        
data_plot = pd.DataFrame(data)
data_plot.columns = ["eir","pfpr",*[str(x+1) for x in range(15)],"kappa","z","beta"]
#%%
data_plot.to_csv(local_path + str(exp_number) + '_S7-8_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + ".csv",index=False)  
#%%
data_plot = pd.read_csv(local_path + str(exp_number) + '_S7-8_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + ".csv")
#%%

# id_vars=['beta', 'z', 'kappa', 'eir','pfpr'], var_name=[*age_class], value_name='freq'
data_plot_melt = data_plot.melt(id_vars=['beta', 'z', 'kappa', 'eir','pfpr'],var_name='age_class', value_name='phi')

data_plot_melt = data_plot_melt[data_plot_melt.eir > 1.0]

#%%
fig, axes = plt.subplots(5,3,sharex=True,sharey=True)
age_classes = data_plot_melt.age_class.unique()
for index,beta in enumerate(age_classes):
    r = index // 3
    c = index % 3
    sns.scatterplot(data=data_plot_melt[data_plot_melt.age_class == str(index+1)],
            x='eir',
            y='phi',
            ax=axes[r,c])
    
    if r < 5:
        axes[r,c].set_xlabel("")
    if c > 0:
        axes[r,c].set_ylabel("")    
    axes[r,c].set_xscale('log')
    axes[r,c].set_xlabel('EIR')
    axes[r,c].set_ylabel('\u03C6',rotation=0,fontsize=14)
    # ax.set_ylim(0,2.0)
    axes[r,c].set_yticks(np.arange(0,0.21,0.1))
    axes[r,c].set_title("Age class %d"%(index + 1)) 

figure = plt.gcf() # get current figure
figure.set_size_inches(18, 10)
plt.savefig(local_path + str(exp_number) + '_S7-8_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + '.png', dpi=300)
