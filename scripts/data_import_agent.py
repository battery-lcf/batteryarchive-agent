#!/usr/bin/env python
# coding: utf-8
from imghdr import tests
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
from sqlalchemy import create_engine
import yaml
import sys, getopt
import logging
import logging.config
import zipfile
import time

# Copyright 2021 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.

# Function to convert a list to a string
def listToString(s):
    # initialize an empty string
    str1 = ""

    # traverse in the string
    for ele in s:
        str1 += ele

        # return string
    return str1


# unpack the dataframe and calculate quantities used in statistics
def calc_cycle_quantities(df):

    logging.info('calculate quantities used in statistics')

    tmp_arr = df[["test_time", "i", "v", "ah_c", 'e_c', 'ah_d', 'e_d', 'cycle_time']].to_numpy()

    start = 0
    last_time = 0
    last_i = 0
    last_v = 0
    last_ah_c = 0
    last_e_c = 0
    last_ah_d = 0
    last_e_d = 0
    initial_time = 0

    for x in tmp_arr:

        if start == 0:
            start += 1
            initial_time = x[0]
        else:
            if x[1] > 0:
                x[3] = (x[0] - last_time) * (x[1] + last_i) * 0.5 + last_ah_c
                x[4] = (x[0] - last_time) * (x[1] + last_i) * 0.5 * (x[2] + last_v) * 0.5 + last_e_c
                last_ah_c = x[3]
                last_e_c = x[4]
            elif x[1] < 0:
                x[5] = (x[0] - last_time) * (x[1] + last_i) * 0.5 + last_ah_d
                x[6] = (x[0] - last_time) * (x[1] + last_i) * 0.5 * (x[2] + last_v) * 0.5 + last_e_d
                last_ah_d = x[5]
                last_e_d = x[6]

        x[7] = x[0] - initial_time

        last_time = x[0]
        last_i = x[1]
        last_v = x[2]
        

    df_tmp = pd.DataFrame(data=tmp_arr[:, [3]], columns=["ah_c"])
    df_tmp.index += df.index[0]
    df['ah_c'] = df_tmp['ah_c']/3600.0

    df_tmp = pd.DataFrame(data=tmp_arr[:, [4]], columns=["e_c"])
    df_tmp.index += df.index[0]
    df['e_c'] = df_tmp['e_c']/3600.0

    df_tmp = pd.DataFrame(data=tmp_arr[:, [5]], columns=["ah_d"])
    df_tmp.index += df.index[0]
    df['ah_d'] = -df_tmp['ah_d']/3600.0

    df_tmp = pd.DataFrame(data=tmp_arr[:, [6]], columns=["e_d"])
    df_tmp.index += df.index[0]
    df['e_d'] = -df_tmp['e_d']/3600.0

    df_tmp = pd.DataFrame(data=tmp_arr[:, [7]], columns=["cycle_time"])
    df_tmp.index += df.index[0]
    df['cycle_time'] = df_tmp['cycle_time']

    return df


# calculate statistics and cycle time
def calc_stats(df_t):

    logging.info('calculate cycle time and cycle statistics')
    df_t['cycle_time'] = 0

    no_cycles = int(df_t['cycle_index'].max())

    # Initialize the cycle_data time frame
    a = [0 for x in range(no_cycles)]  # using loops

    df_c = pd.DataFrame(data=a, columns=["cycle_index"])

    df_c['cell_id'] = df_t['cell_id']
    df_c['cycle_index'] = 0
    df_c['v_max'] = 0
    df_c['i_max'] = 0
    df_c['v_min'] = 0
    df_c['i_min'] = 0
    df_c['ah_c'] = 0
    df_c['ah_d'] = 0
    df_c['e_c'] = 0
    df_c['e_d'] = 0
    df_c['v_c_mean'] = 0
    df_c['v_d_mean'] = 0
    df_c['test_time'] = 0
    df_c['ah_eff'] = 0
    df_c['e_eff'] = 0

    for c_ind in df_c.index:
        x = c_ind + 1

        df_f = df_t[df_t['cycle_index'] == x]

        df_f['ah_c'] = 0
        df_f['e_c'] = 0
        df_f['ah_d'] = 0
        df_f['e_d'] = 0

        if not df_f.empty:

            try:

                df_c.iloc[c_ind, df_c.columns.get_loc('cycle_index')] = x

                df_c.iloc[c_ind, df_c.columns.get_loc('v_max')] = df_f.loc[df_f['v'].idxmax()].v
                df_c.iloc[c_ind, df_c.columns.get_loc('v_min')] = df_f.loc[df_f['v'].idxmin()].v

                df_c.iloc[c_ind, df_c.columns.get_loc('i_max')] = df_f.loc[df_f['i'].idxmax()].i
                df_c.iloc[c_ind, df_c.columns.get_loc('i_min')] = df_f.loc[df_f['i'].idxmin()].i

                df_c.iloc[c_ind, df_c.columns.get_loc('test_time')] = df_f.loc[df_f['test_time'].idxmax()].test_time

                df_f['dt'] = df_f['test_time'].diff() / 3600.0
                df_f_c = df_f[df_f['i'] > 0]
                df_f_d = df_f[df_f['i'] < 0]

                df_f = calc_cycle_quantities(df_f)

                df_t.loc[df_t.cycle_index == x, 'cycle_time'] = df_f['cycle_time']
                df_t.loc[df_t.cycle_index == x, 'ah_c'] = df_f['ah_c']
                df_t.loc[df_t.cycle_index == x, 'e_c'] = df_f['e_c']
                df_t.loc[df_t.cycle_index == x, 'ah_d'] = df_f['ah_d']
                df_t.loc[df_t.cycle_index == x, 'e_d'] = df_f['e_d']

                df_c.iloc[c_ind, df_c.columns.get_loc('ah_c')] = df_f['ah_c'].max()
                df_c.iloc[c_ind, df_c.columns.get_loc('ah_d')] = df_f['ah_d'].max()
                df_c.iloc[c_ind, df_c.columns.get_loc('e_c')] = df_f['e_c'].max()
                df_c.iloc[c_ind, df_c.columns.get_loc('e_d')] = df_f['e_d'].max()

                df_c.iloc[c_ind, df_c.columns.get_loc('v_c_mean')] = df_f_c['v'].mean()
                df_c.iloc[c_ind, df_c.columns.get_loc('v_d_mean')] = df_f_d['v'].mean()

                if df_c.iloc[c_ind, df_c.columns.get_loc('ah_c')] == 0:
                    df_c.iloc[c_ind, df_c.columns.get_loc('ah_eff')] = 0
                else:
                    df_c.iloc[c_ind, df_c.columns.get_loc('ah_eff')] = df_c.iloc[c_ind, df_c.columns.get_loc('ah_d')] / \
                                                                       df_c.iloc[c_ind, df_c.columns.get_loc('ah_c')]

                if df_c.iloc[c_ind, df_c.columns.get_loc('e_c')] == 0:
                    df_c.iloc[c_ind, df_c.columns.get_loc('e_eff')] = 0
                else:
                    df_c.iloc[c_ind, df_c.columns.get_loc('e_eff')] = df_c.iloc[c_ind, df_c.columns.get_loc('e_d')] / \
                                                                      df_c.iloc[c_ind, df_c.columns.get_loc('e_c')]

            except Exception as e:
                logging.info("Exception @ x: " + str(x))
                logging.info(e)

    logging.info("cycle: " + str(x))

    df_cc = df_c[df_c['cycle_index'] > 0]
    df_tt = df_t[df_t['cycle_index'] > 0]

    return df_cc, df_tt


