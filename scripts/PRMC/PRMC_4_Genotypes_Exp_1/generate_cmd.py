# import the regex module
import re
import os 
from pathlib import Path
import numpy as np
import yaml

def read_parameters():
    keys = []
    values = []
    print("Reading parameters.yml")
    with open(r'parameters.yml') as file:
        documents = yaml.full_load(file)
        for item, doc in documents.items():
            keys.append(item)
            values.append(doc)    
    return keys,values            
        
if __name__=="__main__":
    file_path = str(Path.cwd())
    folder = file_path.split("/")[-1]
    print("Will generate cmd to folder: " + folder)
    param_keys, param_values = read_parameters()
    print(param_keys)
    print(param_values)
    run_line_total = 1
    for value in param_values:
        run_line_total *= len(value)
    print("Will generate " + str(run_line_total) + " lines")
    template = (r"cmd.template")    
    line_out_template = ""
    line_out_list = []

    with open(template) as old_file:
        with open(r"run_cmd.sh", "w") as new_file:
            line_count = 0
            for line in old_file:
                line_out = line
                if line_count <= 1:
                    line_out = re.sub("#folder#", folder, line_out)
                    new_file.write(line_out)
                else:   
                    line_out = re.sub("#folder#", folder, line_out)
                    line_out_template = line_out
                line_count += 1
    
    print(line_out_template)
    
    all_tempty = False
    count = 0
    
    for index,key in enumerate(param_keys):
        print("Key " + str(key) + " will be replaced by " + str(param_values[index]))
                        
        line_out = ""
        if len(line_out_list) == 0:
            for value in param_values[index]:
                line_out_list.append(str(value))
        else:
            temp = []
            for line in line_out_list:
                for value in param_values[index]:
                    temp.append(line + " - " + str(value))
            line_out_list = temp
                
        # for value in param_values[index]:
        #     print("  Value " + str(value))
        
    for index,line in enumerate(line_out_list):
        print(index, line)                
                
    # with open(template) as old_file:
    #     with open(r"run_cmd.sh", "w") as new_file:  
    #         line_count = 0
    #         for line in old_file:
    #             print(line)
    #             line_out = line
    #             if line_count <= 1:
    #                 line_out = re.sub("#folder#", folder, line_out)
    #                 new_file.write(line_out)
    #             else:
    #                 line_out = line
    #                 line_out = re.sub("#folder#", folder, line_out)
    #                 for key1 in param_keys:
    #                     print("For key " + key1)
    #                     for index,key2 in enumerate(param_keys):
    #                         print(" |-- replacing " + key2)
    #                     #     for value in param_values[index]:
    #                     #         print("Replacing " + key2 + " with value " + str(value))
    #                     #         line_out = re.sub("#"+key+"#", str(value), line_out)
    #                     #         print(line_out)
    #                     # new_file.write(line_out + " &&\n")
    #             line_count += 1
            