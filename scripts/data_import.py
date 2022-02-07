#!/usr/bin/env python
# coding: utf-8
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
    last_i_c = 0
    last_v_c = 0
    last_i_d = 0
    last_v_d = 0
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
            if x[1] >= 0:
                x[3] = (x[0]-last_time)*(x[1]+last_i_c)*0.5+last_ah_c
                x[4] = (x[0]-last_time)*(x[1]+last_i_c)*0.5*(x[2]+last_v_c)*0.5+last_e_c
                last_i_c = x[1]
                last_v_c = x[2]
                last_ah_c = x[3]
                last_e_c = x[4]

            if x[1] <= 0:
                x[5] = (x[0] - last_time) * (x[1] + last_i_d) * 0.5 + last_ah_d
                if x[5] == 0:
                    print("x5=0:" + str(x[5]) + " last_ah_d: " + str(last_ah_d))
                if last_ah_d == 0:
                    print("x5:" + str(x[5]) + " last_ah_d=0: " + str(last_ah_d))
                x[6] = (x[0] - last_time) * (x[1] + last_i_d) * 0.5 * (x[2] + last_v_d) * 0.5 + last_e_d
                last_i_d = x[1]
                last_v_d = x[2]
                last_ah_d = x[5]
                last_e_d = x[6]

        x[7] = x[0] - initial_time
        last_time = x[0]


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


# calculate statistics for abuse test
def calc_abuse_stats(df_t, df_cell_md, df_test_md):

    for ind in df_t.index:
        df_t["norm_d"] = df_t.iloc[0:, df_t.columns.get_loc("axial_d")] - df_t['axial_d'][0]
        df_t['strain'] = df_t.iloc[0:, df_t.columns.get_loc("norm_d")] / df_test_md['thickness']

    return df_t


# calculate statistics cycle test
def calc_cycle_stats(df_t, df_cell_md, df_test_md):

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

                print("cycle index=" + str(x))
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


# remove metadata entries from MACCOR files
def prepare_maccor_file(cellpath):

    a_file = open(cellpath, "r", encoding='utf8', errors='ignore')
    lines = a_file.readlines()
    a_file.close()

    #a_file = open(cellpath, "rb").read().decode('ISO-8859-1')
    #print(a_file)
    #lines = a_file.readlines()
    #lines = a_file
    #a_file.close()

    cellpath_df = cellpath + "_df"

    new_file = open(cellpath_df, "w")
    for line in lines:
        forget_line = line.startswith("Today") or line.startswith("Filename") or line.startswith("Procedure") or line.startswith("Comment")

        if not forget_line:
            new_file.write(line)

    new_file.close()

    return cellpath_df


# identify the sign of the current for a MACCOR file
def signedCurrent(x, y):
    if x == "D":
        return -y
    else:
        return y


# Read the abuse excel file from ORNL
def read_ornlabuse(cell_id, file_path):

    excels = glob.glob(file_path + '*.xls*')

    df_tmerge = pd.DataFrame()

    for excel in excels:
        if '~$' in excel:
            continue
        df_time_series_file = pd.read_excel(excel, sheet_name='data')  # dictionary of sheets

        df_time_series_a = pd.DataFrame()
        df_time_series_a['test_time'] = df_time_series_file['Running Time']
        df_time_series_a['axial_d'] = df_time_series_file['Axial Displacement']
        df_time_series_a['v'] = df_time_series_file['Analog 1']
        df_time_series_a['axial_f'] = df_time_series_file['Axial Force']
        df_time_series_a['pos_terminal_temperature'] = 0
        df_time_series_a['neg_terminal_temperature'] = 0
        df_time_series_a['left_bottom_temperature'] = 0
        df_time_series_a['right_bottom_temperature'] = 0
        df_time_series_a['above_punch_temperature'] = 0
        df_time_series_a['below_punch_temperature'] = 0
        df_time_series_a['cell_id'] = cell_id

        df_time_series_b = pd.DataFrame()
        df_time_series_b['test_time'] = df_time_series_file['Running Time 1']
        df_time_series_b['axial_d'] = 0
        df_time_series_b['v'] = 0
        df_time_series_b['axial_f'] = 0
        df_time_series_b['pos_terminal_temperature'] = df_time_series_file['TC 01']
        df_time_series_b['neg_terminal_temperature'] = df_time_series_file['TC 02']
        df_time_series_b['left_bottom_temperature'] = df_time_series_file['TC 03']
        df_time_series_b['right_bottom_temperature'] = df_time_series_file['TC 04']
        df_time_series_b['above_punch_temperature'] = df_time_series_file['TC 05']
        df_time_series_b['below_punch_temperature'] = df_time_series_file['TC 06']
        df_time_series_b['cell_id'] = cell_id

        if df_tmerge.empty:
            df_tmerge = df_time_series_a
            df_tmerge = df_tmerge.append(df_time_series_b, ignore_index=True)
        else:
            df_tmerge = df_tmerge.append(df_time_series_a, ignore_index=True)
            df_tmerge = df_tmerge.append(df_time_series_b, ignore_index=True)

    return df_tmerge