# import and save timeseries data
def read_timeseries_arbin(cell_id, file_path):

    # the importer can read Excel worksheets with the Channel number from Arbin files.
    # it assumes column names generated by the Arbin:
    # Cycle_Index -> cycle_index
    # Test_Time(s) -> test_time
    # Current(A) -> i
    # Voltage(V) -> v
    # Date_Time -> date_time

    logging.info('adding files')

    listOfFiles = glob.glob(file_path + '*.xls*')

    for i in range(len(listOfFiles)):
        listOfFiles[i] = listOfFiles[i].replace(file_path[:-1], '')

    logging.info('list of files to add: ' + str(listOfFiles))

    df_file = pd.DataFrame(listOfFiles, columns=['filename'])

    df_file.sort_values(by=['filename'], inplace=True)

    if df_file.empty:
        return

    df_file['cell_id'] = cell_id

    df_tmerge = pd.DataFrame()

    # Loop through all the Excel test files
    for ind in df_file.index:

        filename = df_file['filename'][ind]
        cellpath = file_path + filename
        timeseries = ""

        logging.info('processing file: ' + filename)

        if os.path.exists(cellpath):
            df_cell = pd.read_excel(cellpath, None)
            # Find the time series sheet in the excel file
            for k in df_cell.keys():
                if "hannel" in k:
                    logging.info("file: " + filename + " sheet:" + str(k))
                    timeseries = k

                    df_time_series_file = df_cell[timeseries]

                    df_time_series = pd.DataFrame()

                    df_time_series['cycle_index_file'] = df_time_series_file['Cycle_Index']
                    df_time_series['test_time'] = df_time_series_file['Test_Time(s)']
                    df_time_series['i'] = df_time_series_file['Current(A)']
                    df_time_series['v'] = df_time_series_file['Voltage(V)']
                    df_time_series['date_time'] = df_time_series_file['Date_Time']
                    df_time_series['filename'] = filename

                    df_time_series['ah_c'] = 0
                    df_time_series['e_c'] = 0
                    df_time_series['ah_d'] = 0
                    df_time_series['e_d'] = 0
                    df_time_series['cell_id'] = cell_id
                    df_time_series['cycle_index'] = 0
                    df_time_series['cycle_time'] = 0

                    if df_tmerge.empty:
                        df_tmerge = df_time_series
                    else:
                        df_tmerge = df_tmerge.append(df_time_series, ignore_index=True)

    return df_tmerge


# import data from Arbin-generated Excel files
def read_save_timeseries_arbin(cell_id, file_path, engine, conn):

    # the importer can read Excel worksheets with the Channel number from Arbin files.
    # it assumes column names generated by the Arbin:
    # Cycle_Index -> cycle_index
    # Test_Time(s) -> test_time
    # Current(A) -> i
    # Voltage(V) -> v
    # Date_Time -> date_time

    logging.info('adding files')

    listOfFiles = glob.glob(file_path + '*.xls*')

    for i in range(len(listOfFiles)):
        listOfFiles[i] = listOfFiles[i].replace(file_path[:-1], '')

    logging.info('list of files to add: ' + str(listOfFiles))

    df_file = pd.DataFrame(listOfFiles, columns=['filename'])

    df_file.sort_values(by=['filename'], inplace=True)

    if df_file.empty:
        return

    df_file['cell_id'] = cell_id

    df_tmerge = pd.DataFrame()

    start_time = time.time()

    cycle_index_max = 0

    sheetnames = buffered_sheetnames(cell_id, conn)

    # Loop through all the Excel test files
    for ind in df_file.index:

        filename = df_file['filename'][ind]
        cellpath = file_path + filename
        timeseries = ""

        logging.info('processing file: ' + filename)

        if os.path.exists(cellpath):
            df_cell = pd.ExcelFile(cellpath)
            # Find the time series sheet in the excel file

            for k in df_cell.sheet_names:

                unread_sheet = True
                sheetname = filename + "|" + k

                try:
                    sheetnames.index(sheetname)
                    print("found:" + sheetname)
                    unread_sheet = False
                except ValueError:
                    print("not found:" + sheetname)

                if "hannel" in k and  k != "Channel_Chart" and unread_sheet:
                    logging.info("file: " + filename + " sheet:" + str(k))
                    timeseries = k

                    df_time_series_file = pd.read_excel(df_cell, sheet_name=timeseries)

                    df_time_series = pd.DataFrame()

                    try:

                        df_time_series['cycle_index'] = df_time_series_file['Cycle_Index']
                        df_time_series['test_time'] = df_time_series_file['Test_Time(s)']
                        df_time_series['i'] = df_time_series_file['Current(A)']
                        df_time_series['v'] = df_time_series_file['Voltage(V)']
                        df_time_series['date_time'] = df_time_series_file['Date_Time']
                        df_time_series['cell_id'] = cell_id
                        df_time_series['sheetname'] = filename + "|" + timeseries

                        cycle_index_file_max = df_time_series.cycle_index.max()

                        if cycle_index_file_max > cycle_index_max:
                            cycle_index_max = cycle_index_file_max

                        print('saving sheet: ' + timeseries + ' with max cycle: ' +str(cycle_index_file_max))

                        df_time_series.to_sql('cycle_timeseries_buffer', con=engine, if_exists='append', chunksize=1000, index=False)

                        print("saved=" + timeseries + " time: " + str(time.time() - start_time))

                        start_time = time.time()

                    except KeyError as e:
                        print("I got a KeyError - reason " + str(e))
                        print("processing:" + timeseries + " time: " + str(time.time() - start_time))
                        start_time = time.time()

    return cycle_index_max


