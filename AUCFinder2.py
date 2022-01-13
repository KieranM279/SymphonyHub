#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 14:31:40 2022

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
                         'fields':['id_sub','vload_d0','vload_d4','vload_d7','vload_d14','vload_d27'],
                         'days':[0,4,7,14,27]},
             
             'ATACCC':{'filename':'2021_10_08 ATACCC Master Result Spreadsheet.xlsx',
                       'fields':['id_sub','ct_d0','ct_d1','ct_d2','ct_d3','ct_d4','ct_d5','ct_d6','ct_d7','ct_d8','ct_d9','ct_d10','ct_d11','ct_d12','ct_d13','ct_d14','ct_d15','ct_d16','ct_d17','ct_d18','ct_d19','ct_d20','ct_d28'],
                       'days':[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,28]},
             
             'Fusion':{'filename':'2021_10_08 FUSION Master Result Spreadsheet.xlsx',
                       'fields':['id_sub','ct_d0','ct_d1','ct_d2','ct_d3','ct_d4','ct_d5','ct_d6','ct_d7','ct_d8','ct_d9','ct_d10','ct_d11','ct_d12','ct_d13', 'ct_d27'],
                       'days':[0,1,2,3,4,5,6,7,8,9,10,11,12,13,27]},
             
             'London':{'filename':'2021_10_08 ATACCC2_LONDON Master Result Spreadsheet.xlsx',
                       'fields':['id_sub','ct_d0','ct_d1','ct_d2','ct_d3','ct_d4','ct_d5','ct_d6','ct_d7','ct_d8','ct_d9','ct_d10','ct_d11','ct_d12','ct_d13'],
                       'days':[0,1,2,3,4,5,6,7,8,9,10,11,12,13]},
             
             'Bolton':{'filename':'2021_10_08 ATACCC2_BOLTON Master Result Spreadsheet.xlsx',
                       'fields':['id_sub','ct_d0','ct_d1','ct_d2','ct_d3','ct_d4','ct_d5','ct_d6','ct_d7','ct_d8','ct_d9','ct_d10','ct_d11','ct_d12','ct_d13'],
                       'days':[0,1,2,3,4,5,6,7,8,9,10,11,12,13]}}

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
    x = x*((1000/150)*(100/5))

    return(x)

#############    The Translator    ################

####    Step 5    ####    individual area calculators    ####

# For when there are missing values either side of a Viral load
def singleAUC(x):
    
    auc = (0.5 * x * 1)
    
    return(auc)

# For when there are two viral loads in a row
def multiAUC(y1,y2,d1,d2):
    
    # Half the sum of the parallel sides
    # times the distance between them.
    # Thats how you calculate
    # the area of a trapezium.
    x = 0.5*(d2-d1)*(y1+y2)
    
    return(x)

# Returns a list of only the numeric scores for a given participant
def zeroAUC(dict_entry):
    
    scores = list()
    
    for vload in dict_entry:
    
        if type(vload) == int or type(vload) == float:
            scores.append(vload)
    
    return(scores)


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
    data = data.fillna(value= '.')
    #data = data.replace('.',1000)
    data = data.replace('undetected',0)
    data = data.replace('detected',35)
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


#### Step 4 #### Convert Ct Values to viral load ####

def convCt(data):
    
    dictionary = {}
    
    for i in data.keys():
        
        vloads = list()
        
        for ct in data[i]:
            
            if ct == '.':
                vload = ct
            elif ct == 0:
                vload = ct
            else:
                vload = Ct_ViralLoad(ct)
            
            vloads.append(vload)
        
        dictionary[i] = vloads
    
    return(dictionary)
            


ATACCC_data = convCt(ATACCC_data)
Bolton_data = convCt(Bolton_data)
London_data = convCt(London_data)
Fusion_data = convCt(Fusion_data)



##### Step 5 #### Trapezium finder function ####

def findTraps(keys, scores):
        
    
    trapezium_list = list()
    
    for n, v in enumerate(scores):
        
        
        # for the first pass
        if n == 0:
        
            # Skip if its zero or missing
            if v == 0 or v == '.':
                continue
            
            # Calculate the AUC
            elif v > 0 and scores[n+1] != '.' and scores[n+1] > 0:
            
                a = v
                b = scores[n+1]
                auc = multiAUC(a, b, keys[n], keys[n+1])
            
                trapezium_list.append(auc)
                continue
            elif v > 0 and (scores[n+1] == 0 or scores[n+1] == '.'):
            
                auc = singleAUC(v)
                trapezium_list.append(auc)
                continue
        
        # for last pass
        elif n == (len(scores)-1):
            if v == 0 or v == '.':
                continue
            
            elif v > 0 and (scores[n-1] == 0 or scores[n-1]=='.'):
                        
                auc = singleAUC(v)
                trapezium_list.append(auc)
            else:
                pass
            break
        
        
        elif n > 0 and n < (len(scores)-1):
            
            # Skip if zero or missing
            if v == 0 or v == '.':
                continue
            
            # MultiAUC if value and next value or >0
            elif v > 0 and scores[n+1] != '.' and scores[n+1] > 0:
                
                a = v
                b = scores[n+1]
                auc = multiAUC(a,b,keys[n],keys[n+1])
                
                trapezium_list.append(auc)
                continue
            
            
            if v > 0 and (scores[n+1] == 0 or scores[n+1] == '.'):
                
                if (scores[n-1] == 0 or scores[n-1]=='.') and v > 0 and (scores[n+1] == 0 or scores[n+1] =='.'):
                
                    auc = singleAUC(v)
                    trapezium_list.append(auc)
                    continue
            else:
                continue
            
    
    if trapezium_list == []:
        
        print('help')
            
    
    return(sum(trapezium_list))

