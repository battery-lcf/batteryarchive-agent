import os
import glob
import pandas as pd
import csv
import sys, getopt

# Copyright 2021 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.

# Prints charge and discharge capacity for selected cycles
# Reads a CSV file with UCONN formatting as described in read_csv_rows()

def read_csv_rows(file_path):

    # column names:
    # Cycle_Index -> cycle_index
    # Test_Time(s) -> test_time
    # Current(A) -> i
    # Voltage(V) -> v
    # Date_Time -> date_time

    #print("path: " + file_path)

    list_of_files = glob.glob(file_path + '*.csv*')
    df = pd.read_csv(list_of_files[0]) #todo: modify when adding multiple files

    cycle_str = input('Please input the cycles you wish to compare separated by commas (ex: 1,50,100,150,200): ')
    cycles = [int(s) for s in cycle_str.split(',')]
    
    print('This file has ' + str(len(df)) + ' lines.')
    max_cycles = df['Cycle'].max()
    print('The # of cycles is: ' + str(max_cycles))

    for c in cycles:
        rows = df[df['Cycle']==c]
        no_rows = len(rows.index)
        start_row = df.index[df['Cycle']==c][0]
        print('\n-----Cycle ' + str(c) + ' with ' + str(no_rows) + ' rows-----')
        for r in range(start_row,start_row + no_rows):
            if df['Current (A)'].loc[r]<0:
                if df['Current (A)'].loc[r-1]>0:
                    print('Charge capacity at cycle ' + str(c) + ': ' + str(df['Capacity (Ah)'].loc[r-1]))
                elif r == start_row+no_rows-1:
                    print('Discharge capacity at cycle ' + str(c) + ': ' + str(df['Capacity (Ah)'].loc[r]))

def main(argv):
    mode = 'env'
    path = r'\\'

    try:
        opts, args = getopt.getopt(argv, "hm:p:t:", ["mode=", "path=", "test="])
    except getopt.GetoptError:
        print('run as: data_import.py -m <mode> -t <test> -p <path>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('data_import.py -m <mode> -t <test> -p <path>')
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
        elif opt in ("-t", "--test"):
            test = arg
        elif opt in ("-p", "--path"):
            path = arg

    read_csv_rows(path)

if __name__ == "__main__":
   main(sys.argv[1:])