# import data from generic csv files
def read_save_timeseries_json(cell_id, file_path, engine, conn):

    # the importer can read Excel worksheets with the Channel number from Arbin files.
    # it assumes column names generated by the Arbin:
    # Cycle_Index -> cycle_index
    # Test_Time(s) -> test_time
    # Current(A) -> i
    # Voltage(V) -> v
    # Date_Time -> date_time

    logging.info('adding files')

    print("path: " + file_path)

    listOfFiles = glob.glob(file_path + '*.json*')

    print("files:" + str(listOfFiles))

    for i in range(len(listOfFiles)):
        listOfFiles[i] = listOfFiles[i].replace(file_path[:-1], '')

    logging.info('list of files to add: ' + str(listOfFiles))

    df_file = pd.DataFrame(listOfFiles, columns=['filename'])

    df_file.sort_values(by=['filename'], inplace=True)

    if df_file.empty:
        return

    df_file['cell_id'] = cell_id

    df_tmerge = pd.DataFrame()

    start_time = time.time()

    cycle_index_max = 0

    # Loop through all the Excel test files
    for ind in df_file.index:

        filename = df_file['filename'][ind]
        cellpath = file_path + filename
        timeseries = ""

        logging.info('processing file: ' + filename)

        if os.path.exists(cellpath):
            df_time_series_file = pd.read_json(cellpath)
            # Find the time series sheet in the excel file

            df_time_series = pd.DataFrame()

            try:
                df_time_series['cycle_index'] = df_time_series_file['Cycle number']
                df_time_series['test_time'] = df_time_series_file['Time [s]']
                df_time_series['i'] = df_time_series_file['Current [mA]']/1000
                df_time_series['v'] = df_time_series_file['Voltage [V]']
                #df_time_series['date_time'] = df_time_series_file['Date_Time']
                df_time_series['cell_id'] = cell_id
                df_time_series['sheetname'] = filename

                cycle_index_file_max = df_time_series.cycle_index.max()

                print('saving sheet: ' + timeseries + ' with max cycle: ' +str(cycle_index_file_max))

                df_time_series.to_sql('cycle_timeseries_buffer', con=engine, if_exists='append', chunksize=1000, index=False)

                print("saved=" + filename + " time: " + str(time.time() - start_time))

                start_time = time.time()

            except KeyError as e:
                print("I got a KeyError - reason " + str(e))
                print("processing:" + timeseries + " time: " + str(time.time() - start_time))
                start_time = time.time()

    return cycle_index_max


# import data from generic csv files
def read_save_timeseries_generic(cell_id, file_path, engine, conn):

    # the importer can read Excel worksheets with the Channel number from Arbin files.
    # it assumes column names generated by the Arbin:
    # Cycle_Index -> cycle_index
    # Test_Time(s) -> test_time
    # Current(A) -> i
    # Voltage(V) -> v
    # Date_Time -> date_time

    logging.info('adding files')

    print("path: " + file_path)

    listOfFiles = glob.glob(file_path + '*.csv*')

    print("files:" + str(listOfFiles))

    for i in range(len(listOfFiles)):
        listOfFiles[i] = listOfFiles[i].replace(file_path[:-1], '')

    logging.info('list of files to add: ' + str(listOfFiles))

    df_file = pd.DataFrame(listOfFiles, columns=['filename'])

    df_file.sort_values(by=['filename'], inplace=True)

    if df_file.empty:
        return

    df_file['cell_id'] = cell_id

    df_tmerge = pd.DataFrame()

    start_time = time.time()

    cycle_index_max = 0

    # Loop through all the Excel test files
    for ind in df_file.index:

        filename = df_file['filename'][ind]
        cellpath = file_path + filename
        timeseries = ""

        logging.info('processing file: ' + filename)

        if os.path.exists(cellpath):
            df_time_series_file = pd.read_csv(cellpath)
            # Find the time series sheet in the excel file

            df_time_series = pd.DataFrame()

            try:
                df_time_series['cycle_index'] = df_time_series_file['Cycle number']
                df_time_series['test_time'] = df_time_series_file['Time [s]']
                df_time_series['i'] = df_time_series_file['Current [mA]']/1000
                df_time_series['v'] = df_time_series_file['Voltage [V]']
                #df_time_series['date_time'] = df_time_series_file['Date_Time']
                df_time_series['cell_id'] = cell_id
                df_time_series['sheetname'] = filename

                cycle_index_file_max = df_time_series.cycle_index.max()

                print('saving sheet: ' + timeseries + ' with max cycle: ' +str(cycle_index_file_max))

                df_time_series.to_sql('cycle_timeseries_buffer', con=engine, if_exists='append', chunksize=1000, index=False)

                print("saved=" + filename + " time: " + str(time.time() - start_time))

                start_time = time.time()

            except KeyError as e:
                print("I got a KeyError - reason " + str(e))
                print("processing:" + timeseries + " time: " + str(time.time() - start_time))
                start_time = time.time()

    return cycle_index_max


