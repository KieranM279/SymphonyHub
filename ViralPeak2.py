#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 11:42:29 2022

@author: kieran
"""

import os
os.chdir('/Volumes/kmadon/Documents/InProgress/SymphonyHub/')
import pandas as pd
import time
import math

start = time.time()

#############    Required Files    ################


file_dict = {'Symphony':{'filename':'2022_01_12 SYMPHONY Master Results Spreadsheet.xlsx',
                         'fields':['id_sub']},
             
             'INSTINCT':{'filename':'2021_10_08 INSTINCT Master Results Spreadsheet.xlsx',
                         'fields':['id_sub','vload_d0','vload_d4','vload_d7','vload_d14','vload_d27', 'vload_3m','vload_6m']},
             
             'ATACCC':{'filename':'2021_10_08 ATACCC Master Result Spreadsheet.xlsx',
                       'fields':['id_sub','ct_dN0','ct_d0','ct_d1','ct_d2','ct_d3','ct_d4','ct_d5','ct_d6','ct_dN7','ct_d7','ct_d8','ct_d9','ct_d10','ct_d11','ct_d12','ct_d13','ct_d14','ct_d15','ct_d16','ct_d17','ct_d18','ct_d19','ct_d20','ct_d28']},
             
             'Fusion':{'filename':'2021_10_08 FUSION Master Result Spreadsheet.xlsx',
                       'fields':['id_sub','ct_dN0','ct_d0','ct_d1','ct_d2','ct_d3','ct_d4','ct_d5','ct_d6','ct_dN7','ct_d7','ct_d8','ct_d9','ct_d10','ct_d11','ct_d12','ct_d13','ct_dN13', 'ct_dN27', 'ct_d27']},
             
             'London':{'filename':'2021_10_08 ATACCC2_LONDON Master Result Spreadsheet.xlsx',
                       'fields':['id_sub','ct_d0','ct_d1','ct_d2','ct_d3','ct_d4','ct_d5','ct_d6','ct_d7','ct_d8','ct_d9','ct_d10','ct_d11','ct_d12','ct_d13']},
             
             'Bolton':{'filename':'2021_10_08 ATACCC2_BOLTON Master Result Spreadsheet.xlsx',
                       'fields':['id_sub','ct_d0','ct_d1','ct_d2','ct_d3','ct_d4','ct_d5','ct_d6','ct_d7','ct_d8','ct_d9','ct_d10','ct_d11','ct_d12','ct_d13']}}

##########    File paths    ##########

def getDir():
    
    file = open('mac_dir.txt')
    dictionary = {}
    
    # Parse the directories text file
    for ln in file.readlines():
        
        # Format and add to dictionary
        ln = ln.strip('\n')
        ln = ln.split('\t')
        dictionary[ln[0]] = ln[1]
    
    return(dictionary)

dir_dict = getDir()

###### Helper functions ######

def MotifF(motif, string):

    # Sets the length of the motif and string
    motif_length = len(motif)
    string_length = len(string)
    
    if motif_length > string_length:
        Bool = False
        return(Bool)

    # Loops as a sliding window through the String
    for i in range(string_length):

        # Potential match to motif
        P_match = string[i:i+motif_length]

        # Conditional identifying the presence of the motif
        if len(P_match) < motif_length:
            break
        elif motif == P_match:
            Bool = True
            #print(i)
            #print(len(P_match))
            break
        else:
            Bool = False

    return(Bool)


def idTrans(ids, n):
    
    
    # Set to Booleans to account for retrospectively recruited indexes
    retro_indexA = False
    retro_indexB = False
    
    if ids[-1] == 'A':
        retro_indexA = True
        ids = ids[0:len(ids)-1]
    
    if ids[-1] == 'B':
        retro_indexB = True
        ids = ids[0:len(ids)-1]
    
    
    # List the five cohorts
    cohorts = ['ATA','INS','FUZR','FUZHH','BUZ']
    
    dictionary = {'cohort':'',
                  'participant':''}
    
    # Loop through all the possible cohorts
    for c in cohorts:
        
        # if the cohort motif is present in the ID
        if MotifF(c,ids):
            
            
            # Remove the ID and transform remainder to an integer
            ids = ids.replace(c,'')
            
            # Save participant info
            dictionary['cohort'] = c
            dictionary['participant'] = int(ids)
    
    
    
    # Define the number of digits in the participant number
    if (dictionary['participant'] <= 9):
        length = 1
    
    elif (dictionary['participant'] >=10 and dictionary['participant'] <= 99):
        length = 2
    
    elif (dictionary['participant'] >= 100 and dictionary['participant'] <= 999):
        length = 3
        
    else:
        print('help: The participant number exceeds 999')
    
    # Identify the nunber of zeros needed
    zeros = n-length
    
    n_zero = ''
    
    for z in range(zeros):
        
        n_zero = n_zero + '0'
    
    
    if retro_indexA:
        return(dictionary['cohort'] + n_zero + str(dictionary['participant']) + 'A')
    elif retro_indexB:
        return(dictionary['cohort'] + n_zero + str(dictionary['participant']) + 'B')
    else:
        return(dictionary['cohort'] + n_zero + str(dictionary['participant']))




#############    The Translator    ################

def Ct_ViralLoad(x):

    # RNA copies per reaction
    x = math.exp((37.933-x)/1.418)

    # RNA copies per ml
    #x = x*((1000/150)*(25/5))
    x = x * 133.3333

    return(x)

#############    The Translator    ################


####    Step 1    ####    Get list of Symphony IDs    ####
def getSymphony(filename):

    # Identify path to file
    path = dir_dict['MRS_path'] + str(filename)

    # Import list of IDs from the Symphony MRS
    fields = file_dict['Symphony']['fields']
    participants = pd.read_excel(path,
                                 sheet_name='Raw Symptom Scores',
                                 usecols=(fields))
    participants = participants.dropna()
    part_list = list()

    # Create a list of the IDs
    for p in participants['id_sub']:

        part_list.append(p)

    return(part_list)

symphony_ids = getSymphony(file_dict['Symphony']['filename'])


####    Step 2    ####    Get Viral loads (ATACCC/INSTINCT)  ####

def getINSTINCT(filename):

    path = dir_dict['MRS_path'] + str(filename)

    fields = file_dict['INSTINCT']['fields']

    # Import the Viral load data from the INSTINCT MRS
    data = pd.read_excel(path,
                         sheet_name='Oroswab quantitative',
                         usecols=(fields),
                         index_col=(0))

    # Remove missing values
    data = data.fillna(value = 0)
    data = data.replace('.',0)

    return(data)

def getCt(filename,fields):
    
    # Identify the files pathway
    path = dir_dict['MRS_path'] + str(filename)
    
    # Import the data from the cohort's MRS
    data = pd.read_excel(path,
                         sheet_name='Ct_Values',
                         usecols=(fields),
                         index_col=(0))
    
    # These need to be reversed to 0 when the viral load data is here
    data = data.fillna(value= 10000)
    data = data.replace('.',10000)
    data = data.replace('undetected',502)
    data = data.replace('detected',501)
    data = data.replace('>40',40)
    
    return(data)


INSTINCT_data = getINSTINCT(file_dict['INSTINCT']['filename'])
ATACCC_data = getCt(file_dict['ATACCC']['filename'], file_dict['ATACCC']['fields'])
London_data = getCt(file_dict['London']['filename'], file_dict['London']['fields'])
Bolton_data = getCt(file_dict['Bolton']['filename'], file_dict['Bolton']['fields'])
Fusion_data = getCt(file_dict['Fusion']['filename'], file_dict['Fusion']['fields'])


#### Step 3 #### Data Transformation (to dictionary) ####


def dataTransform(df):
    
    # Transform df into Dictionary of Dictionaries
    dictof_dicts = df.to_dict(orient='index')
    
    # Convert DoD to Dictionary of Lists
    dictof_lists = {}
    for i in dictof_dicts.keys():
        
        dictof_lists[i] = list(dictof_dicts[i].values())
    
    
    return(dictof_lists)

INSTINCT_data = dataTransform(INSTINCT_data)
ATACCC_data = dataTransform(ATACCC_data)
Fusion_data = dataTransform(Fusion_data)
London_data = dataTransform(London_data)
Bolton_data = dataTransform(Bolton_data)


#### Step 4 #### Get the Peaks ####

def getPeaks():
    
    # Declare new Peak dictionary
    viral_peak_dict = {}
    
    # Loop through participants in Symphony
    for i in symphony_ids:
        
        
        
        
        #### INSTINCT ####
        
        if i[0:3] == 'INS':
            
            # Skip if they are not present in the MRS
            if i not in INSTINCT_data.keys():
                entry = {'peak_vl':'.',
                     'vl_sd':'.'}
                viral_peak_dict[i] = entry
            
            else:
                
                 # Isolate the list of loads
                 loads = INSTINCT_data[i]
                 # Find the index of the load peak
                 day_index = loads.index(max(loads))
                 # Find the study day of the load peak
                 day = file_dict['INSTINCT']['fields'][day_index+1]
                 
                 # If the max is 0, study day = '.'
                 if max(loads) == 0:
                     day = '.'

            # Add the data to the dictionary
            entry = {'peak_vl':max(loads),
                     'vl_sd':day.strip('vload_d')}
            viral_peak_dict[i] = entry
        
        
        
        #### ATACCC ####
        
        if i[0:3] == 'ATA':
            
            if i not in ATACCC_data.keys():
                entry = {'peak_vl':'.',
                     'vl_sd':'.'}
                viral_peak_dict[i] = entry
            
            else:
                
                ataloads = ATACCC_data[i]
            
                day_index = ataloads.index(min(ataloads))
                day = file_dict['ATACCC']['fields'][day_index+1]
                
                # Value missing
                if min(ataloads) == 10000:
                    entry = {'peak_vl':'missing',
                             'vl_sd':'.'}
                    viral_peak_dict[i] = entry
                    continue
                # Value detected
                elif min(ataloads) == 501:
                    entry = {'peak_vl':'detected',
                             'vl_sd':'.'}
                    viral_peak_dict[i] = entry
                    continue
                #Value undetected
                elif min(ataloads) == 502:
                    entry = {'peak_vl':0,
                             'vl_sd':'.'}
                    viral_peak_dict[i] = entry
                    continue
                
                # Value Ct to Viral load
                entry = {'peak_vl':Ct_ViralLoad(min(ataloads)),
                         'vl_sd':day.strip('ct_d')}
                viral_peak_dict[i] = entry
        
        
        
        #### Fusion ####
        
        if i[0:4] == 'FUZH':
            
            if i not in Fusion_data.keys():
                entry = {'peak_vl':'.',
                     'vl_sd':'.'}
                viral_peak_dict[i] = entry
            
            else:
                
                fusloads = Fusion_data[i]
            
                day_index = fusloads.index(min(fusloads))
                day = file_dict['Fusion']['fields'][day_index+1]

                # Value missing
                if min(fusloads) == 10000:
                    entry = {'peak_vl':'missing',
                             'vl_sd':'.'}
                    viral_peak_dict[i] = entry
                    continue
                # Value detected
                elif min(fusloads) == 501:
                    entry = {'peak_vl':'detected',
                             'vl_sd':'.'}
                    viral_peak_dict[i] = entry
                    continue
                #Value undetected
                elif min(fusloads) == 502:
                    entry = {'peak_vl':0,
                             'vl_sd':'.'}
                    viral_peak_dict[i] = entry
                    continue
                
                # Value Ct to Viral load
                entry = {'peak_vl':Ct_ViralLoad(min(fusloads)),
                         'vl_sd':day.strip('ct_d')}
                viral_peak_dict[i] = entry
                
                
        
        #### ATACCC2_London ####
        
        if i[0:4] == 'FUZR':
            
            if i not in London_data.keys():
                entry = {'peak_vl':'.',
                     'vl_sd':'.'}
                viral_peak_dict[i] = entry
            
            else:
                
                fuzloads = London_data[i]
            
                day_index = fuzloads.index(min(fuzloads))
                day = file_dict['London']['fields'][day_index+1]

                # Value missing
                if min(fuzloads) == 10000:
                    entry = {'peak_vl':'missing',
                             'vl_sd':'.'}
                    viral_peak_dict[i] = entry
                    continue
                # Value detected
                elif min(fuzloads) == 501:
                    entry = {'peak_vl':'detected',
                             'vl_sd':'.'}
                    viral_peak_dict[i] = entry
                    continue
                #Value undetected
                elif min(fuzloads) == 502:
                    entry = {'peak_vl':0,
                             'vl_sd':'.'}
                    viral_peak_dict[i] = entry
                    continue
                
                # Value Ct to Viral load
                entry = {'peak_vl':Ct_ViralLoad(min(fuzloads)),
                         'vl_sd':day.strip('ct_d')}
                viral_peak_dict[i] = entry
                
        
        
        #### ATACCC2_Bolton ####
        
        if i[0:3] == 'BUZ':
            
            if idTrans(i,4) not in Bolton_data.keys():
                entry = {'peak_vl':'.',
                     'vl_sd':'.'}
                viral_peak_dict[i] = entry
            
            else:
                
                buzloads = Bolton_data[idTrans(i,4)]
            
                day_index = buzloads.index(min(buzloads))
                day = file_dict['Bolton']['fields'][day_index+1]

                # Value missing
                if min(buzloads) == 10000:
                    entry = {'peak_vl':'missing',
                             'vl_sd':'.'}
                    viral_peak_dict[i] = entry
                    continue
                # Value detected
                elif min(buzloads) == 501:
                    entry = {'peak_vl':'detected',
                             'vl_sd':'.'}
                    viral_peak_dict[i] = entry
                    continue
                #Value undetected
                elif min(buzloads) == 502:
                    entry = {'peak_vl':0,
                             'vl_sd':'.'}
                    viral_peak_dict[i] = entry
                    continue
                
                # Value Ct to Viral load
                entry = {'peak_vl':Ct_ViralLoad(min(buzloads)),
                         'vl_sd':day.strip('ct_d')}
                viral_peak_dict[i] = entry
        
            
            
            
    return(viral_peak_dict)
    
peak_data = getPeaks()

####     Step 5    ####    Output the data as a 'csv'    ####


def getArray(dictionary):

    data = pd.DataFrame.from_dict(dictionary)

    return(data.transpose())

data = getArray(peak_data)

data.to_csv(dir_dict['output_dir'] + 'viralpeak_output.csv')



####    Concluding Statements    ####

end = time.time()
print('==============================================')
print('Total time ellapsed: ' + str(end-start))
print('==============================================')

del start
del end