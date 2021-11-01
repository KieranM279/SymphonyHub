# -*- coding: utf-8 -*-
"""
Created on Sat May  8 17:57:25 2021

@author: kieran
"""
import os
os.chdir('/Volumes/kmadon/Documents/InProgress/SymphonyHub/')
import pandas as pd

########        Filenames        ########

symphony_filename = '2021_10_25 SYMPHONY Master Results Spreadsheet.xlsx'
ataccc_filename = '2021_10_08 ATACCC Master Result Spreadsheet.xlsx'
instinct_filename = '2021_10_08 INSTINCT Master Results Spreadsheet.xlsx'

########        Filenames        ########

########          Paths          ########

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

########          Paths          ########

def DateTime_Date(x):

    if type(x) == str:
        x = 'missing'
        return(x)
    else:
        x = x.date()
        return(x)


####    Step 1    ####    Get list of IDs from Symphony    ####

def getSymphony():

    path = str(dir_dict['MRS_path'] + symphony_filename)

    # Import list of IDs from the Symphony MRS
    fields = ['id_sub']
    participants = pd.read_excel(path,
                                 sheet_name='Symptom Duration',
                                 usecols=(fields))
    part_list = list()

    # Create a list of the IDs
    for p in participants['id_sub']:

        part_list.append(p)

    return(part_list)

symphony_ids = getSymphony()

####    Step 2    ####    Get the Study day 0 Dates    ####

def getDates(loc, filename, cohort):

    # Create path to the particular MRS file
    path = str(loc + filename)

    # Change field names based on each cohort
    if cohort =='ataccc':
        fields = ['id_sub','date_d0']
    elif cohort == 'instinct':
        fields = ['id_sub','date_visit0']

    # Import the data from the MRS
    dates = pd.read_excel(path,
                          sheet_name='Dates',
                          usecols=(fields),
                          index_col=(0))

    dates = dates.fillna('missing')
    # Re-arrange data into a dictionary
    dictionary = dates.to_dict(orient='dict')
    dictionary = dictionary[fields[1]]

    return(dictionary)

ataccc_data = getDates(dir_dict['MRS_path'], ataccc_filename, 'ataccc')
instinct_data = getDates(dir_dict['MRS_path'], instinct_filename, 'instinct')

####    Step 3    ####    Create new dictionary of study dates    ####

def collateData():

    dictionary = {}

    # Create list of all available participant IDs
    dict_ids = list(ataccc_data.keys()) + list(instinct_data.keys())

    # Loop through IDs in Symphony
    for i in symphony_ids:
        print(i)
        # Basic entry layout
        entry = {'date_d0':''}

        # If the particpant in not found in either MRS
        if i not in dict_ids:

            entry['date_d0'] = 'not in MRS'

        # If the participant is in the MRS
        elif i in dict_ids:

            # Fund entry in the correct dictionary
            if i[0:3] == 'ATA':
                entry['date_d0'] = DateTime_Date(ataccc_data[i])

            elif i[0:3] == 'INS':
                entry['date_d0'] = DateTime_Date(instinct_data[i])

        # Add entry to larger dictionary
        dictionary[i] = entry

    return(dictionary)

final_dict = collateData()

####    Step 4    ####    Output data in a '.csv' file    ####

def getArray(dictionary):

    data = pd.DataFrame.from_dict(dictionary)

    return(data.transpose())

getArray(final_dict).to_csv(dir_dict['output_dir'] + 'studyday_output.csv')