# import data from the voltaiq csv timeseries files
def read_save_timeseries_voltaiq(cell_id, file_path, engine, conn):

    # the importer can read Excel worksheets with the Channel number from Arbin files.
    # it assumes column names generated by the Arbin:
    # Cycle_Index -> cycle_index
    # Test_Time(s) -> test_time
    # Current(A) -> i
    # Voltage(V) -> v
    # Date_Time -> date_time

    logging.info('adding files')

    print("path: " + file_path)

    listOfFiles = glob.glob(file_path + '*.csv*')

    print("files:" + str(listOfFiles))

    for i in range(len(listOfFiles)):
        listOfFiles[i] = listOfFiles[i].replace(file_path[:-1], '')

    logging.info('list of files to add: ' + str(listOfFiles))

    df_file = pd.DataFrame(listOfFiles, columns=['filename'])

    df_file.sort_values(by=['filename'], inplace=True)

    if df_file.empty:
        return

    df_file['cell_id'] = cell_id

    df_tmerge = pd.DataFrame()

    start_time = time.time()

    cycle_index_max = 0

    # Loop through all the Excel test files
    for ind in df_file.index:

        filename = df_file['filename'][ind]
        cellpath = file_path + filename
        timeseries = ""

        logging.info('processing file: ' + filename)

        if os.path.exists(cellpath):
            df_time_series_file = pd.read_csv(cellpath)
            # Find the time series sheet in the excel file

            df_time_series = pd.DataFrame()

            try:
                df_time_series['cycle_index'] = df_time_series_file['Cycle Number']
                df_time_series['test_time'] = df_time_series_file['Test Time (s)']
                df_time_series['i'] = df_time_series_file['Current (A)']
                df_time_series['v'] = df_time_series_file['Potential (V)']
                df_time_series['date_time'] = df_time_series_file['[Maccor] Datapoint Time']
                df_time_series['cell_id'] = cell_id
                df_time_series['sheetname'] = filename

                cycle_index_file_max = df_time_series.cycle_index.max()

                print('saving sheet: ' + timeseries + ' with max cycle: ' +str(cycle_index_file_max))

                df_time_series.to_sql('cycle_timeseries_buffer', con=engine, if_exists='append', chunksize=1000, index=False)

                print("saved=" + filename + " time: " + str(time.time() - start_time))

                start_time = time.time()

            except KeyError as e:
                print("I got a KeyError - reason " + str(e))
                print("processing:" + timeseries + " time: " + str(time.time() - start_time))
                start_time = time.time()

    return cycle_index_max


# sort data imported to insure cycle index and test times are correctly calculated
def sort_timeseries(df_tmerge):
    # Arrange the data by date time first, then by test time
    # Rebuild Cycle Index and test time to increment from file to file
    # This method does not depend on data from a specific testers

    logging.info('sorting timeseries dataframe')

    if not df_tmerge.empty:

        df_t = df_tmerge.sort_values(by=['date_time'])
        df_t = df_t.reset_index(drop=True)

        cycles = df_t[["cycle_index_file", "cycle_index", "filename", "test_time"]].to_numpy()

        max_cycle = 1
        past_index = 1
        max_time = 0
        last_file = ""
        delta_t = 0
        start = 0

        for x in cycles:

            if start == 0:
                last_file = x[2]
                start += 1

            if x[2] != last_file:
                delta_t = max_time
                x[3] += delta_t
                last_file = x[2]
            else:
                x[3] += delta_t
                max_time = x[3]
                last_file = x[2]

            if x[0] < max_cycle:

                if past_index == x[0]:
                    past_index = x[0]
                    x[1] = max_cycle
                else:
                    past_index = x[0]
                    x[1] = max_cycle + 1
                    max_cycle = x[1]

            else:
                past_index = x[0]
                max_cycle = x[0]
                x[1] = x[0]

        df_tmp = pd.DataFrame(data=cycles[:, [1]], columns=["cycle_index"])
        df_t['cycle_index'] = df_tmp['cycle_index']

        df_tmp = pd.DataFrame(data=cycles[:, [3]], columns=["test_time"])
        df_t['test_time'] = pd.to_numeric(df_tmp['test_time'])

        df_ts = df_t.sort_values(by=['test_time'])

        # Remove quantities only needed to tag files
        df_ts.drop('filename', axis=1, inplace=True)
        df_ts.drop('cycle_index_file', axis=1, inplace=True)

        return df_ts


# Build cell metadata
def populate_cycle_metadata(df_c_md):

    # Build cell metadata
    df_cell_md = pd.DataFrame()
    df_cell_md['cell_id'] = [df_c_md['cell_id']]
    df_cell_md['anode'] = [df_c_md['anode']]
    df_cell_md['cathode'] = [df_c_md['cathode']]
    df_cell_md['source'] = [df_c_md['source']]
    df_cell_md['ah'] = [df_c_md['ah']]
    df_cell_md['form_factor'] = [df_c_md['form_factor']]
    df_cell_md['test'] = [df_c_md['test']]
    df_cell_md['tester'] = [df_c_md['tester']]
    
    # Build cycle metadata
    df_cycle_md = pd.DataFrame()
    df_cycle_md['cell_id'] = [df_c_md['cell_id']]
    df_cycle_md['crate_c'] = [df_c_md['crate_c']]
    df_cycle_md['crate_d'] = [df_c_md['crate_d']]
    df_cycle_md['soc_max'] = [df_c_md['soc_max']]
    df_cycle_md['soc_min'] = [df_c_md['soc_min']]
    df_cycle_md['temperature'] = [df_c_md['temperature']]

    return df_cell_md, df_cycle_md