##### Step 6 #### Collate AUCs #####

def collateAUC():
    
    AUC_dict = {}
    
    for i in symphony_ids:
    
        #### INSTINCT ####
        
        if i[0:3] == 'INS':
            
            # If the ID is not present in the viral load dataset
            if i not in INSTINCT_data.keys():
                # enter a blank the into the dictionary
                AUC_dict[i] = ''
                continue
            
            
            # Get list of numeric scores
            zeroCheck = zeroAUC(INSTINCT_data[i])
            # If they are all zero
            if all(item == 0 for item in zeroCheck):
                
                # Then AUC is also zero
                AUC_dict[i] = 0
                continue

            else:
            
                AUC_dict[i] = findTraps(file_dict['INSTINCT']['days'], INSTINCT_data[i])
                
                
        #### ATACCC ####
        
        if i[0:3] == 'ATA':
            
            #print(i)
            
            # If the ID is not present in the viral load dataset
            if i not in ATACCC_data.keys():
                # enter a blank the into the dictionary
                AUC_dict[i] = ''
                continue
            
            
            # Get list of numeric scores
            zeroCheck = zeroAUC(ATACCC_data[i])
            # If they are all zero
            if all(item == 0 for item in zeroCheck):
                
                # Then AUC is also zero
                AUC_dict[i] = 0
                continue

            else:
            
                AUC_dict[i] = findTraps(file_dict['ATACCC']['days'], ATACCC_data[i])
            
            
        
        #### Fusion ####
        
        if i[0:4] == 'FUZH':
            
            # If the ID is not present in the viral load dataset
            if i not in Fusion_data.keys():
                # enter a blank the into the dictionary
                AUC_dict[i] = ''
                continue
            
            
            # Get list of numeric scores
            zeroCheck = zeroAUC(Fusion_data[i])
            # If they are all zero
            if all(item == 0 for item in zeroCheck):
                
                # Then AUC is also zero
                AUC_dict[i] = 0
                continue

            else:
            
                AUC_dict[i] = findTraps(file_dict['Fusion']['days'], Fusion_data[i])
                
                
                
                
                
        #### London ####
        
        if i[0:4] == 'FUZR':
            
            # If the ID is not present in the viral load dataset
            if i not in London_data.keys():
                # enter a blank the into the dictionary
                AUC_dict[i] = ''
                continue
            
            
            # Get list of numeric scores
            zeroCheck = zeroAUC(London_data[i])
            # If they are all zero
            if all(item == 0 for item in zeroCheck):
                
                # Then AUC is also zero
                AUC_dict[i] = 0
                continue

            else:
            
                AUC_dict[i] = findTraps(file_dict['London']['days'], London_data[i])
        #### Bolton ####
        
        
        if i[0:3] == 'BUZ':
            
            # If the ID is not present in the viral load dataset
            if idTrans(i,4) not in Bolton_data.keys():
                # enter a blank the into the dictionary
                AUC_dict[i] = ''
                continue
            
            
            # Get list of numeric scores
            zeroCheck = zeroAUC(Bolton_data[idTrans(i,4)])
            # If they are all zero
            if all(item == 0 for item in zeroCheck):
                
                # Then AUC is also zero
                AUC_dict[i] = 0
                continue

            else:
            
                AUC_dict[i] = findTraps(file_dict['Bolton']['days'], Bolton_data[idTrans(i,4)])
        
    return(AUC_dict)

AUC_dict = collateAUC()


####    Step 7    ####    Get log values    ####

def getLog(raw_dictionary):
    
    dictionary = {}
    
    for key, auc in raw_dictionary.items():
        
        if auc == '':
            entry = {'AUC':'',
                     'log10(AUC)':''}
        elif auc == 0:
            entry = {'AUC':0,
                     'log10(AUC)':0}
        elif auc < 1:
            entry = {'AUC':auc,
                     'log10(AUC)':0}
        else:
            entry = {'AUC':auc,
                     'log10(AUC)':math.log10(auc)}
        
        dictionary[key] = entry
    
    return(dictionary)

AUC_dict = getLog(AUC_dict)


####     Step 8    ####    Output the data as a 'csv'    ####


def getArray(dictionary):

    data = pd.DataFrame.from_dict(dictionary)

    return(data.transpose())

data = getArray(AUC_dict)

data.to_csv(dir_dict['output_dir'] + 'auc_output.csv')

####    Concluding Statements    ####

end = time.time()
print('==============================================')
print('Total time ellapsed: ' + str(end-start))
print('==============================================')

del start
del end
