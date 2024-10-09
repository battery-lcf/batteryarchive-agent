#!/usr/bin/env python
# coding: utf-8

import os
import argparse 
import glob
import pandas as pd
import numpy as np #for mat files
import h5py #for mat files
pd.options.mode.chained_assignment = None  # default='warn'
import matplotlib.pyplot as plt
import psycopg2
from sqlalchemy import create_engine
import yaml
import sys, getopt
import logging
import logging.config
import time
from sqlalchemy import MetaData, Table
from sqlalchemy import create_engine, select, insert, update, delete, func

# Copyright 2021 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.

class abstractDataType():
    def template_method(self):
        self.add_data()
        self.calc_stats()
        self.buffer()
        self.cell_metadata_table = ''
        self.cycle_metadata_table = ''
        self.timeseries_table = ''
        self.buffer_table = ''
        self.stats_table = ''

    #add cells to the database
    def add_data(self, cell_list, conn, save, plot, path, slash): ##conflict how to pass all tables
        logging.info('add cells')
        df_excel = pd.read_excel(cell_list)

        # Process one cell at the time
        for ind in df_excel.index:

            cell_id = df_excel['cell_id'][ind]
            file_id = df_excel['file_id'][ind]
            tester = df_excel['tester'][ind]
            file_type = df_excel['file_type'][ind]
            source = df_excel['source'][ind]

            logging.info("add file: " + file_id + " cell: " + cell_id)

            df_tmp = df_excel.iloc[ind]

            print(df_tmp)

            df_cell_md, df_cycle_md = self.populate_cycle_metadata(df_tmp) ##rconflict??

            engine = create_engine(conn)

            # check if the cell is already there and report status

            status = self.check_cell_status(cell_id, conn)

            if status=="completed":
                print("skip cell_id: " + cell_id)

            if status=='new': 

                logging.info('save cell metadata')
                df_cell_md.to_sql(self.cell_metadata_table, con=engine, if_exists='append', chunksize=1000, index=False)##rconflict
                logging.info('save cycle metadata')
                df_cycle_md.to_sql(self.cycle_metadata_table, con=engine, if_exists='append', chunksize=1000, index=False)##rconflict

                status = 'buffering'

                self.set_cell_status(cell_id, status, conn)
            if status=='buffering':
                print("buffering cell_id: " + cell_id)

                file_path = path + file_id + slash

                #replacing selector with one function that will differ in each class
                cycle_index_max = self.setup_buffer(cell_id, source, file_path, engine, conn, file_type)

                print('start import')

                status = "processing"

                self.set_cell_status(cell_id, status, conn)

            if status == 'processing':

                # read the data back in chunks.
                block_size = 30

                cycle_index_max = self.get_cycle_index_max(cell_id, conn, self.buffer_table) ##rconflict
                cycle_stats_index_max = self.get_cycle_index_max(cell_id, conn, self.stats_table) ##rconflict

                print("max cycle: " + str(cycle_index_max))

                start_cycle = 1
                start_time = time.time()

                for i in range(cycle_index_max+1):
                
                    if (i-1) % block_size == 0 and i > 0 and i>cycle_stats_index_max:

                        start_cycle = i
                        end_cycle = start_cycle + block_size - 1

                        sql_cell =  " cell_id='" + cell_id + "'" 
                        sql_cycle = " and cycle_index>=" + str(start_cycle) + " and cycle_index<=" + str(end_cycle)
                        sql_str = "select * from " + self.buffer_table + " where " + sql_cell + sql_cycle + " order by test_time"##rconflict

                        print(sql_str)
                        df_ts = pd.read_sql(sql_str, conn)

                        df_ts.drop('sheetname', axis=1, inplace=True)

                        if not df_ts.empty:
                            start_time = time.time()
                            df_cycle_stats, df_cycle_timeseries = self.calc_stats(df_ts, cell_id, engine)
                            print("calc_stats time: " + str(time.time() - start_time))
                            logging.info("calc_stats time: " + str(time.time() - start_time))

                            start_time = time.time()
                            df_cycle_stats.to_sql(self.stats_table, con=engine, if_exists='append', chunksize=1000, index=False)##rconflict
                            print("save stats time: " + str(time.time() - start_time))
                            logging.info("save stats time: " + str(time.time() - start_time))

                            start_time = time.time()
                            df_cycle_timeseries.to_sql(self.timeseries_table, con=engine, if_exists='append', chunksize=1000, index=False) ##rconflict
                            print("save timeseries time: " + str(time.time() - start_time))
                            logging.info("save timeseries time: " + str(time.time() - start_time))


                status='completed'

                self.set_cell_status(cell_id, status, conn)

                self.clear_buffer(cell_id, conn)

    def calc_stats(self, df_t, ID, engine):
        logging.info('calculate cycle time and cycle statistics')
        df_t['cycle_time'] = 0
        no_cycles = int(df_t['cycle_index'].max())
        # Initialize the cycle_data time frame
        a = [x for x in range(no_cycles-30, no_cycles)]  # using loops
        df_c = pd.DataFrame(data=a, columns=["cycle_index"]) 
        
        #'cmltv' = 'cumulative'
        df_c['cell_id'] = ID
        df_c['cycle_index'] = 0
        df_c['v_max'] = 0
        df_c['i_max'] = 0
        df_c['v_min'] = 0
        df_c['i_min'] = 0
        df_c['ah_c'] = 0
        df_c['ah_d'] = 0
        df_c['e_c'] = 0
        df_c['e_d'] = 0
        if self.batt_type == 'flow':
            with engine.connect() as conn: ## conflict for flow
                init = pd.read_sql("select max(e_c_cmltv) from " + self.stats_table + " where cell_id='"+ID+"'", conn).iloc[0,0] #for continuity btwn calc_stats calls
                init = 0 if init == None else init
                df_c['e_c_cmltv'] = init 
                init = pd.read_sql("select max(e_d_cmltv) from " + self.stats_table + " where cell_id='"+ID+"'", conn).iloc[0,0]
                init = 0 if init == None else init
            df_c['e_d_cmltv'] = init ## conflict
            df_c['e_eff_cmltv'] = 0 ##conflict 
        df_c['v_c_mean'] = 0
        df_c['v_d_mean'] = 0
        df_c['test_time'] = 0
        df_c['ah_eff'] = 0
        df_c['e_eff'] = 0
        if self.batt_type == 'flow':
            convert_dict = {'cell_id': str,
                        'cycle_index': int,
                        'v_max': float,
                        'i_max': float,
                        'v_min': float,
                        'i_min': float,
                        'ah_c': float,
                        'ah_d': float,
                        'e_c': float,
                        'e_d': float,
                        'e_c_cmltv': float, ##conflict
                        'e_d_cmltv': float, ##conflict
                        'v_c_mean': float,
                        'v_d_mean': float,
                        'test_time': float,
                        'ah_eff': float,
                        'e_eff': float,
                        'e_eff_cmltv': float ##conflict
                    }
        elif self.batt_type == 'li-ion':
                       convert_dict = {'cell_id': str,
                        'cycle_index': int,
                        'v_max': float,
                        'i_max': float,
                        'v_min': float,
                        'i_min': float,
                        'ah_c': float,
                        'ah_d': float,
                        'e_c': float,
                        'e_d': float,
                        'v_c_mean': float,
                        'v_d_mean': float,
                        'test_time': float,
                        'ah_eff': float,
                        'e_eff': float,
                    }
        df_c = df_c.astype(convert_dict)
        for c_ind in df_c.index:
            x = no_cycles + c_ind - 29
            
            df_f = df_t[df_t['cycle_index'] == x]
            df_f['ah_c'] = 0
            df_f['e_c'] = 0
            df_f['ah_d'] = 0
            df_f['e_d'] = 0
            df_f['w'] = 0
            
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
                    df_f = self.calc_cycle_quantities(df_f)
                    df_t['cycle_time'] = df_t['cycle_time'].astype('float64') #to address dtype warning
                    
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
                    if self.batt_type == 'flow':
                        df_t.loc[df_t.cycle_index == x, 'w'] = df_f['i'] * df_f['v'] 
                        df_c.iloc[c_ind, df_c.columns.get_loc('e_c_cmltv')] = df_f['e_c'].max() + df_c.iloc[c_ind-1,df_c.columns.get_loc('e_c_cmltv')] ##conflict
                        df_c.iloc[c_ind, df_c.columns.get_loc('e_d_cmltv')] = df_f['e_d'].max() + df_c.iloc[c_ind-1,df_c.columns.get_loc('e_d_cmltv')] ##conflict

                        if df_c.iloc[c_ind, df_c.columns.get_loc('e_c_cmltv')] == 0: ##conflict
                            df_c.iloc[c_ind, df_c.columns.get_loc('e_eff_cmltv')] = 0
                        else:
                            df_c.iloc[c_ind, df_c.columns.get_loc('e_eff_cmltv')] = df_c.iloc[c_ind, df_c.columns.get_loc('e_d_cmltv')] / \
                                                                        df_c.iloc[c_ind, df_c.columns.get_loc('e_c_cmltv')]
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
        logging.info("cell_id: "+ df_c['cell_id'])
        df_cc = df_c[df_c['cycle_index'] > 0]
        df_tt = df_t[df_t['cycle_index'] > 0]
        return df_cc, df_tt
    
    def setup_buffer(self, cell_id, source, file_path, engine, conn, file_type): ##conflict need to pass file_type
        logging.info('adding files')
        listOfFiles = glob.glob(file_path + '*.'+ file_type +'*') ##rconflict
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

        sheetnames = self.buffered_sheetnames(cell_id, conn)

        for ind in df_file.index:
            filename = df_file['filename'][ind]
            cellpath = file_path + filename
            timeseries = ""
            logging.info('buffering file: ' + filename)
            cycle_index_max = self.buffer(cell_id, source, cellpath, filename, sheetnames, engine, start_time)

        return cycle_index_max
    
    def buffer(self, cell_id, source, cellpath, filename, sheetnames, engine, start_time):
        pass
    
    def calc_cycle_quantities(self,df):
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
        
    def populate_cycle_metadata(self, df_c_md): ##conflict need to pass cell type from main
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
    
    def get_cycle_index_max(self, cell_id, conn, table):
        sql_str = "select max(cycle_index)::int as max_cycles from " + table + " where cell_id = '" + cell_id + "'" ##rconflict
        db_conn = psycopg2.connect(conn)
        curs = db_conn.cursor()
        curs.execute(sql_str)
        db_conn.commit()
        record = [r[0] for r in curs.fetchall()]
        if record[0]: 
            cycle_index_max = record[0] 
        else:
            cycle_index_max = 0
        curs.close()
        db_conn.close()
        return cycle_index_max

    def get_cycle_stats_index_max():
        ##rconfict this could be combined with get_cycle_index_max
        return
    
    def check_cell_status(self, cell_id, conn):
        status = 'new'
        sql_str = "select * from " + self.cell_metadata_table + " where cell_id = '" + cell_id + "'" ##rconflict
        db_conn = psycopg2.connect(conn)
        curs = db_conn.cursor()
        curs.execute(sql_str)
        db_conn.commit()
        record = curs.fetchall()
        if record: 
            status = record[0][16] ##conflict, see joseph's code
        else:
            status = 'new'
        curs.close()
        db_conn.close()
        print('cell status is: ' + status)
        return status
        
    def set_cell_status(self, cell_id, status, conn):
        sql_str = "update " + self.cell_metadata_table + " set status = '" + status + "' where cell_id = '" + cell_id + "'" ##rconflict
        db_conn = psycopg2.connect(conn)
        curs = db_conn.cursor()
        curs.execute(sql_str)
        db_conn.commit()
        curs.close()
        db_conn.close()
        return
    
    def clear_buffer(self, cell_id, conn):
        # this method will delete data for a cell_id. Use with caution as there is no undo
        db_conn = psycopg2.connect(conn)
        curs = db_conn.cursor()
        curs.execute("delete from " + self.buffer_table + " where cell_id='" + cell_id + "'") ##rconflict
        db_conn.commit()
        curs.close()
        db_conn.close()
        return
    
    def buffered_sheetnames(self, cell_id, conn):
        sql_str = "select distinct sheetname from " + self.buffer_table + " where cell_id = '" + cell_id + "'" ##rconflict
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

