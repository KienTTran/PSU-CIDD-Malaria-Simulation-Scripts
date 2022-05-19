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

exp_number = 10

local_path = "D:\\plot\\PRMC_2_Genotypes_Exp_" + str(exp_number) + "\\"
local_path_raw = local_path + "\\raw"
local_path_bin = local_path + "\\bin"

config_df = pd.read_csv(local_path_bin + '\\configs.csv',index_col=False)
config_df.set_index('Index', inplace=True)

n_run = 10

data = []

for index,config in config_df.iterrows(): 
    for run in range(n_run):
        # print(run)
        filename_db = "gene_db_%d.txt"%(index*1000 + run)
        filename_freq = "gene_freq_%d.txt"%(index*1000 + run)
        # print(filename_db) 
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
            csv_freq['year'] = (csv_freq['month'] / 12).round()
            csv_freq['beta'] = [beta]*len(csv_freq)
            csv_freq['prmc_size'] = [prmc_size]*len(csv_freq)
            csv_freq['ifr'] = [ifr]*len(csv_freq)
            # csv_freq['ld'] = csv_freq[csv_db.aa_sequence[0]]*csv_freq[csv_db.aa_sequence[1]]
            
            # if len(csv_db.aa_sequence) == 4:
                # csv_freq['ld'] = csv_freq['ld'] - csv_freq[csv_db.aa_sequence[2]]*csv_freq[csv_db.aa_sequence[3]]
            
            data.append(csv_freq)            
        except Exception as e:
            raise
            print(file_path_freq + " error reading " + str(e))
        
data_plot = pd.concat(data,ignore_index=True, axis = 0)
#%%

data_plot.to_csv(local_path + "data_plot_exp_" + str(exp_number) + ".csv",index=False)
#%%

import os
import re
import pandas as pd
import numpy as np
import math
import seaborn as sns

data_plot = pd.read_csv(local_path + "data_plot_exp_" + str(exp_number) + ".csv")

plot = sns.relplot(data = data_plot, 
            x = 'year',
            y = data_plot.columns[11],
            col = 'ifr',
            row = 'beta',
            # hue = 'ifr',
            # style = "ifr",
            kind = "line",
            ci = 'sd',
            palette=sns.color_palette("husl",7)[:6]
            )


#%%
plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + ".png", dpi=300)


            
