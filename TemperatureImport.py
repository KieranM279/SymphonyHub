# -*- coding: utf-8 -*-
"""
Created on Wed May  5 10:00:54 2021

@author: kiera
"""
import os
os.chdir('/Volumes/kmadon/Documents/InProgress/SymphonyHub')
import pandas as pd
import time

start = time.time()

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


#######      Path Variables required      #######

ataccc_symptom_diaries = dir_dict['ataccc_symptom_diaries']
instinct_symptom_diaries = dir_dict['instinct_symptom_diaries']
symphony_path = dir_dict['MRS_path']

#######      Path Variables required      #######

#######      Filenames required      #######

symphony_filename = '2021_10_25 SYMPHONY Master Results Spreadsheet.xlsx'
days_filename = 'day_names.txt'

#######      Filenames required      #######

#######     Farenheit to Celcius converter     #######

def FtoC(f):
    
    c = (f-32) * (5/9)
    
    return(c)

#######     Farenheit to Celcius converter     #######

####    Step 1    ####    Get a list of all the Symphony IDs    ####

def getSymphony():
    
    path = str(symphony_path + symphony_filename)  
    
    # Import list of IDs from the Symphony MRS
    fields = ['id_sub']
    participants = pd.read_excel(path,
                                 sheet_name='Raw Temperatures',
                                 usecols=(fields))
    participants = participants.dropna()
    part_list = list()
    
    # Create a list of the IDs
    for p in participants['id_sub']:
        
        part_list.append(p)
    
    return(part_list)

symphony_ids = getSymphony()


####    Step 2    ####    Get list of days for columns    ####

def getDays(filename):
    
    # Open the file with the name conversions
    names = open(filename)
    day_list = list()
    
    # Loop through the line of the symptom names file
    for ln in names.readlines():
        
        ln = ln.strip()
        
        # Create a list of the days
        day_list.append(ln)
        
    return(day_list)

# Create a list of the new file names
days = getDays(days_filename)


####   Step 3   ####   Create a dictionary of Symptom Diary filenames   ####

def DiaryDictmaker():
    dictionary = {}
    
    # Get a list of filenames from the TRACKER DATABASE
    ataccc_diary_list = os.listdir(ataccc_symptom_diaries)
    instinct_diary_list = os.listdir(instinct_symptom_diaries)
    
    ####    INSTINCT Diary Filenames    ####
    
    # Loop throught the list of filenames
    for filenameINS in instinct_diary_list:
        
        # Skip if it is not a Symptom Diary
        if filenameINS[0:3] != 'INS':
            continue
        
        # Create a dictionary of the participants and their diary filename
        dictionary[str(filenameINS[0:7])] = filenameINS
        
        if str(filenameINS[7]) == 'i':
            dictionary[str(filenameINS[0:8])] = filenameINS
    
    ####    ATACCC Diary Filenames    ####
    
    # Loop throught the list of filenames
    for filenameATA in ataccc_diary_list:
        
        # Skip if it is not a Symptom Diary
        if filenameATA[0:3] != 'ATA':
            continue
        
        # Create a dictionary of the participants and their diary filename
        dictionary[str(filenameATA[0:7])] = filenameATA
        
        if str(filenameATA[7]) == 'i':
            dictionary[str(filenameATA[0:8])] = filenameATA
    
    return(dictionary)

diary_dict = DiaryDictmaker()


####    Step 4    ####    Function to import the Symptom data    ####

def getData(filename):
    
    if filename[0:3] == 'INS':
        ###   INSTINCT   ###
        path = str(dir_dict['instinct_symptom_diaries'] + str(filename))
        
    elif filename[0:3] == 'ATA':
        ###   ATACCC   ###
        path = str(dir_dict['ataccc_symptom_diaries'] + str(filename))
    
    # Read the '.xlsx' file into python
    data = pd.read_excel(path,
                         sheet_name='SYMPTOM_DIARY',
                         header=1,
                         index_col=(0),
                         skiprows=([2,4]),
                         #skipfooter=35
                         )
    # Isolate the rows you want
    data2 = data[:1]
    
    # Clean up th data
    data2 = data2.fillna(value = '')
    data2 = data2.replace('.','')
    # Get the improved row names from Step 1
    return(data2)

#data = getData('INS0047.xlsx')


####    Step 5    ####    Re-organise data into a dictionary    ####

def reorgData(df):
    
    final_days_dict = {}
    
    # Create a dictionary of each of the temperature data (by day)
    days_dict = df.to_dict(orient='index')
    days_dict = days_dict['TEMPERATURE']
    
    # Loop through each day
    for i in days:
        
        # Add a blank if the day is not present in the Symptom Diary
        if i not in list(days_dict.keys()):
            final_days_dict[i] = ''
        else:
            
            # Isolate temperature
            temp = days_dict[i]
            
            # If the temp is reported in Farenheit, convert to celcius
            if temp != '' and temp > 80:
                temp = FtoC(temp)
                
            final_days_dict[i] = temp
    
    return(final_days_dict)

#test = reorgData(data)


####    Step 6    ####    Collate data     ####

def collateData():
    
    final_dict = {}
    entry = {}
    
    # Loop through symphony IDs
    for i in symphony_ids:
        
        print(i)
        
        # If there is no diary...
        if i not in list(diary_dict.keys()):
            
            # ...add a list of blanks
            for d in days:
                
                entry[d] = ''
        else:
            
            # Get the participant data
            diary = getData(diary_dict[i])
            # Re-organise the data into a dictionary
            entry = reorgData(diary)
        
        # Add the entry to the final dictionary
        final_dict[i] = entry
    
    return(final_dict)

temperature_data = collateData()


####    Step 7    ####    Export the data to a '.csv' file    ####

def getArray(dictionary):
    
    data = pd.DataFrame.from_dict(dictionary)
    
    return(data.transpose())

getArray(temperature_data).to_csv(dir_dict['output_dir'] + 'raw_temperatures.csv')


end = time.time()
print('===============================================')
print('Total time ellapsed: ' + str(end-start))
print('===============================================')

del start
del end