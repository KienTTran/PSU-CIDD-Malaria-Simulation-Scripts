# import the regex module
import re
import os 
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
import math
import copy

def read_parameters():
    params = {}
    print("Reading parameters.yml")
    with open(r'parameters.yml') as file:
        documents = yaml.full_load(file)
        for item, doc in documents.items():
            params[item] = doc
    return params
        
if __name__=="__main__":
    config_folder_name = "generated_inputs"
    file_path = str(Path.cwd())
    if "\\" in file_path:
        folder = file_path.split("\\")[-1]  
    else:
        folder = file_path.split("/")[-1]
    config_path = os.path.join(Path.cwd(), config_folder_name)
    if not os.path.exists(config_folder_name):
        os.mkdir(config_path)
    print("Will generate configs to folder: " + config_path)
    params = read_parameters()
    print(params)

    template = (r"cmd.template")   
    all_value_list = []  
    
    #Calculate beta log10
    # start = math.log10(params['beta'][0])
    # stop = math.log10(params['beta'][1])
    # step = (stop - start)/params['beta'][-1]
    # log10_beta = np.arange(start,stop,step)
    # betas = 10**log10_beta
    # params['beta'] = betas
        
    #generate YML
    stream = open('sim_prmc.yml', 'r');
    data = yaml.full_load(stream);
    stream.close();
    
    location_info =  [[0, 0, 0]]
    number_of_locations = len(location_info);
    data['location_db']['location_info'] = location_info;
    data['location_db']['population_size_by_location'] = [params['population'][-1]]
    data['initial_strategy_id'] = params['therapy_id'][-1]    
    data['starting_date'] = str(params['start_year'][-1])+'/1/1';
    data['ending_date'] = str(params['end_year'][-1])+'/1/1';
    data['start_of_comparison_period']= str(params['start_year'][-1])+'/1/1';        
    
    config_df = pd.DataFrame()
    config = []
    for beta in params['beta']:
        for p_size in params['prmc_size']:
            for ifr in params['ifr']:       
                config.append([beta, p_size, ifr])
    
    config_df = pd.DataFrame(config)
    config_df.columns = ['beta','prmc_size','ifr']
    
    config_df.to_csv("configs.csv",index=True,index_label="Index")
    
    df = config_df.reset_index()  # make sure indexes pair with number of rows
    for index, row in df.iterrows():
        new_data = copy.deepcopy(data)
        new_data['location_db']['beta_by_location'] = np.full(number_of_locations, row.beta).tolist()
        new_data['mosquito_config']['interrupted_feeding_rate'] = np.full(number_of_locations, row.ifr).tolist()
        new_data['mosquito_config']['prmc_size'] = (int)(row.prmc_size)
        new_data['events'][4]['info'][0]['rate'] = (float)(row.ifr)
        
        output_filename = config_folder_name + '/%d.yml'%(index)
        output_stream = open(output_filename, 'w');
        yaml.dump(new_data, output_stream); 
        output_stream.close();  
                
    with open(r"submit_all_jobs.template", "r") as old_file:
        with open(r"submit_all_jobs.pbs", "w") as new_file:
            for line in old_file:
                if '#REPLICATES#' in line:
                    new_file.writelines('TO=' + str(len(config_df) - 1) + "\n")
                else:
                    new_file.writelines(line)
        
    # #Write to cmd.sh (for Rob queue job version)
    # for index,key in enumerate(params):
    #     print(index,key,params[key])
    #     if len(all_value_list) == 0:
    #         for value in params[key]:
    #             all_value_list.append(str(value))
    #     else:
    #         temp = []
    #         for line in all_value_list:
    #             for value in params[key]:
    #                 temp.append(line + "#" + str(value))
    #         all_value_list = temp
            
    # for index,line in enumerate(all_value_list):
    #     print(index, line)          
    # line_template = ""
    # line_out = []
    # with open(r"cmd.template", "r") as old_file:
    #     for line in old_file:
    #         line_template = line            
    # line_template = re.sub("#folder#", folder, line_template)
    # with open(r"run_cmd.sh", "w") as new_file:
    #     line_out.append("#!/bin/bash\n")
    #     line_out.append("source Scripts/%s/Schedule_Run_PRMC.sh &&\n"%(folder))
    #     for index,value_list in enumerate(all_value_list):
    #         line_temp = line_template
    #         for k_index,key in enumerate(params):
    #             if key == 'beta':
    #                     line_temp = re.sub("#"+key+"#", '%.3f'%(float)(value_list.split("#")[k_index]), line_temp)
    #             else:
    #                 line_temp = re.sub("#"+key+"#", value_list.split("#")[k_index], line_temp)
    #         # print(line_temp)
    #         if index == len(all_value_list) - 1:
    #             line_out.append(line_temp)
    #         else:
    #             line_out.append(line_temp+"\n")
    #     new_file.writelines(line_out)
            
        
    
                
            