# read the abuse excel files from SNL
def read_snlabuse(cell_id, file_path):

    excels = glob.glob(file_path + '*.xls*')

    df_tmerge = pd.DataFrame()

    for excel in excels:
        if '~$' in excel:
            continue
        df_time_series_file = pd.read_excel(excel, sheet_name='data')  # dictionary of sheets

        df_time_series = pd.DataFrame()
        df_time_series['test_time'] = df_time_series_file['Running Time']
        df_time_series['axial_d'] = df_time_series_file['Axial Displacement']
        df_time_series['axial_f'] = df_time_series_file['Axial Force']
        df_time_series['v'] = df_time_series_file['Analog 1']
        df_time_series['pos_terminal_temperature'] = df_time_series_file['TC 01']
        df_time_series['neg_terminal_temperature'] = df_time_series_file['TC 02']
        df_time_series['left_bottom_temperature'] = df_time_series_file['TC 03']
        df_time_series['right_bottom_temperature'] = df_time_series_file['TC 04']
        df_time_series['above_punch_temperature'] = df_time_series_file['TC 05']
        df_time_series['below_punch_temperature'] = df_time_series_file['TC 06']
        df_time_series['cell_id'] = cell_id

        if df_tmerge.empty:
            df_tmerge = df_time_series
        else:
            df_tmerge = df_tmerge.append(df_time_series, ignore_index=True)

    return df_tmerge


#import generic files: needs column mapping information in cell_list
def read_generic(cell_id, file_path, file_type, mapping):

    logging.info('adding files')

    listOfFiles = glob.glob(file_path + '*.' + file_type)

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

        logging.info('processing file: ' + filename)

        if os.path.exists(cellpath):

            if file_type == 'csv':
                df_cell = pd.read_csv(cellpath, sep=',')

            # Find the time series sheet in the excel file

            df_time_series_file = df_cell
            df_time_series = pd.DataFrame()
            column_list = mapping.split(",")

            file_col = 0
            for col in column_list:
                file_col_name = df_time_series_file.columns[file_col]
                df_time_series[col] = df_time_series_file[file_col_name]
                file_col += 1

            print(df_time_series.columns)

            df_time_series['date_time'] = pd.to_datetime(df_time_series['date_time'], format='%Y-%m-%d %H:%M:%S.%f')
            df_time_series['i'] = df_time_series['i'].apply(pd.to_numeric)
            df_time_series['v'] = df_time_series['v'].apply(pd.to_numeric)
            df_time_series['env_temperature'] = df_time_series['env_temperature'].apply(pd.to_numeric)
            df_time_series['test_time'] = df_time_series['date_time'] - df_time_series['date_time'].iloc[0]
            df_time_series['test_time'] = df_time_series['test_time'].dt.total_seconds()

            df_time_series['cycle_index_file'] = 1

            df_time_series['filename'] = filename
            df_time_series['ah_c'] = 0
            df_time_series['e_c'] = 0
            df_time_series['ah_d'] = 0
            df_time_series['e_d'] = 0
            df_time_series['cell_id'] = cell_id
            df_time_series['cycle_index'] = 0
            df_time_series['cycle_time'] = 0

            print(df_time_series['test_time'].head(5))

            if df_tmerge.empty:
                df_tmerge = df_time_series
            else:
                df_tmerge = df_tmerge.append(df_time_series, ignore_index=True)

    return df_tmerge


