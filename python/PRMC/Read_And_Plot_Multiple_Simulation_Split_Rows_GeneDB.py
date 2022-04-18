# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 22:35:31 2022

@author: kient
"""

from Read_Simulations import read_simulations
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import operator
import math

plot_keywords = [
            "gene"
            ]
start_year = 2000
end_year = 2040
display = "Month"
year_interval = 1
month_interval = 12
day_interval = 90

# local_path = "D:/plot/Simulations/"
# local_path = "D:/plot/parasite_id/10K/"
# local_path = "D:/plot/parasite_id/100K/"
# local_path = "D:/plot/parasite_id/new/"
# local_path = "D:/plot/all/parasite_id/"
# local_path = "D:/plot/all/Nguyen/"
# local_path = "D:/plot/4000/"
# local_path = "D:/plot/new/"
# local_path = "D:/plot/new/250K_500K_1M/"
# local_path = "D:/plot/new/1M/"
# local_path = "D:/plot/new/1M/Parasite"
# local_path = "D:/plot/new/1M/PRMC"
# local_path = "D:/plot/new/Test/Normal"
# local_path = "D:/plot/new/Test/PRMC"
# local_path = "D:/plot/new/1M/Test1/"
# local_path = "D:/plot/new/1M/4-Genotypes/PRMC"
# local_path = "D:/plot/new/1M/4-Genotypes/Parasite"
# local_path = "D:/plot/new/1M/4-Genotypes/Parasite"
# local_path = "D:/plot/PRMC_2_Genotypes_Exp_2/raw"
local_path = "D:/plot/Test1/"
plot_delay = 2

#Plot vars
plot_lines = []
plot_labels = []
ops = { 
        "+": operator.add, 
        "-": operator.sub,
        "x": operator.mul,
        "/": operator.truediv
        }
def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

def plot_headers(title, data_mean, data_min, data_max, \
                    rep_cols_observe, col_index, row_index, \
                    rep_header_observe, rep_x_observe, axes, \
                    index, confident_interval):
    if index == 0:
        for header in rep_header_observe:
            sns.lineplot(data = data_mean, 
                        x = rep_x_observe,
                        y = header,
                        ax = axes[index],
                        ci = confident_interval,
                        linewidth = 1.0,
                        # linestyle="dashed"
                        # err_style='bars'
                        )
        axes[index].set_title("Allele Frequency",fontsize=12)
        # axes[index].axhline(y=0.5, color='grey', linestyle='--', linewidth = 2.0, alpha = 0.4)
        axes[index].legend(loc='lower right', labels=[headers for headers in rep_header_observe], ncol = 2)
    elif index == 1:
        for header in rep_header_observe:
            sns.lineplot(data = data_mean, 
                        x = rep_x_observe,
                        y = header,
                        ax = axes[index],
                        ci = confident_interval,
                        linewidth = 1.0,
                        # err_style='bars'
                        )
        axes[index].set_title("Genotype Frequency",fontsize=12)
        # axes[index].axhline(y=0.25, color='grey', linestyle='--', linewidth = 2.0, alpha = 0.4)
        axes[index].legend(loc='lower right', labels=[headers for headers in rep_header_observe], ncol = 2)
    else:
        for header in rep_header_observe:
            sns.lineplot(data = data_mean, 
                        x = rep_x_observe,
                        y = header,
                        ax = axes[index],
                        ci = confident_interval,
                        linewidth = 1.0,
                        # err_style='bars'
                        )
        axes[index].set_title("Linkage Disequilibrium",fontsize=12)
        axes[index].tick_params(which="both", bottom=True)
        axes[index].legend(loc='center', labels=[headers for headers in rep_header_observe], ncol = 2)
        axes[index].set_xlabel(None)
    axes[index].set_ylabel(None) 
    
print("Reading simulations")   
simulations = read_simulations(local_path, plot_keywords, plot_delay)
if simulations == []:
    print("No simulation available")
else:
    print("Ploting simulations")
    
rep_data_gene_freq_csv = []
rep_data_monthly_csv = []
rep_data_summary_csv = []
rep_file_db = []
rep_file_freq = []
rep_file_monthly = []
rep_file_summary = []
for rep_file in simulations:
    rep_tag = ""  
    rep_tags = []
    print(rep_file)
    for split_items_1 in rep_file.split("/"):
        if "\\" in split_items_1:
            rep_tags = split_items_1.split("\\")
            print(rep_tags)
            if len(rep_tags) > 3:
                rep_tag = rep_tags[-3]
            else:
                rep_tag = rep_tags[-1]
        else:
            rep_tags = rep_file.split("/")
            rep_tag = rep_tags[-1]
    
    rep_tag_data = rep_tag.split("_")
    print(rep_tag_data)   

    if "_db_" in rep_file:     
        rep_file_db.append(rep_file)
    if "_freq_" in rep_file:
        rep_file_freq.append(rep_file)

for file_db,file_freq in zip(rep_file_db,rep_file_freq):
    try:
        rep_data_gene_db = pd.read_csv(file_db, sep='\t', header=None,index_col=None)
        rep_data_gene_db.columns = ["id","aa_sequence"]   
        rep_data_gene_freq = pd.read_csv(file_freq, sep='\t', header=None, skiprows=1)
        rep_data_gene_freq.dropna(how='all', axis=1, inplace=True)
        rep_data_gene_freq.fillna(0)
        rep_data_gene_freq.columns = rep_data_gene_db["aa_sequence"]
        rep_data_gene_freq_csv.append(rep_data_gene_freq)
        # rep_data_monthly = pd.read_csv(file_monthly, sep='\t', header=None,index_col=None)
        # rep_data_monthly = rep_data_monthly.iloc[:,[10]]
        # rep_data_monthly.columns = ["EIR","PFPR1"]
        # rep_data_monthly_csv.append(rep_data_monthly)
        # rep_data_gene_freq_csv.append(pd.concat([rep_data_gene_freq, rep_data_monthly], axis=1))
    except pd.errors.EmptyDataError:
        print('Empty csv file!')
        continue 
       

for csv in rep_data_gene_freq_csv:
    rep_data_raw = []
    rep_data_observe = []
    rep_data_mean_observe = []
    rep_headers = []  
    rep_header_legend = []
    rep_data_range = [start_year, end_year]
    rep_total_location = 1   
    
    rep_data_raw.append(csv)
        
    for data in rep_data_raw:
        rep_data_observe.append(data)
    
    genotypes = int(math.sqrt(len(csv.columns)))
    index_pop_gen_start = 1
    index_pop_gen_end = pow(genotypes,2) + 1
    
    if genotypes == 2:
        all_alleles = [["K","T"],["Y","C"]]
        introduced_genotypes = ["KC","TY"]
        all_allele_pos = [9,31]
    if genotypes == 4:
        all_alleles = [["K","T"],["Y","F"],["1","2"],["x","X"]]
        introduced_genotypes = ["KY1x","TY1x","KF2X","TF2X"]
        all_allele_pos = [9,5,33,15]
    for data in rep_data_observe:     
        data.insert(0,"Month",data.index)
        # Calculate Allele freq     
        for allele_pair in all_alleles:
            for allele in allele_pair:
                data["Allele " + allele] = 0;
        for column in data.columns[index_pop_gen_start:index_pop_gen_end]:
            for index,pos in enumerate(all_allele_pos):
                if column[pos] in all_alleles[index]:
                    data["Allele " + column[pos]] += data[column]
        # Calculate LD
        genotype_ld = []
        for column in data.columns[index_pop_gen_start:index_pop_gen_end]:
            genotype_str = ""
            for pos in all_allele_pos:
                genotype_str += column[pos]
            if genotype_str in introduced_genotypes:
                genotype_ld.append(column)
        for index,genotype in enumerate(genotype_ld):
            data["temp"] = data["Allele " + introduced_genotypes[index][0]]
            for index2 in range(1,len(introduced_genotypes[index])):
                data["temp"] *= data["Allele " + introduced_genotypes[index][index2]]
            data[introduced_genotypes[index]] = data[genotype] - data["temp"]
        del data["temp"]
        
    rep_headers = rep_data_observe[0].columns
    
    rep_data_concat = [rep_data for rep_data in rep_data_observe]             
    rep_data_mean_observe = pd.concat(rep_data_concat).mean(level=0)            
    rep_data_min_observe = pd.concat(rep_data_concat).min(level=0)          
    rep_data_max_observe = pd.concat(rep_data_concat).max(level=0)         
    rep_data_quantile_observe = pd.concat(rep_data_concat).quantile(axis=0)
       
    x_tick_major = []
    x_tick_major_label = []
    y_tick_major = [x * 0.1 for x in range(0, 7)]
       
    for month in range(0,int(rep_data_mean_observe.Month.tail(1))):
        if month % 24 == 0:
            x_tick_major.append(month)
            x_tick_major_label.append(start_year + int(month/12))
       
    #None/sd
    confident_interval = None
    rep_header_observe = []
    rep_header_observe.append(rep_headers[index_pop_gen_end:(index_pop_gen_end + genotypes*2)]) #index 0 - Allele frequency
    rep_header_observe.append(rep_headers[index_pop_gen_start:index_pop_gen_end]) #index 1 - Genotype frequency
    rep_header_observe.append(rep_headers[(index_pop_gen_end + genotypes*2):(index_pop_gen_end + genotypes*2 + 5)]) #index 2 - LD
       
    rep_header_legend = []
       
    for index in range(0,int((len(rep_header_observe))/rep_total_location)):
        rep_header_legend.append(rep_header_observe[index][2:])
       
    rep_rows_observe = 3
    rep_cols_observe = 1
       
    fig, axes = plt.subplots(nrows=rep_rows_observe, 
                              ncols=rep_cols_observe,
                              sharex="col", sharey=False, 
                              figsize = (300,100),
                              gridspec_kw={'height_ratios': [1,3,1]})
    fig.subplots_adjust(top = 0.94, bottom = 0.06, right = 0.95, left = 0.05, 
                        hspace=0.2, wspace = 0.2)
    sns.set_style("darkgrid")
          
    #Ploting
    for col_index in range(0,rep_cols_observe):
        for row_index in range(0,rep_rows_observe):
            index = col_index + row_index * rep_cols_observe
            plot_headers(rep_tag, rep_data_mean_observe, rep_data_min_observe, rep_data_max_observe, \
                          rep_cols_observe, col_index, row_index, \
                          rep_header_observe[index], display, axes, \
                          index, confident_interval)
               
    plt.minorticks_on()
    plt.xticks(x_tick_major,x_tick_major_label)
    # plt.yticks(y_tick_major)
    plt.pause(plot_delay)
