import os
import glob
import pandas as pd
import yaml
import sys, getopt
import scipy as sp

# Copyright 2024 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.

# Prints charge and discharge capacity for selected cycles
# Reads a CSV file with TONGJI-KIT formatting as described in read_csv_rows()

def quality_check(file_path):

    #list_of_files = glob.glob(file_path + '*.csv*')
    mapper = read_mapper()
    list_of_tester_types = []
    for dict in mapper:
        list_of_tester_types.append(dict['tester'])
    print('Please select file/tester type from the following options: ')
    tester = input(str(list_of_tester_types))
    for dict in mapper:
        if tester == dict['tester']:
            df = file_reader(file_path, dict['reader_func'], '')
            col_dict = dict['column_names']
            cycle_col = col_dict['cycle_index']
            current_col = col_dict['i']
            capacity_c_col = col_dict['Qc']
            capacity_d_col = col_dict['Qd']
    cycle_str = input('Please input the cycles you wish to compare separated by commas (ex: 1,50,100,150,200): ')
    cycles = [int(s) for s in cycle_str.split(',')]
    print('This file has ' + str(len(df)) + ' lines.')
    max_cycles = df[cycle_col].max() 
    print('The max cycle # is: ' + str(max_cycles))

    for c in cycles:
        rows = df[df[cycle_col]==c]
        no_rows = len(rows.index)
        try:
            start_row = df.index[df[cycle_col]==c][0]
        except IndexError:
            print('Selected cycle #'+ str(c) + ' is an invalid cycle.')
            continue
        print('\n-----Cycle ' + str(c) + ' with ' + str(no_rows) + ' rows-----')
        df_int = pd.DataFrame(columns=['i','time'])
        c_list = []
        t_list = []
        for r in range(start_row,start_row + no_rows):
            if df[current_col].loc[r]<0:
                if df[current_col].loc[r-1]>=0 and r > 0:
                    print('Charge capacity at cycle ' + str(c) + ': ' + str(df[capacity_c_col].loc[r-1]))
                elif r == start_row+no_rows-1:
                    print('Discharge capacity at cycle ' + str(c) + ': ' + str(df[capacity_d_col].loc[r]))
            else:
                if c == 7978: 
                    c_list.append(df[current_col].loc[r])
                    t_list.append(df['Timestamp'].loc[r])
        df_int['i'] = c_list
        df_int['time'] = t_list
        integrate(df_int)

def file_reader(path, name, sheetname):
    read_func = getattr(pd, name)
    if name=='read_excel':
        return read_func(path,sheet_name=sheetname)
    else:
        return read_func(path)

def read_mapper():
    with open(f'mapper.yaml','r') as f:
        return list(yaml.safe_load_all(f))
    
def integrate(df):
    df_time = pd.DataFrame()
    df_time['pystamp'] = pd.to_datetime(df['time'])
    df_time['inttime'] = df_time['pystamp'].astype(int)
    df_time['inttime'] = df_time['inttime'].div(10**9)
    df_time['Time [s]'] = df_time['inttime']-df_time['inttime'].iloc[0]
    out = sp.integrate.simpson(df['i'], df_time['Time [s]'])
    print('Integrated: ' + str(out/3600))

def main(argv):
    mode = 'env'
    path = r'\\'

    try:
        opts, args = getopt.getopt(argv, "h")
        path = args[0]
    except getopt.GetoptError:
        print('run as: python quality_check.py <path>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('run as: python quality_check.py <path>')
            sys.exit()

    quality_check(path)

if __name__ == "__main__":
   main(sys.argv[1:])