# import data from MACCOR-generated  files
def read_maccor(cell_id, file_path):

    # the importer can read Excel worksheets with the Channel number from Arbin files.
    # it assumes column names generated by the MACCOR:
    # Cycle_Index -> cycle_index
    # Test_Time(s) -> test_time
    # Current(A) -> i
    # Voltage(V) -> v
    # Date_Time -> date_time

    logging.info('adding files')

    listOfFiles = glob.glob(file_path + '*.txt')

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

        logging.info('processing file: ' + filename)

        if os.path.exists(cellpath):

            cellpath_df = prepare_maccor_file(cellpath)

            df_cell = pd.read_csv(cellpath_df, sep='\t')
            # Find the time series sheet in the excel file

            df_time_series_file = df_cell

            df_time_series = pd.DataFrame()

            df_time_series['cycle_index_file'] = df_time_series_file['Cycle'].apply(pd.to_numeric)
            df_time_series['test_time'] = df_time_series_file['Test Time (sec)'].str.replace(',', '').apply(pd.to_numeric)

            df_time_series['i'] = df_time_series_file['Current'].apply(pd.to_numeric)
            df_time_series['MD'] = df_time_series_file['MD']

            df_time_series['i'] = df_time_series.apply(lambda x: signedCurrent(x.MD, x.i), axis=1)

            df_time_series.drop('MD', axis=1, inplace=True)

            df_time_series['v'] = df_time_series_file['Voltage'].apply(pd.to_numeric)
            df_time_series['date_time'] = pd.to_datetime(df_time_series_file['DPT Time'], format='%m/%d/%Y %I:%M:%S %p')
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
def read_arbin(cell_id, file_path):

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
            if '~$' in cellpath:
                continue
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

                    #if not df_time_series_file['Temperature (C)_1'].empty:
                    #    df_time_series['cell_temperature'] = df_time_series_file['Temperature (C)_1']

                    df_time_series['ah_c'] = 0
                    df_time_series['e_c'] = 0
                    df_time_series['ah_d'] = 0
                    df_time_series['e_d'] = 0
                    df_time_series['cell_id'] = cell_id
                    df_time_series['cycle_index'] = 0
                    df_time_series['cycle_time'] = 0

                    cycles_index = df_time_series[["cycle_index_file"]].to_numpy()
                    past_cycle = 0
                    start = 0

                    for x in cycles_index:
                        if start == 0:
                            past_cycle = x[0]
                            start += 1
                        else:
                            if x[0]<past_cycle:
                                x[0] = past_cycle
                            past_cycle = x[0]

                    df_tmp = pd.DataFrame(data=cycles_index[:, [0]], columns=["cycle_index_file"])
                    df_time_series['cycle_index_file'] = df_tmp['cycle_index_file']

                    if df_tmerge.empty:
                        df_tmerge = df_time_series
                    else:
                        df_tmerge = df_tmerge.append(df_time_series, ignore_index=True)

    return df_tmerge


# sort data imported to insure cycle index and test times are correctly calculated
def sort_timeseries(df_tmerge):
    # Arrange the data by date time first, then by test time
    # Rebuild Cycle Index and test time to increment from file to file
    # This method does not depend on data from a specific testers

    logging.info('sorting timeseries dataframe')

    if not df_tmerge.empty:

        df_t = df_tmerge.sort_values(by=['date_time','test_time'])
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


# Build abuse test metadata
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

    # Build test metadata
    df_test_md = pd.DataFrame()
    df_test_md['cell_id'] = [df_c_md['cell_id']]
    df_test_md['test_temperature'] = [df_c_md['temperature']]
    df_test_md['thickness'] = [df_c_md['thickness']]
    df_test_md['v_init'] = [df_c_md['v_init']]
    df_test_md['indentor'] = [df_c_md['indentor']]
    df_test_md['nail_speed'] = [df_c_md['nail_speed']]

    return df_cell_md, df_test_md


# Build cycle test metadata
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

    # Build test metadata
    df_test_md = pd.DataFrame()
    df_test_md['cell_id'] = [df_c_md['cell_id']]
    df_test_md['crate_c'] = [df_c_md['crate_c']]
    df_test_md['crate_d'] = [df_c_md['crate_d']]
    df_test_md['soc_max'] = [df_c_md['soc_max']]
    df_test_md['soc_min'] = [df_c_md['soc_min']]
    df_test_md['test_temperature'] = [df_c_md['temperature']]

    return df_cell_md, df_test_md


