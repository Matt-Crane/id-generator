import pandas as pd
import luhn
import hashlib as hl
import os
import sys
from tkinter import *
from tkinter import filedialog as fd
import random
import string


def file_dialog():
    '''
    Opens file dialog to find appropriate files
    '''
    root = Tk()
    root.withdraw()
    
    # limit file types
    filetypes = (
        ('text files', '*.txt'),
        ('csv files', '*.csv')
    )
    
    filename = fd.askopenfilename(
        title='Open a file',
        initialdir=os.getcwd(),
        filetypes=filetypes)
    return filename


def generate_salt(n = 20):
    '''
    Generate a random string of n (default 20) ascii upper and lower case characters and digits
    '''
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=n))


def input_settings():
    '''
    Load the args and set the program settings
    arg 1: LLC_MODE, True or False.
        determines program flow (LLC MODE automates where possible with LLC-specific assumptions)
    arg 2: N, int.
        The size of the ID length (before addition of 2 extra digits)
        Final ID length will be N+2
    '''
    if len(sys.argv) > 1 and sys.argv[1].lower() == "true":
        try:
            LLC_mode = True
        except:
            print("Error in input 'LLC_MODE' (position 1), using default settings")

        if len(sys.argv) > 2:
            try: 
                N = int(sys.argv[2])
            except EXCEPTION:
                print("Error in input 'N' (position 2), using default value")
        else:
            N = 14
    else:
        LLC_mode = False
        N = 14

        
    return LLC_mode, N

if __name__ == "__main__":

    # Removing a irritating window that pops up by default with tkinter
    root = Tk()
    root.withdraw()

    # Get input settings (LLC_mode True/False) for program flow
    LLC_mode, N = input_settings()

    # STEP 1: FILE SETUP
    # change dir to to test output dir, can be changed to suit
    wd = fd.askdirectory()
    os.chdir(wd)
    # import file - changed to ODBC to SQL to get lastest ALF from file 1- will need updating if file 1 changed
    #cnxn = pyodbc.connect('DSN=?????')
    #query = 'SELECT * FROM schema.table_name;'
    temp_schema_placeholder = "SCHEMA"
    #idbase = pd.read_sql(query, cnxn)
    inputfile = file_dialog()
    # read in file as per user defined input
    idbase = pd.read_csv(inputfile)
    # select and keep column to hash - user can select one column from list 
    if LLC_mode:
        idtohash = "ALF_E"
    else:
        idtohash = input('please type name of id column to hash option in input file are' +str(list(idbase))+' ... ')
    idbase = idbase[[idtohash]]

    # STEP 2: HASHING TO GENERATE CONSISTENT ID
    # add salt 

    while True:
        salt = generate_salt()
        idbase['idplussalt'] = idbase[idtohash].apply(lambda x: str(x) + salt)
        # perform SHA256 hash and remove chars by converting to decimal. 
        idbase['hashedid'] = [str(int(hl.sha256(str.encode(str(i))).hexdigest(), 16))for i in idbase['idplussalt']]

        # string down to first 9 digits. Increases risk of duplicates
        idbase['hashedidN'] = idbase['hashedid'].str[:N]
        # dulicate checker
        idbase['dupflag'] = idbase.duplicated(['hashedidN'], keep=False)
        # check all ids are unqiue any will return true if one or more elements are ture. If false, all ids are unique
        if idbase.dupflag.any() == True:
            print('Duplicate IDs. Regenerating salt...')
            continue
            # restart loop
        else:
            break
            # Once on duplicates are generated, continue

            
    # create directory for salt
    salt_path = os.path.join(wd,'salt')
    if not os.path.exists(salt_path):
        os.makedirs(salt_path) 
    else:
        raise FileExistsError("File {} already exists".format(salt_path))
    # store salt for reproducability
    text_file = open(os.path.join(salt_path, temp_schema_placeholder+'_salt.txt'),'w')
    text_file.write(salt)
    text_file.close()

    # STEP 3: add prefix
    # define 2 digit prefix for id - should evaluate if len is 2
    if LLC_mode:
        prefix = "1"
    else:
        prefix = input('Define a one digit prefix number for id ')
    idbase['hashedidN_pref'] = str(prefix) + idbase['hashedidN']

    # STEP 4
    # generate the luhn check digit in new column for visability (will be dropped)
    idbase['luhn1'] = idbase['hashedidN_pref'].apply(lambda x: luhn.generate(x))
    # append the check digit
    idbase['hashedidN_pref_check'] = idbase['hashedidN_pref'].apply(lambda x: luhn.append(x))
    # test verify
    idbase['luhnvalid'] = idbase['hashedidN_pref_check'].apply(lambda x: luhn.verify(x))
    # check if any invalid numbers
    if idbase.luhnvalid.all() == True:
        print('check digits passed validation')
    elif idbase.luhnvalid.all() == False:
        raise ValueError("Luln check digit failed to validate")
        
    # STEP 5: cleanup and strip down
    # rename new id column
    if LLC_mode:
        idcolname = "encrytpedID"
    else:
        idcolname = input('specify column name for new ID... ')
    idbase.rename(columns={'hashedidN_pref_check':idcolname},inplace=True)

    # strip down file
    sailpreg = idbase[[idtohash, idcolname]]

    #debug prints
    print(idbase)
    print(sailpreg)

    # create input for file name
    if LLC_mode:
        filename = os.path.split(inputfile)[1].split(".")[0] + "_encypted"
    else:
        filename = input('please define a filename for output... ')
    # export as csv
    sailpreg.to_csv(filename+'.csv', index=False)
