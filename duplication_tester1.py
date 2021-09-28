import pandas as pd
import luhn
import hashlib as hl
import os
import sys
from tkinter import *
from tkinter import filedialog as fd
import random
import string
import time


def generate_salt(n = 20):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))



if __name__ == "__main__":

    '''
    Reduced program to test duplications when given different sizes of data
    
    '''
    for N in [9,10,11,12,13]:
        for n in [100, 1000, 10000, 25000, 50000, 75000, 100000, 200000, 500000]:
            input_data = {"id":[i for i in range(n)]}

            idbase = pd.DataFrame.from_dict(input_data)

            idtohash = "id"

            dupe_count = 0
            start = time.time()

            for i in range(100):
                salt = generate_salt()
                idbase['idplussalt'] = idbase[idtohash].apply(lambda x: str(x) + salt)
                # perform SHA256 hash and remove chars by converting to decimal. 
                idbase['hashedid'] = [str(int(hl.sha256(str.encode(str(i))).hexdigest(), 16))for i in idbase['idplussalt']]

                # string down to first 9 digits. Increases risk of duplicates
                idbase['hashedidN'] = idbase['hashedid'].str[:N]
                # dulicate checker
                idbase['dupflag'] = idbase.duplicated(['hashedidN'], keep=False)
                if idbase.dupflag.any() == True:
                    dupe_count += 1
            

            print("{}% dupe chance: id_size = {}, pop_size = {} (test duration {} seconds)".format(dupe_count, N, n, round(time.time() - start )))
            if dupe_count == 100:
                print("skipping larger checks (for sake of time)")
                break