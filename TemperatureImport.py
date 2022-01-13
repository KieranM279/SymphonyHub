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


#######      Filenames required      #######

symphony_filename = '2022_01_12 SYMPHONY Master Results Spreadsheet.xlsx'
days_filename = 'day_names.txt'

#######      Filenames required      #######

#######     Farenheit to Celcius converter     #######

def FtoC(f):
    
    c = (f-32) * (5/9)
    
    return(c)

#######     Farenheit to Celcius converter     #######

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



####    Step 1    ####    Get a list of all the Symphony IDs    ####

def getSymphony():
    
    path = str(dir_dict['MRS_path'] + symphony_filename)  
    
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
    ataccc_diary_list = os.listdir(dir_dict['ataccc_symptom_diaries'])
    instinct_diary_list = os.listdir(dir_dict['instinct_symptom_diaries'])
    bolton_diary_list = os.listdir(dir_dict['bolton_symptom_diaries'])
    london_diary_list = os.listdir(dir_dict['london_symptom_diaries'])
    fusion_diary_list = os.listdir(dir_dict['fusion_symptom_diaries'])
    
    ####    INSTINCT Diary Filenames    ####
    
    # Loop throught the list of filenames
    for filenameINS in instinct_diary_list:
        
        # Skip if it is not a Symptom Diary
        if filenameINS[0:3] != 'INS':
            continue
        
        elif str(filenameINS[7]) == 'i':
            dictionary[str(filenameINS[0:8])] = filenameINS
            continue
        
        
        # Create a dictionary of the participants and their diary filename
        dictionary[str(filenameINS[0:7])] = filenameINS
        
    
    ####    ATACCC Diary Filenames    ####
    
    # Loop throught the list of filenames
    for filenameATA in ataccc_diary_list:
        
        # Skip if it is not a Symptom Diary
        if filenameATA[0:3] != 'ATA':
            continue
        
        elif str(filenameATA[7]) == 'i':
            dictionary[str(filenameATA[0:8])] = filenameATA
            continue
        
        # Create a dictionary of the participants and their diary filename
        dictionary[str(filenameATA[0:7])] = filenameATA
      
    
    ####    FUSION Diary Filenames    ####
    
    # Loop through list of filenames
    for filenameFUSHH in fusion_diary_list:
        
        # Skip of not a Symptom Diary
        if filenameFUSHH[0:4] != 'FUZH':
            continue
        
        # Add to dictionary
        dictionary[idTrans(str(filenameFUSHH[0:9]),3)] = filenameFUSHH
    
    
    ####    ATACCC2 Bolton Diary Filenames    ####
    
    # Loop through th list of filenames
    for filenameBUZ in bolton_diary_list:
        
        # Skip if not a Symptom Diary
        if filenameBUZ[0:3] != 'BUZ':
            continue
        
        # Account for Non-recruited indexes
        elif (str(filenameBUZ[7]) == 'A' or str(filenameBUZ[7]) == 'B'):
            dictionary[idTrans(str(filenameBUZ[0:8]),3)] = filenameBUZ
            continue
            
        # Add to dictionary
        dictionary[idTrans(str(filenameBUZ[0:7]),3)] = filenameBUZ
    
    
    ####    ATACCC2 London Diary Filenames    ####
    
    # Loop through list of filenames
    for filenameFUZR in london_diary_list:
        
        # Skip if not a filename
        if filenameFUZR[0:4] != 'FUZR':
            continue
        
        # Account for non-recriuted indexes
        elif (str(filenameFUZR[8]) == 'A' or str(filenameFUZR[8]) == 'B'):
            dictionary[idTrans(str(filenameFUZR[0:9]),3)] = filenameFUZR
            continue
        
        # Add to dictionary
        dictionary[idTrans(str(filenameFUZR[0:8]),3)] = filenameFUZR
        
    
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
        
    elif filename[0:3] == 'BUZ':
        ###   ATACCC2 Bolton   ###
        path = str(dir_dict['bolton_symptom_diaries'] + str(filename))
        
    elif filename[0:4] == 'FUZR':
        ###   ATACCC2 London   ###
        path = str(dir_dict['london_symptom_diaries'] + str(filename))
    
    elif filename[0:4] == 'FUZH':
        ###   FUSION   ###
        path = str(dir_dict['fusion_symptom_diaries'] + str(filename))
    
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
del days_filename