# Build cell metadata
def populate_abuse_metadata(df_c_md):

    # Build cell metadata
    df_cell_md = pd.DataFrame()
    df_cell_md['cell_id'] = [df_c_md['cell_id']]
    df_cell_md['anode'] = [df_c_md['anode']]
    df_cell_md['cathode'] = [df_c_md['cathode']]
    df_cell_md['source'] = [df_c_md['source']]
    df_cell_md['ah'] = [df_c_md['ah']]
    df_cell_md['form_factor'] = [df_c_md['form_factor']]
    df_cell_md['test'] = [df_c_md['test']]
    df_cell_md['tester'] = [df_c_md['tester']]
    df_cell_md['weight'] = [df_c_md['weight']]
    df_cell_md['dimensions'] = [df_c_md['dimensions']]
    
    # Build cycle metadata
    df_abuse_md = pd.DataFrame()
    df_abuse_md['cell_id'] = [df_c_md['cell_id']]
    df_abuse_md['v_init'] = [df_c_md['v_init']]
    df_abuse_md['indentor'] = [df_c_md['indentor']]
    df_abuse_md['nail_speed'] = [df_c_md['nail_speed']]
    df_abuse_md['soc'] = [df_c_md['soc']]

    return df_cell_md, df_abuse_md


# direct_query
def execute_query(sql_str, conn):

    # this method will delete data for a cell_id. Use with caution as there is no undo
    db_conn = psycopg2.connect(conn)
    curs = db_conn.cursor()
    curs.execute(sql_str)
    db_conn.commit()
    curs.close()
    db_conn.close()

    return


# delete records (call with caution)
def delete_records(cell_id, conn):
    # this method will delete data for a cell_id. Use with caution as there is no undo
    db_conn = psycopg2.connect(conn)
    curs = db_conn.cursor()

    curs.execute("delete from timeseries_data where cell_id='" + cell_id + "'")
    curs.execute("delete from cycle_data where cell_id='" + cell_id + "'")
    curs.execute("delete from cell_metadata where cell_id='" + cell_id + "'")
    curs.execute("delete from cycle_metadata where cell_id='" + cell_id + "'")

    db_conn.commit()
    curs.close()
    db_conn.close()

    return


# delete records (call with caution)
def clear_buffer(cell_id, conn):
    # this method will delete data for a cell_id. Use with caution as there is no undo
    db_conn = psycopg2.connect(conn)
    curs = db_conn.cursor()

    curs.execute("delete from cycle_timeseries_buffer where cell_id='" + cell_id + "'")

    db_conn.commit()
    curs.close()
    db_conn.close()

    return


def set_cell_status(cell_id, status, conn):

    sql_str = "update cell_metadata set status = '" + status + "' where cell_id = '" + cell_id + "'"

    db_conn = psycopg2.connect(conn)
    curs = db_conn.cursor()
    curs.execute(sql_str)
    db_conn.commit()
    curs.close()
    db_conn.close()

    return


def get_cycle_index_max(cell_id,conn):


    sql_str = "select max(cycle_index)::int as max_cycles from cycle_timeseries_buffer where cell_id = '" + cell_id + "'"

    db_conn = psycopg2.connect(conn)
    curs = db_conn.cursor()
    curs.execute(sql_str)
    db_conn.commit()

    record = [r[0] for r in curs.fetchall()]

    if record[0]: 
        # bad valerio -- very bad! you are a very bad man!!
        cycle_index_max = record[0]
    else:
        cycle_index_max = 0

    curs.close()
    db_conn.close()

    print("buffer cycle_index_max: " + str(cycle_index_max))

    return cycle_index_max


def get_cycle_stats_index_max(cell_id,conn):


    sql_str = "select max(cycle_index)::int as max_cycles from cycle_stats where cell_id = '" + cell_id + "'"

    db_conn = psycopg2.connect(conn)
    curs = db_conn.cursor()
    curs.execute(sql_str)
    db_conn.commit()

    record = [r[0] for r in curs.fetchall()]

    if record[0]: 
        # bad valerio -- very bad! you are a very bad man!!
        cycle_index_max = record[0]
    else:
        cycle_index_max = 0

    curs.close()
    db_conn.close()

    print("stats cycle_index_max: " + str(cycle_index_max))

    return cycle_index_max


def check_cell_status(cell_id,conn):

    status = 'new'

    sql_str = "select * from cell_metadata where cell_id = '" + cell_id + "'"

    db_conn = psycopg2.connect(conn)
    curs = db_conn.cursor()
    curs.execute(sql_str)
    db_conn.commit()

    record = curs.fetchall()

    if record: 
        # bad valerio -- very bad! you are a very bad man!!
        status = record[0][8]
    else:
        status = 'new'

    curs.close()
    db_conn.close()

    return status


def buffered_sheetnames(cell_id, conn):

    sql_str = "select distinct sheetname from cycle_timeseries_buffer where cell_id = '" + cell_id + "'"

    db_conn = psycopg2.connect(conn)
    curs = db_conn.cursor()
    curs.execute(sql_str)
    db_conn.commit()

    record = [r[0] for r in curs.fetchall()]

    curs.close()
    db_conn.close()

    sheetnames=[]

    if record:
        
        print("record: " + str(record))
        sheetnames = record
            
    else:
        print("empty list")

    return sheetnames


# calculate statistics for abuse test
def calc_abuse_stats(df_t, df_test_md):

    for _ in df_t.index:
        df_t['norm_d'] = df_t.iloc[0:, df_t.columns.get_loc('axial_d')] - df_t['axial_d'][0]
        df_t['strain'] = df_t.iloc[0:, df_t.columns.get_loc('norm_d')] / df_test_md['indentor']

    return df_t


