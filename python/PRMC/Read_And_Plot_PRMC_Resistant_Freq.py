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
import matplotlib.pyplot as plt

a4_dims = (11.7, 8.27)

exp_number = 11

local_path = "D:\\plot\\PRMC_2_Genotypes_Exp_" + str(exp_number) + "\\"
local_path_raw = local_path + "\\raw"
local_path_bin = local_path + "\\bin"

config_df = pd.read_csv(local_path_bin + '\\configs.csv',index_col=False)
config_df.set_index('Index', inplace=True)

#%%
n_run = 1

data = []

for index,config in config_df.iterrows(): 
    for run in range(n_run):
        # print(run)
        filename_db = "gene_db_%d.txt"%(index*1000 + run)
        filename_freq = "gene_freq_%d.txt"%(index*1000 + run)
        # print(filename) 
        beta = config.beta 
        prmc_size = config.prmc_size      
        ifr = config.ifr
        # print(beta,ifr)        
        file_path_db = os.path.join(local_path_raw, filename_db)
        file_path_freq = os.path.join(local_path_raw, filename_freq)
        try:
            csv_db = pd.read_csv(file_path_db, sep='\t', header=None,index_col=None)
            csv_db.columns = ["id","aa_sequence"]   
            genotype_names = csv_db.aa_sequence
            genotype_names = pd.concat([genotype_names, pd.Series(["temp"])], ignore_index=True)
            csv_freq = pd.read_csv(file_path_freq, sep='\t', header=None, names = genotype_names, index_col=None)
            csv_freq = csv_freq.fillna(0)
            csv_freq = csv_freq.drop(['temp'], axis=1)
            csv_freq['month'] = csv_freq.index
            csv_freq['beta'] = [beta]*len(csv_freq)
            csv_freq['prmc_size'] = [prmc_size]*len(csv_freq)
            csv_freq['ifr'] = [ifr]*len(csv_freq)
            csv_freq['ld'] = csv_freq[csv_db.aa_sequence[0]]*csv_freq[csv_db.aa_sequence[1]] - csv_freq[csv_db.aa_sequence[2]]*csv_freq[csv_db.aa_sequence[3]]
            data.append(csv_freq)            
        except Exception as e:
            print(" error reading " + str(e))
        
data_plot = pd.concat(data,ignore_index=True, axis = 0)

#%%
data_plot.to_csv(local_path + "data_plot_res_freq" + str(exp_number) + ".csv",index=False)  

#%%
data_plot = pd.read_csv(local_path + "data_plot_res_freq" + str(exp_number) + ".csv") 

#%%

data_genotypes = data_plot.columns[0:8]

data_plot_melt = data_plot.melt(id_vars=['beta', 'prmc_size', 'ifr','month', 'ld'], var_name='cols', value_name='vals')

#%%
plot = sns.relplot(data = data_plot_melt, 
            x = 'month',
            y = 'vals',
            hue = 'cols',
            col = 'ifr',
            row = 'beta',
            kind = "line",
            ci = "sd",
            palette=sns.color_palette("husl",9)[:len(data_genotypes)],
            height = a4_dims[1], aspect = 1.5
            )

plot.axhline(0.1, ls='--', linewidth=2, color='red')
plot.set(xlim=(40, 72))
plot.set(ylim=(0, 0.2))
plot.set(xticks=range(40,72,4))
plot.set(yticks=np.arange(0,0.2,0.025))
plot.set_xlabels('Months')
plot.set_ylabels('Freq.')
plot.map(plt.axhline, y=0.1, ls='--', linewidth=2, color='red')


plot.fig.subplots_adjust(bottom=0.1);        
plot._legend.remove()
plot.fig.legend(data_genotypes, ncol = 4, loc='lower center', 
                bbox_to_anchor=(0.0, 0.0, 1.0, 0.1), frameon=False)
plt.subplots_adjust(hspace = 0.2, wspace = 0.1) 

#%%
plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_res_freq.png", dpi=600)
            
