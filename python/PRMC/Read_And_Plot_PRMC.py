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

local_path = "D:\\plot\\PRMC_2_Genotypes_Exp_9\\raw"

config_df = pd.read_csv(local_path + '\configs.csv',index_col=False)
config_df.set_index('Index', inplace=True)

n_run = 10

data = []

for index,config in config_df.iterrows(): 
    for run in range(n_run):
        # print(run)
        filename_db = "gene_db_%d.txt"%(index*1000 + run)
        filename_freq = "gene_freq_%d.txt"%(index*1000 + run)
        print(filename_db) 
        beta = config.beta 
        prmc_size = config.prmc_size      
        ifr = config.ifr
        # print(beta,ifr)        
        file_path_db = os.path.join(local_path, filename_db)
        file_path_freq = os.path.join(local_path, filename_freq)
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
            csv_freq['ld'] = csv_freq[csv_db.aa_sequence[0]]*csv_freq[csv_db.aa_sequence[1]]
            
            if len(csv_db.aa_sequence) == 4:
                csv_freq['ld'] = csv_freq['ld'] - csv_freq[csv_db.aa_sequence[2]]*csv_freq[csv_db.aa_sequence[3]]
            
            data.append(csv_freq)            
        except Exception as e:
            raise
            print(file_path_freq + " error reading " + str(e))
        
data_plot = pd.concat(data,ignore_index=True, axis = 0)
#%%

import seaborn as sns

sns.relplot(data = data_plot, 
            x = 'month',
            y = 'ld',
            col = 'prmc_size',
            row = 'beta',
            hue = 'ifr',
            style = "ifr",
            kind = "line",
            ci = 'sd'
            )



            