# delete records (call with caution)
def delete_records(cell_id, conn):
    # this method will delete data for a cell_id. Use with caution as there is no undo
    db_conn = psycopg2.connect(conn)
    curs = db_conn.cursor()

    curs.execute("delete from cycle_timeseries where cell_id='" + cell_id + "'")
    curs.execute("delete from cycle_stats where cell_id='" + cell_id + "'")
    curs.execute("delete from cell_metadata where cell_id='" + cell_id + "'")
    curs.execute("delete from cycle_metadata where cell_id='" + cell_id + "'")

    db_conn.commit()
    curs.close()
    db_conn.close()

    return


# add cells to the database
def add_cells(cell_list, conn, save, plot, path, slash):
    # The importer expects an Excel file with cell and test information
    # The file contains one row per cell

    logging.info('add cells')
    df_excel = pd.read_excel(cell_list)

    # Process one cell at the time
    for ind in df_excel.index:

        cell_id = df_excel['cell_id'][ind]
        file_id = df_excel['file_id'][ind]

        logging.info("add file: " + file_id + " cell: " + cell_id)

        df_tmp = df_excel.iloc[ind]

        # Read time series data: Excel files from Arbin tester
        # Modify this method to add more testers
        file_path = path + file_id + slash

        test_type = str(df_excel["test"][ind])

        if test_type == "cycle":

            df_cell_md, df_test_md = populate_cycle_metadata(df_tmp)

            if df_excel['tester'][ind] == 'arbin':
                df_merge = read_arbin(cell_id, file_path)
            elif df_excel['tester'][ind] == 'maccor':
                df_merge = read_maccor(cell_id, file_path)
            elif df_excel['tester'][ind] == 'maccor':
                df_merge = read_maccor(cell_id, file_path)
            elif df_excel['tester'][ind] == 'generic':
                file_type = df_excel['file_type'][ind]
                mapping = df_excel['mapping'][ind]
                df_merge = read_generic(cell_id, file_path, file_type, mapping)

            # Sort the timeseries data and rebuild cycle index and test time
            df_ts = sort_timeseries(df_merge)

            # Calculate statistics and prepare the dataframes for saving
            df_stats, df_timeseries = calc_cycle_stats(df_ts, df_cell_md, df_test_md)

            # Controls when data is saved to the database

            if plot:
                df_timeseries.plot(x='test_time', y='v')
                df_timeseries.plot(x='test_time', y='i')
                plt.show()

            if save:
                engine = create_engine(conn)
                df_cell_md.to_sql('cell_metadata', con=engine, if_exists='append', chunksize=1000, index=False)
                df_test_md.to_sql('cycle_metadata', con=engine, if_exists='append', chunksize=1000, index=False)
                df_stats.to_sql('cycle_stats', con=engine, if_exists='append', chunksize=1000, index=False)
                df_timeseries.to_sql('cycle_timeseries', con=engine, if_exists='append', chunksize=1000, index=False)
                logging.info('data saved')

        elif test_type == "abuse":

            df_cell_md, df_test_md = populate_abuse_metadata(df_tmp)

            if df_excel['tester'][ind] == 'ornl':
                df_merge = read_ornlabuse(cell_id, file_path)
            elif df_excel['tester'][ind] == 'snl':
                df_merge = read_snlabuse(cell_id, file_path)

            # Sort the timeseries data and rebuild cycle index and test time
            df_ts = df_merge

            # Calculate statistics and prepare the dataframes for saving
            df_timeseries = calc_abuse_stats(df_ts, df_cell_md, df_test_md)

            if save:
                engine = create_engine(conn)
                df_cell_md.to_sql('cell_metadata', con=engine, if_exists='append', chunksize=1000, index=False)
                df_test_md.to_sql('abuse_metadata', con=engine, if_exists='append', chunksize=1000, index=False)
                df_timeseries.to_sql('abuse_timeseries', con=engine, if_exists='append', chunksize=1000, index=False)
                logging.info('data saved')


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

    df = pd.read_sql(sql_str[0], conn)

    cell_id_to_file = cell_id[0].replace(r'/', '-')
    csv = path + cell_id_to_file + '_cycle_data.csv'
    df.to_csv(csv, encoding='utf-8', index=False)