# calculate statistics for abuse test
def read_ornlabuse(file_path, cell_id):

    excels = glob.glob(file_path + '*.xls*')

    #df_ts = pd.DataFrame()
    #df_ts['test_time'] = df_ts_file['Test Time [s]']
    #df_ts['axial_d'] = df_ts_file['Displacement [mm]']
    #df_ts['axial_f'] = df_ts_file['Penetrator Force [mm]']
    #df_ts['v'] = df_ts_file['vCell [V]']
    #df_ts['ambient_temperature'] = df_ts_file['tAmbient [C]']
    #df_ts['top_indent_temperature'] = df_ts_file['TC1 near positive terminal [C]']
    #df_ts['top_back_temperature'] = df_ts_file['TC2 near negative terminal [C]']
    #df_ts['left_bottom_temperature'] = df_ts_file['TC3 bottom - bottom [C]']
    #df_ts['right_bottom_temperature'] = df_ts_file['TC4 bottom - top [C]']
    #df_ts['above_punch_temperature'] = df_ts_file['TC5 above punch [C]']
    #df_ts['below_punch_temperature'] = df_ts_file['TC6 below punch [C]']

    df_tmerge = pd.DataFrame()
    for excel in excels:
        if '~$' in excel:
            continue
        df_ts_file = pd.read_excel(
            excel, sheet_name='Sheet1')  # dictionary of sheets

        print(df_ts_file.columns)

        df_ts_a = pd.DataFrame()
        df_ts_a['test_time'] = df_ts_file['Time (second)']
        df_ts_a['axial_d'] = df_ts_file['Displacement (mm)']
        df_ts_a['v'] = df_ts_file['Voltage (V)']
        df_ts_a['axial_f'] = df_ts_file['Penetrator Force (N)']
        df_ts_a['load'] = df_ts_file['Load (lb)']

        df_ts_a['top_indent_temperature'] = 0
        df_ts_a['top_back_temperature'] = 0
        df_ts_a['left_bottom_temperature'] = 0
        df_ts_a['right_bottom_temperature'] = 0
        df_ts_a['above_punch_temperature'] = 0
        df_ts_a['below_punch_temperature'] = 0

        df_ts_b = pd.DataFrame()
        df_ts_b['test_time'] = df_ts_file['Time (sec) ']
        df_ts_b['axial_d'] = 0
        df_ts_b['v'] = 0
        df_ts_b['axial_f'] = 0

        if 'TC1 top indent [C]' in df_ts_file:
            print("6 cols" + cell_id) 
            df_ts_b['top_indent_temperature'] = df_ts_file['TC1 top indent [C]']
            df_ts_b['top_back_temperature'] = df_ts_file['TC2 top back [C]']
            df_ts_b['left_bottom_temperature'] = df_ts_file['TC3 bottom back [C]']
            df_ts_b['right_bottom_temperature'] = df_ts_file['TC4 bottom indent [C]']
            df_ts_b['above_punch_temperature'] = df_ts_file['TC5 above punch [C]']
            df_ts_b['below_punch_temperature'] = df_ts_file['TC6 below punch [C]']
        elif 'TC1 (°C)' in df_ts_file:
            print("1 col:" + cell_id)
            df_ts_b['below_punch_temperature'] = df_ts_file['TC1 (°C)']

        if df_tmerge.empty:
            df_tmerge = df_ts_a
            df_tmerge = df_tmerge.append(df_ts_b, ignore_index=True)
        else:
            df_tmerge = df_tmerge.append(df_ts_a, ignore_index=True)
            df_tmerge = df_tmerge.append(df_ts_b, ignore_index=True)

    df_tmerge['cell_id'] = cell_id

    return df_tmerge


# read the abuse excel files from SNL
def read_snlabuse(file_path, cell_id):

    excels = glob.glob(file_path + '*.xls*')

    df_tmerge = pd.DataFrame()

    for excel in excels:
        if '~$' in excel:
            continue
        df_ts_file = pd.read_excel(
            excel, sheet_name='Sheet1')  # dictionary of sheets

        df_ts = pd.DataFrame()
        df_ts['test_time'] = df_ts_file['Test Time [s]']
        df_ts['axial_d'] = df_ts_file['Displacement [mm]']
        df_ts['axial_f'] = df_ts_file['Penetrator Force [mm]']
        df_ts['v'] = df_ts_file['vCell [V]']
        df_ts['ambient_temperature'] = df_ts_file['tAmbient [C]']
        df_ts['top_indent_temperature'] = df_ts_file['TC1 near positive terminal [C]']
        df_ts['top_back_temperature'] = df_ts_file['TC2 near negative terminal [C]']
        df_ts['left_bottom_temperature'] = df_ts_file['TC3 bottom - bottom [C]']
        df_ts['right_bottom_temperature'] = df_ts_file['TC4 bottom - top [C]']
        df_ts['above_punch_temperature'] = df_ts_file['TC5 above punch [C]']
        df_ts['below_punch_temperature'] = df_ts_file['TC6 below punch [C]']

        if df_tmerge.empty:
            df_tmerge = df_ts
        else:
            df_tmerge = df_tmerge.append(df_ts, ignore_index=True)

    df_tmerge['cell_id'] = cell_id

    return df_tmerge


# add cells to the database
def add_ts_md_abuse(cell_list, conn, save, plot, path, slash):
    # The importer expects an Excel file with cell and test information
    # The file contains one row per cell

    logging.info('add cells')
    df_excel = pd.read_excel(cell_list)

    # Process one cell at the time
    for ind in df_excel.index:

        cell_id = df_excel['cell_id'][ind]
        file_id = df_excel['file_id'][ind]
        tester = df_excel['tester'][ind]

        logging.info("add file: " + file_id + " cell: " + cell_id)

        df_tmp = df_excel.iloc[ind]

        print(df_tmp)

        df_cell_md, df_abuse_md = populate_abuse_metadata(df_tmp)

        engine = create_engine(conn)

        logging.info('save cell metadata')
        df_cell_md.to_sql('cell_metadata', con=engine, if_exists='append', chunksize=1000, index=False)
        logging.info('save cycle metadata')
        df_abuse_md.to_sql('abuse_metadata', con=engine, if_exists='append', chunksize=1000, index=False)

        file_path = path + file_id + slash

        df_abuse_ts = pd.DataFrame()   

        print("tester=" + tester)

        if tester=='ORNL-Servo-Motor':
            print("ORNL CELL=" + cell_id)
            df_abuse_ts = read_ornlabuse(file_path, cell_id)
        if tester=='SNL-Hydraulic':
            print("SNL CELL=" + cell_id)
            df_abuse_ts = read_snlabuse(file_path, cell_id)
       
        if not df_abuse_ts.empty:
            df_abuse_ts = calc_abuse_stats(df_abuse_ts, df_abuse_md)
            df_abuse_ts.to_sql('abuse_timeseries', con=engine, if_exists='append', chunksize=1000, index=False)
            

