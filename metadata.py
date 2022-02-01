#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 10:50:51 2022

@author: kieran
"""

# Script to find all the metadata for the paticipants within SYMPHONY


import os
#os.chdir('C:/Users/kiera/Desktop/Symphony/Symptom Diary Import')
os.chdir('/Volumes/kmadon/Documents/InProgress/SymphonyHub/')
import pandas as pd
import time
start = time.time()


#############    Required Files    ################


file_dict = {'Symphony':{'filename':'2022_01_12 SYMPHONY Master Results Spreadsheet.xlsx',
                         'fields':['id_sub']},
             
             'INSTINCT':{'filename':'2021_10_08 INSTINCT Master Results Spreadsheet.xlsx',
                         'fields':['id_sub','vload_d0','vload_d4','vload_d7','vload_d14','vload_d27', 'vload_3m','vload_6m']},
             
             'ATACCC':{'filename':'2021_10_08 ATACCC Master Result Spreadsheet.xlsx',
                       'fields':['id_sub','ct_dN0','ct_d0','ct_d1','ct_d2','ct_d3','ct_d4','ct_d5','ct_d6','ct_dN7','ct_d7','ct_d8','ct_d9','ct_d10','ct_d11','ct_d12','ct_d13','ct_d14','ct_d15','ct_d16','ct_d17','ct_d18','ct_d19','ct_d20','ct_d28']},
             
             'Fusion':{'filename':'2021_10_08 FUSION Master Result Spreadsheet.xlsx',
                       'fields':['id_sub','type','hh','Overall_PCR']},
             
             'London':{'filename':'2021_10_08 ATACCC2_LONDON Master Result Spreadsheet.xlsx',
                       'fields':['id_sub','ct_d0','ct_d1','ct_d2','ct_d3','ct_d4','ct_d5','ct_d6','ct_d7','ct_d8','ct_d9','ct_d10','ct_d11','ct_d12','ct_d13']},
             
             'Bolton':{'filename':'2021_10_08 ATACCC2_BOLTON Master Result Spreadsheet.xlsx',
                       'fields':['id_sub','ct_d0','ct_d1','ct_d2','ct_d3','ct_d4','ct_d5','ct_d6','ct_d7','ct_d8','ct_d9','ct_d10','ct_d11','ct_d12','ct_d13']}}

##########    File paths    ##########

#######      Path Variables required      #######

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


#### Import the list of participants within Symphony ####

def getSymphony():
    
    # Establish the path of the Symphony MRS
    filename = '2022_01_12 SYMPHONY Master Results Spreadsheet.xlsx'
    path = str(dir_dict['MRS_path']) + str(filename)
    #path = "/Volumes/kmadon/Documents/InProgress/SymphonyHub/symphony_test/test_mrs.xlsx"
    
    
    # Import list of IDs from the Symphony MRS
    fields = ['id_sub']
    participants = pd.read_excel(path,
                                 sheet_name='Raw Symptom Scores',
                                 usecols=(fields))
    
    # Remove NAs and export as list
    participants = participants.dropna()
    part_list = participants['id_sub'].tolist()
    
    return(part_list)

symphony_ids = getSymphony()





####    Import the metadata from the cohort's MRSs  ####

def getMetadata(filename, fields):

    path = dir_dict['MRS_path'] + str(filename)


    # Import the Viral load data from the INSTINCT MRS
    data = pd.read_excel(path,
                         sheet_name='Summary_Tab',
                         usecols=(fields),
                         index_col=(0))


    return(data)


fusion_data = getMetadata(file_dict['Fusion']['filename'],file_dict['Fusion']['fields'] )










end = time.time()

print('Time ellapsed: ' + str((end-start)))

del start
del end