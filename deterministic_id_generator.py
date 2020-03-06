import pandas as pd
import luhn
import hashlib as hl
import os
import sys
#import tkinter as tk
#import pyodbc


# STEP 1: FILE SETUP
# change dir to to test output dir, can be chnaged to suit
wd = input('specify working directory for outputs... ')
os.chdir(wd)
# import file - chnaged to ODBC to SQL to get lastest ALF from file 1- will need updating if file 1 changed
#cnxn = pyodbc.connect('DSN=?????')
#query = 'SELECT * FROM schema.table_name;'
#idbase = pd.read_sql(query, cnxn)
inputfile = input('specify file for input including full filepath and file extension... ')
# read in file as per user defined input
idbase = pd.read_csv(inputfile)
# select and keep column to hash - user can select one column from list 
idtohash = input('please type name of id column to hash option in input file are' +str(list(idbase))+' ... ')
idbase = idbase[[idtohash]]

# STEP 2: HASHING TO GENERATE CONSISTENT ID
# add salt 
salt = input('define a salt... ')
idbase['idplussalt'] = idbase[idtohash].apply(lambda x: str(x) + salt)
# perform SHA256 hash
idbase['hashedid'] = [hl.sha256(str.encode(str(i))).hexdigest() for i in idbase['idplussalt']]
# remove chars - only want digits - does run risk of introducing dups - this checked a few lines doen
chars = {'a':'','b':'','c':'','d':'','e':'','f':''}
idbase['hashedid2'] = idbase['hashedid'].replace(chars, regex=True)
# string down to first 9 digits
idbase['hashedid9'] = idbase['hashedid2'].str[:9]
# dulicate checker
idbase['dupflag'] = idbase.duplicated(['hashedid9'], keep=False)
# check all ids are unqiue any will return true if one or more elements are ture. If false, all ids are unique
if idbase.dupflag.any() == True:
    print('STOP - duplicate IDs. Please rerun and define new salt')
    sys.exit()
    #print('STOP - duplicate IDs. Please define new salt')
elif idbase.dupflag.all() == False:
    print('no duplication in ids with defined salt')
# create directory for salt
if not os.path.exists(wd+'/salt'):
    os.makedirs(wd+'/salt') 
# store salt for reproducability
text_file = open(wd+'\salt\\'+'salt'+salt[:5]+'.txt','w+')
text_file.write(salt)
text_file.close()

# STEP 3: add prefix
# define 2 digit prefix for id - should evaluate if len is 2
prefix = input('Define a 1 digit prefix number for id ')
idbase['hashedid11'] = str(prefix) + idbase['hashedid9']

# STEP 4
# generate the luhn check digit in new column for visability (will be dropped)
idbase['luhn1'] = idbase['hashedid11'].apply(lambda x: luhn.generate(x))
 # append the check digit
idbase['hashedid12'] = idbase['hashedid11'].apply(lambda x: luhn.append(x))
# test verify
idbase['luhnvalid'] = idbase['hashedid12'].apply(lambda x: luhn.verify(x))
# check if any invalid numbers
if idbase.luhnvalid.all() == True:
    print('no issue with check digits')
elif idbase.luhnvalid.all() == False:
    sys.exit('STOP - issue with luhn check digit')
    
# STEP 5: cleanup and strip down
# rename new id column
idcolname = input('specify column name for new ID... ')
idbase.rename(columns={'hashedid12':idcolname},inplace=True)
# strip down file
sailpreg = idbase[[idtohash, idcolname]]
# create input for file name
filename = input('please define a filename for output... ')
# export as csv
sailpreg.to_csv(filename+'.csv', index=False)
