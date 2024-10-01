import os
import glob
import pandas as pd
import csv
import sys, getopt

# Copyright 2024 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.

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

    cycle_col = 'cycle number'
    current_col = '<I>/mA'
    capacity_c_col = 'Q charge/mA.h'
    capacity_d_col = 'Q discharge/mA.h'
    cycle_str = input('Please input the cycles you wish to compare separated by commas (ex: 1,50,100,150,200): ')
    cycles = [int(s) for s in cycle_str.split(',')]
    
    print('This file has ' + str(len(df)) + ' lines.')
    max_cycles = df[cycle_col].max()
    print('The # of cycles is: ' + str(max_cycles))

    for c in cycles:
        rows = df[df[cycle_col]==c]
        no_rows = len(rows.index)
        start_row = df.index[df[cycle_col]==c][0]
        print('\n-----Cycle ' + str(c) + ' with ' + str(no_rows) + ' rows-----')
        for r in range(start_row,start_row + no_rows):
            if df[current_col].loc[r]<0:
                if df[current_col].loc[r-1]>=0:
                    print('Charge capacity at cycle ' + str(c) + ': ' + str(df[capacity_c_col].loc[r-1]))
                elif r == start_row+no_rows-1:
                    print('Discharge capacity at cycle ' + str(c) + ': ' + str(df[capacity_d_col].loc[r]))

def main(argv):
    mode = 'env'
    path = r'\\'

    try:
        opts, args = getopt.getopt(argv, "h")
        path = args[0]
    except getopt.GetoptError:
        print('run as: quality_check.py <path>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('run as: quality_check.py <path>')
            sys.exit()

    read_csv_rows(path)

if __name__ == "__main__":
   main(sys.argv[1:])