# add cells to the database
def add_ts_md_cycle(cell_list, conn, save, plot, path, slash):
    # The importer expects an Excel file with cell and test information
    # The file contains one row per cell

    logging.info('add cells')
    df_excel = pd.read_excel(cell_list)

    # Process one cell at the time
    for ind in df_excel.index:

        cell_id = df_excel['cell_id'][ind]
        file_id = df_excel['file_id'][ind]
        tester = df_excel['tester'][ind]

        logging.info("add file: " + file_id + " cell: " + cell_id)

        df_tmp = df_excel.iloc[ind]

        print(df_tmp)

        df_cell_md, df_cycle_md = populate_cycle_metadata(df_tmp)

        engine = create_engine(conn)

        # check if the cell is already there and report status

        print(conn)
        status = check_cell_status(cell_id, conn)

        if status=="completed":
            print("skip cell_id: " + cell_id)

        if status=='new': 

            logging.info('save cell metadata')
            df_cell_md.to_sql('cell_metadata', con=engine, if_exists='append', chunksize=1000, index=False)
            logging.info('save cycle metadata')
            df_cycle_md.to_sql('cycle_metadata', con=engine, if_exists='append', chunksize=1000, index=False)

            status = 'buffering'

            set_cell_status(cell_id, status, conn)
    
        if status=='buffering':

            print("buffering cell_id: " + cell_id)
            
            # Modify this method to add more testers
            file_path = path + file_id + slash

            # importer specific to the Arbin file (TODO)
            cycle_index_max = 1

            print("select import")
            if tester == 'arbin':
                cycle_index_max = read_save_timeseries_arbin(cell_id, file_path, engine, conn) 

            if tester == 'json':
                cycle_index_max = read_save_timeseries_json(cell_id, file_path, engine, conn) 
            
            if tester == 'generic':
                print("start import")
                cycle_index_max = read_save_timeseries_generic(cell_id, file_path, engine, conn) 
            
            if tester == 'voltaiq':
                print("start import")
                cycle_index_max = read_save_timeseries_voltaiq(cell_id, file_path, engine, conn) 
            
            status = "processing"

            set_cell_status(cell_id, status, conn)

        if status == 'processing':

            # read the data back in chunks.
            block_size = 30

            cycle_index_max = get_cycle_index_max(cell_id, conn)
            cycle_stats_index_max = get_cycle_stats_index_max(cell_id, conn)

            print("max cycle: " + str(cycle_index_max))

            start_cycle = 1
            start_time = time.time()

            for i in range(cycle_index_max+1):
                
                if (i-1) % block_size == 0 and i > 0 and i>cycle_stats_index_max:

                    start_cycle = i
                    end_cycle = start_cycle + block_size - 1

                    sql_cell =  " cell_id='" + cell_id + "'" 
                    sql_cycle = " and cycle_index>=" + str(start_cycle) + " and cycle_index<=" + str(end_cycle)
                    sql_str = "select * from cycle_timeseries_buffer where " + sql_cell + sql_cycle + " order by test_time"

                    print(sql_str)
                    df_ts = pd.read_sql(sql_str, conn)

                    df_ts.drop('sheetname', axis=1, inplace=True)

                    if not df_ts.empty:
                        start_time = time.time()
                        df_cycle_stats, df_cycle_timeseries = calc_stats(df_ts)
                        print("calc_stats time: " + str(time.time() - start_time))
                        logging.info("calc_stats time: " + str(time.time() - start_time))

                        start_time = time.time()
                        df_cycle_stats.to_sql('cycle_stats', con=engine, if_exists='append', chunksize=1000, index=False)
                        print("save stats time: " + str(time.time() - start_time))
                        logging.info("save stats time: " + str(time.time() - start_time))

                        start_time = time.time()
                        df_cycle_timeseries.to_sql('cycle_timeseries', con=engine, if_exists='append', chunksize=1000, index=False)
                        print("save timeseries time: " + str(time.time() - start_time))
                        logging.info("save timeseries time: " + str(time.time() - start_time))

            status='completed'

            set_cell_status(cell_id, status, conn)

            clear_buffer(cell_id, conn)


# generate csv files with cycle data
def generate_cycle_data(cell_id, conn, path):

    # generate cycle data in csv format

    logging.info('export cell cycle data to csv files')

    sql_str = """select 
        cycle_index as "Cycle_Index", 
        round(test_time,3) as "Test_Time (s)",
        round(i_min,3) as "Min_Current (A)", 
        round(i_max,3) as "Max_Current (A)", 
        round(v_min,3) as "Min_Voltage (V)", 
        round(v_max,3) as "Max_Voltage (V)", 
        round(ah_c,3) as "Charge_Capacity (Ah)", 
        round(ah_d,3) as "Discharge_Capacity (Ah)", 
        round(e_c,3) as "Charge_Energy (Wh)", 
        round(e_d,3)  as "Discharge_Energy (Wh)" 
      from cycle_stats where cell_id='""" + cell_id + """' order by cycle_index"""

    print(sql_str)

    df = pd.read_sql(sql_str, conn)

    cell_id_to_file = cell_id.replace(r'/', '-')
    csv = path + cell_id_to_file + '_cycle_data.csv'
    df.to_csv(csv, encoding='utf-8', index=False)


def generate_timeseries_data(cell_id, conn, path):

    # generate timeseries data

    logging.info('export cell timeseries data to csv files')

    status = 'exporting'

    set_cell_status(cell_id, status, conn)

    block_size = 30

    cycle_index_max = get_cycle_index_max(cell_id, conn)

    print("max cycle: " + str(cycle_index_max))

    start_cycle = 1
    create_file = True 

    for i in range(cycle_index_max+1):
                
        if (i-1) % block_size == 0 and i > 0:

            start_cycle = i
            end_cycle = start_cycle + block_size - 1

            sql_cell =  " cell_id='" + cell_id + "'" 
            sql_cycle = " and cycle_index>=" + str(start_cycle) + " and cycle_index<=" + str(end_cycle) + " "

            sql_str = """select 
                date_time as "Date_Time",
                round(test_time,3) as "Test_Time (s)", 
                cycle_index as "Cycle_Index", 
                round(i,3) as "Current (A)",
                round(v,3) as "Voltage (V)",
                round(ah_c,3) as "Charge_Capacity (Ah)", 
                round(ah_d,3) as "Discharge_Capacity (Ah)", 
                round(e_c,3) as "Charge_Energy (Wh)", 
                round(e_d,3) as "Discharge_Energy (Wh)",
                round(env_temperature,3) as "Environment_Temperature (C)",
                round(cell_temperature,3) as "Cell_Temperature (C)"
                from cycle_timeseries where """ + sql_cell + sql_cycle + """
                order by test_time"""

            print(sql_str)

            df = pd.read_sql(sql_str, conn)

            cell_id_to_file = cell_id.replace(r'/', '-')
            csv = path + cell_id_to_file + '_timeseries_data.csv'
            if create_file:
                df.to_csv(csv, encoding='utf-8', index=False)
                create_file = False
            else:
                df.to_csv(csv, mode='a', index=False, header=False)