# generate csv files with time series data
def generate_timeseries_data(cell_id, conn, path):

    # generate timeseries data

    logging.info('export cell timeseries data to csv files')

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
      from cycle_timeseries where cell_id='""" + cell_id + """' order by test_time"""

    df = pd.read_sql(sql_str[0], conn)

    cell_id_to_file = cell_id[0].replace(r'/', '-')
    csv = path + cell_id_to_file + '_timeseries_data.csv'
    df.to_csv(csv, encoding='utf-8', index=False)


# generate csv files with time series and cycle data
def export_cells(cell_list, conn, path):

    # export data from the cell list

    logging.info('export cell data to csv files')
    df_excel = pd.read_excel(cell_list)

    # Process one cell at the time
    for ind in df_excel.index:
        cell_id_try = df_excel['cell_id'][ind]
        sql = "select * from cell_metadata where cell_id='" + cell_id_try + "'"
        df_tmp = pd.read_sql(sql, conn)

        # if the cell exist, then update, otherwise skip
        if not df_tmp.empty:

            cell_id = df_tmp['cell_id']
            generate_cycle_data(cell_id, conn, path)
            generate_timeseries_data(cell_id, conn, path)

    return


# add new calculated quantities to cells previously imported, or update existing calculated statistics
def update_cells(cell_list, conn, save, plot):

    logging.info('update cell data')

    # The importer expects an Excel file with the cell id and test information
    # The file contains one row per cell
    df_excel = pd.read_excel(cell_list)

    # Process one cell at the time
    for ind in df_excel.index:

        cell_id_try = df_excel['cell_id'][ind]
        sql = "select * from cell_metadata where cell_id='" + cell_id_try + "'"
        df_try = pd.read_sql(sql, conn)

        # if the cell exist, then update, otherwise skip
        if not df_try.empty:

            df_tmp = df_excel.iloc[ind]
            df_cell_md, df_test_md = populate_cycle_metadata(df_tmp)

            cell_id = df_tmp['cell_id']
            logging.info("update:" + cell_id)

            sql = "select * from cycle_timeseries where cell_id='" + cell_id + "' order by test_time"
            df_ts = pd.read_sql(sql, conn)

            df_cycle_data, df_timeseries_data = calc_cycle_stats(df_ts,df_cell_md, df_test_md )

            delete_records(cell_id, conn)

            # Useful flag during testing
            if plot:
                df_cycle_data.plot(x='cycle_index', y='ah_c')
                df_cycle_data.plot(x='cycle_index', y='ah_d')
                plt.show()

            # Controls when data is saved to the database
            if save:
                engine = create_engine(conn)
                logging.info('save cell metadata')
                df_cell_md.to_sql('cell_metadata', con=engine, if_exists='append', chunksize=1000, index=False)
                logging.info('save test metadata')
                df_test_md.to_sql('cycle_metadata', con=engine, if_exists='append', chunksize=1000, index=False)
                logging.info('save cycle data')
                df_cycle_data.to_sql('cycle_stats', con=engine, if_exists='append', chunksize=1000, index=False)
                logging.info('save timeseries data')
                df_timeseries_data.to_sql('cycle_timeseries', con=engine, if_exists='append', chunksize=1000,
                                          index=False)

        else:
            logging.info("cell:" + cell_id_try + " not found")

    return


def main(argv):

    # command line variables that can be used to run from an IDE without passing arguments
    mode = 'env'
    path = r'C:\\Users\\vdeange\\Documents\\BA\\calce\\'

    # initializing the logger
    logging.basicConfig(format='%(asctime)s %(message)s', filename='blc-python.log', level=logging.DEBUG)
    logging.info('starting')

    try:
        opts, args = getopt.getopt(argv, "hm:p:", ["mode=", "path="])
    except getopt.GetoptError:
        print('run as: data_import.py -m <mode> -p <path>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('data_import.py -m <mode> -p <path>')
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
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
                conn = j[1]
    except:
        print("Error opening env file:", sys.exc_info()[0])

    # read configuration values
    data = yaml.safe_load(open('battery-blc-library.yaml'))

    plot = data['environment']['PLOT']
    save = data['environment']['SAVE']
    style = data['environment']['STYLE']

    # use default if env file not there
    if conn == '':
        conn = data['environment']['DATABASE_CONNECTION']

    #logging.info('command line: ' + str(opts))
    logging.info('configuration: ' + str(data))

    # needed to maintain compatibility with windows machines
    if style == 'unix':
        slash = "/"
    elif style == 'windows':
        slash = r'\\'

    # Mode of operation
    if mode == 'add':
        add_cells(path + "cell_list.xlsx", conn, save, plot, path, slash)
    elif mode == 'update':
        update_cells(path + "cell_list.xlsx", conn, save, plot)
    elif mode == 'export':
        export_cells(path + "cell_list.xlsx", conn, path)
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



