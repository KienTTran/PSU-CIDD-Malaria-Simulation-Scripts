# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 03:58:19 2022

@author: nguyentd
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import seaborn as sns

exp_number = 12
number = 0

local_path = "D:\\plot\\PRMC_2_Genotypes_Exp_" + str(exp_number) + "\\"
local_path_raw = local_path + "\\raw"
local_path_bin = local_path + "\\bin"

# monthly_data = pd.read_csv('monthly_data_0.txt', sep='\t', header=None);

genotype_data = pd.read_csv(local_path_raw + '\\gene_db_' + str(number) +'.txt', sep='\t', header=None,index_col=None);
genotype_data.columns = ["id","aa_sequence"]

genotype_names = genotype_data.aa_sequence
genotype_names = pd.concat([genotype_names, pd.Series(["temp"])], ignore_index=True)

gene_freq_data = pd.read_csv(local_path_raw + '\\gene_freq_' + str(number) +'.txt', sep='\t', header=None, names = genotype_names,index_col=None,);

#%%
figure(figsize=(8, 4.5), dpi=150)

n_years = 30

my_colors = sns.color_palette("husl",len(genotype_data))

for col_i, col in enumerate(gene_freq_data.columns):
    if col!='temp':
        plt.plot(gene_freq_data.index, gene_freq_data[col], label=col, color= my_colors[col_i])

plt.xlabel('Years')
plt.ylabel('Freqency')
plt.xticks(range(0,n_years*12+1,12*5), range(0,n_years+1,5))
plt.legend(title="genotypes", ncol=1, loc='center left')