class liCellCsv(abstractDataType):
    def __init__(self):
        super().__init__()
        self.batt_type = 'li-ion'
        self.cell_metadata_table = 'cell_metadata'
        self.cycle_metadata_table = 'cycle_metadata'
        self.timeseries_table = 'cycle_timeseries'
        self.buffer_table = 'cycle_timeseries_buffer'
        self.stats_table = 'cycle_stats'

    def buffer(self, cell_id, source, cellpath, filename, sheetnames, engine, start_time):
        cycle_index_max = 0
        if os.path.exists(cellpath):
            df_time_series_file = pd.read_csv(cellpath)
            # Find the time series sheet in the excel file

            if source=='ISU-ILCC':
            #Calculate the Time (s) for the UConn data (only has date time)
                df_time_series_file['pystamp']=pd.to_datetime(df_time_series_file['Timestamp']) #convert to python date-time format in ns
                df_time_series_file['inttime']=df_time_series_file['pystamp'].astype(int)
                df_time_series_file['inttime']=df_time_series_file['inttime'].div(10**9)
                df_time_series_file['Time [s]']=df_time_series_file['inttime']-df_time_series_file['inttime'].iloc[0]

            df_time_series = pd.DataFrame()

            try:
                if source=='ISU-ILCC':
                    df_time_series['cycle_index'] = df_time_series_file['Cycle'] 
                    df_time_series['test_time'] = df_time_series_file['Time [s]']
                    df_time_series['i'] = df_time_series_file['Current (A)'] 
                    df_time_series['v'] = df_time_series_file['Voltage (V)']
                    df_time_series['date_time'] = df_time_series_file['Timestamp'] 
                    df_time_series['cell_id'] = cell_id
                    df_time_series['sheetname'] = filename
                elif source=='TON-KIT':
                    df_time_series['cycle_index'] = df_time_series_file['cycle number']
                    df_time_series['test_time'] = df_time_series_file['time/s']
                    df_time_series['i'] = df_time_series_file['<I>/mA']
                    df_time_series['v'] = df_time_series_file['Ecell/V']
                    df_time_series['cell_id'] = cell_id
                    df_time_series['sheetname'] = filename
                elif source=='XCEL':
                    df_time_series['cycle_index'] = df_time_series_file['cycle_index']
                    df_time_series['test_time'] = df_time_series_file['test_time']
                    df_time_series['i'] = df_time_series_file['i']
                    df_time_series['v'] = df_time_series_file['v']
                    df_time_series['date_time'] = df_time_series_file['date_time']
                    df_time_series['env_temperature'] = df_time_series_file['env_temperature']
                    df_time_series['cell_id'] = cell_id
                    df_time_series['sheetname'] = filename
                
                cycle_index_file_max = df_time_series.cycle_index.max()

                print('saving sheet: with max cycle: ' +str(cycle_index_file_max)) ##weird

                df_time_series.to_sql(self.buffer_table, con=engine, if_exists='append', chunksize=1000, index=False)

                print("saved=" + filename + " time: " + str(time.time() - start_time))

                start_time = time.time()

            except KeyError as e:
                print("I got a KeyError - reason " + str(e))
                print("processing: time: " + str(time.time() - start_time))##weird
                start_time = time.time()

        return cycle_index_max
    
def main(argv):

    # command line variables that can be used to run from an IDE without passing arguments
    mode = 'env'
    path = r'\\'

    # initializing the logger
    logging.basicConfig(format='%(asctime)s %(message)s', filename='blc-python.log', level=logging.DEBUG)
    logging.info('starting')

    try:
        opts, args = getopt.getopt(argv, "h")
        path = args[0]
    except getopt.GetoptError:
        print('run as: data_import_agent.py <path>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('run as: data_import_agent.py <path>')
            sys.exit()

    # read database connection
    conn = ''
    try:
        env = yaml.safe_load(open('../env'))
        x = env.split(" ")
        for i in x:
            j = i.split("=")
            if j[0] == 'LOCAL_CONNECTION':
                conn =  j[1]
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

    logging.info('command line: ' + str(opts))
    logging.info('configuration: ' + str(data))

    # needed to maintain compatibility with windows machines
    if style == 'unix':
        slash = "/"
    elif style == 'windows':
        slash = r'\\'

    imp = liCellCsv()
    imp.add_data(path + "cell_list.xlsx", conn, save, plot, path, slash)



if __name__ == "__main__":
    main(sys.argv[1:])