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
import multiprocessing

def generate_salt(n = 20):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))


def test(N):
    outlist = []
    for n in [100000, 250000, 500000, 750000, 1000000, 2000000]:
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
        

        outlist.append("{}% dupe chance: id_size = {}, pop_size = {} (test duration {} seconds)".format(dupe_count, N, n, round(time.time() - start )))
        if dupe_count == 100:
            break
    for line in outlist:
        print(line)


if __name__ == "__main__":

    '''
    Reduced program to test duplications when given different sizes of data
    
    '''
    for N in [11,12,13,14,15]:
        p1 = multiprocessing.Process(target=test, args=(N,))
        p1.start()