# generate csv files with time series and cycle data
def export_cells(cell_list, conn, path):

    # export data from the cell list

    logging.info('export cell data to csv files')
    
    # Look for cells that need to be updated

    sql_str = "select * from cell_metadata where status = 'export' order by cell_id"
    print(sql_str)
    df_cells = pd.read_sql(sql_str, conn)

    engine = create_engine(conn)

    # Process one cell at the time
    for ind in df_cells.index:
        cell_id = df_cells['cell_id'][ind]
        print("cell_id=" + cell_id)

        generate_cycle_data(cell_id, conn, path)
        generate_timeseries_data(cell_id, conn, path)

        status='completed'

        set_cell_status(cell_id, status, conn)

    return;


# add new calculated quantities to cells previously imported, or update existing calculated statistics
def update_cells(conn, save, plot):

    logging.info('update cell data')

    # Look for cells that need to be updated

    sql_str = "select * from cell_metadata where status = 'update' order by cell_id"
    print(sql_str)
    df_cells = pd.read_sql(sql_str, conn)

    engine = create_engine(conn)

    # Process one cell at the time
    for ind in df_cells.index:

        cell_id = df_cells['cell_id'][ind]

        # read the data back in chunks.
        block_size = 30

        cycle_index_max = get_cycle_stats_index_max(cell_id, conn)

        print("cell_id=" + cell_id + " max cycle: " + str(cycle_index_max))

        start_cycle = 1
        start_time = time.time()

        ####for i in range(block_size+1):
        for i in range(cycle_index_max+1):

                
            if (i-1) % block_size == 0 and i > 0:

                start_cycle = i
                end_cycle = start_cycle + block_size - 1

                sql_cell =  " cell_id='" + cell_id + "'" 
                sql_cycle = " and cycle_index>=" + str(start_cycle) + " and cycle_index<=" + str(end_cycle)
                sql_str = "select * from cycle_timeseries where " + sql_cell + sql_cycle + " order by test_time"

                print(sql_str)
                df_ts = pd.read_sql(sql_str, conn)

                if not df_ts.empty:
                    start_time = time.time()
                    df_cycle_stats, df_cycle_timeseries = calc_stats(df_ts)
                    print("calc_stats time: " + str(time.time() - start_time))
                    logging.info("calc_stats time: " + str(time.time() - start_time))

                    start_time = time.time()

                    # remove old data before adding new data
                    sql_str = "delete from cycle_stats where " + sql_cell + sql_cycle
                    execute_query(sql_str,conn)

                    df_cycle_stats.to_sql('cycle_stats', con=engine, if_exists='append', chunksize=1000, index=False)
                    print("save stats time: " + str(time.time() - start_time))
                    logging.info("save stats time: " + str(time.time() - start_time))

                    start_time = time.time()
                    
                    # remove old data before adding new data
                    sql_str = "delete from cycle_timeseries where " + sql_cell + sql_cycle
                    execute_query(sql_str,conn)

                    df_cycle_timeseries.to_sql('cycle_timeseries', con=engine, if_exists='append', chunksize=1000, index=False)
                    print("save timeseries time: " + str(time.time() - start_time))
                    logging.info("save timeseries time: " + str(time.time() - start_time))



        status='completed'

        set_cell_status(cell_id, status, conn)

    return


def main(argv):

    # command line variables that can be used to run from an IDE without passing arguments
    mode = 'env'
    path = r'\\'

    # initializing the logger
    logging.basicConfig(format='%(asctime)s %(message)s', filename='blc-python.log', level=logging.DEBUG)
    logging.info('starting')

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

    # read database connection
    conn = ''
    try:
        env = yaml.safe_load(open('../env'))
        x = env.split(" ")
        for i in x:
            j = i.split("=")
            if j[0] == 'DATABASE_CONNECTION':
                conn =  j[1]
    except:
        print("Error opening env file:", sys.exc_info()[0])

    # read configuration values
    data = yaml.safe_load(open('battery-blc-library.yaml'))

    plot = data['environment']['PLOT']
    save = data['environment']['SAVE']
    style = data['environment']['STYLE']
    
    logging.info('command line: ' + str(opts))
    logging.info('configuration: ' + str(data))

    # needed to maintain compatibility with windows machines
    if style == 'unix':
        slash = "/"
    elif style == 'windows':
        slash = r'\\'

    # Mode of operation
    if mode == 'add':
        if test == 'cycle':
            add_ts_md_cycle(path + "cell_list.xlsx", conn, save, plot, path, slash)
        if test == 'abuse':
            add_ts_md_abuse(path + "cell_list.xlsx", conn, save, plot, path, slash)
        logging.info('Done adding files')
    elif mode == 'update':
        update_cells(conn, save, plot)
        logging.info('Done updating files')
    elif mode == 'export':
        export_cells(path, conn, path)
        logging.info('Done exporting files')
    elif mode == 'env':
        logging.info('printing environment variables only')
        print("style: " + style)
        print("  -slash: " + slash)
        print("  -path: " + path)
        print("conn: " + conn)
        print("plot: " + str(plot))
        print("save: " + str(save))
    else:
        print('data_import.py -m <mode> -p <path>')


if __name__ == "__main__":
   main(sys.argv[1:])



