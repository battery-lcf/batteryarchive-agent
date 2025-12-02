# coding: utf-8
# Copyright 2025 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.
import pathlib
import pandas as pd
import logging
from sqlalchemy import Engine, text

from abstractCell import AbstractCell

class FlowCell(AbstractCell):
    def __init__(self, path:str, md:pd.Series):
        self.cell_metadata_table = 'flow_cell_metadata'
        self.cycle_metadata_table = 'flow_cycle_metadata'
        self.timeseries_table = 'flow_cycle_timeseries'
        self.buffer_table = 'flow_cycle_timeseries_buffer'
        self.stats_table = 'flow_cycle_stats'
        self.md = md

        self.cell_id = self.md['cell_id']
        self.set_file_id()
        self.set_tester()
        self.set_file_type()
        self.set_path(path)
    
    def set_tester(self):
        self.tester = self.md['tester']
        
    def set_path(self, path:str):
        self.file_path = pathlib.PurePath(path).joinpath(self.file_id)
    
    def set_file_id(self):
        self.file_id = self.md['file_id'] #use get functions
    
    def set_file_type(self):
        self.file_type = self.md['file_type']
    
    def set_cell_id(self, id:str):
        self.cell_id = id
   
    def calc_timeseries(self, df_t:pd.DataFrame) -> pd.DataFrame:
        df_t['cycle_time'] = 0
        no_cycles = int(df_t['cycle_index'].max())
        for c_ind in pd.RangeIndex(30):
            x = no_cycles + c_ind - 29
            df_f = df_t[df_t['cycle_index'] == x]
            df_f['ah_c'] = 0
            df_f['e_c'] = 0
            df_f['ah_d'] = 0
            df_f['e_d'] = 0
            df_f['w'] = 0
            if not df_f.empty:
                try:
                    df_f['dt'] = df_f['test_time'].diff() / 3600.0
                    df_f = self.calc_cycle_quantities(df_f)
                    df_t['cycle_time'] = df_t['cycle_time'].astype('float64') #to address dtype warning

                    df_t.loc[df_t.cycle_index == x, 'cycle_time'] = df_f['cycle_time']
                    df_t.loc[df_t.cycle_index == x, 'ah_c'] = df_f['ah_c']
                    df_t.loc[df_t.cycle_index == x, 'e_c'] = df_f['e_c']
                    df_t.loc[df_t.cycle_index == x, 'ah_d'] = df_f['ah_d']
                    df_t.loc[df_t.cycle_index == x, 'e_d'] = df_f['e_d']
                    df_t.loc[df_t.cycle_index == x, 'w'] = df_f['i'] * df_f['v'] #power
                except Exception as e:
                    logging.info(e)
        df_tt = df_t[df_t['cycle_index'] > 0]
        return df_tt

    def calc_cycle(self, df_t:pd.DataFrame, engine:Engine) -> pd.DataFrame:
        logging.info('calculate cycle time and cycle statistics')
        df_t['cycle_time'] = 0
        no_cycles = int(df_t['cycle_index'].max())
        # Initialize the cycle_data time frame
        a = [x for x in range(no_cycles-30, no_cycles)]  # using loops
        df_c = pd.DataFrame(data=a, columns=["cycle_index"]) 
        
        #'cmltv' = 'cumulative'
        df_c['cell_id'] = self.cell_id
        df_c['cycle_index'] = 0
        df_c['v_max'] = 0
        df_c['i_max'] = 0
        df_c['v_min'] = 0
        df_c['i_min'] = 0
        df_c['ah_c'] = 0
        df_c['ah_d'] = 0
        df_c['e_c'] = 0
        df_c['e_d'] = 0
        #find better solution for this
        with engine.connect() as conn:
            init = pd.read_sql(text("select max(e_c_cmltv) from " + self.stats_table + " where cell_id='"+self.cell_id+"'"), conn).iloc[0,0] #for continuity btwn calc_stats calls
            init = 0 if init == None else init
            df_c['e_c_cmltv'] = init 
            init = pd.read_sql(text("select max(e_d_cmltv) from " + self.stats_table + " where cell_id='"+self.cell_id+"'"), conn).iloc[0,0]
            init = 0 if init == None else init
        df_c['e_d_cmltv'] = init 
        df_c['v_c_mean'] = 0
        df_c['v_d_mean'] = 0
        df_c['test_time'] = 0
        df_c['ah_eff'] = 0
        df_c['e_eff'] = 0
        df_c['e_eff_cmltv'] = 0
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
                    'e_c_cmltv': float,
                    'e_d_cmltv': float,
                    'v_c_mean': float,
                    'v_d_mean': float,
                    'test_time': float,
                    'ah_eff': float,
                    'e_eff': float,
                    'e_eff_cmltv': float
                }
    
        df_c = df_c.astype(convert_dict)
        for c_ind in df_c.index:
            #x = c_ind + 1
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
                    
                    df_c.iloc[c_ind, df_c.columns.get_loc('ah_c')] = df_f['ah_c'].max()
                    df_c.iloc[c_ind, df_c.columns.get_loc('ah_d')] = df_f['ah_d'].max()
                    df_c.iloc[c_ind, df_c.columns.get_loc('e_c')] = df_f['e_c'].max()
                    df_c.iloc[c_ind, df_c.columns.get_loc('e_d')] = df_f['e_d'].max()
                    df_c.iloc[c_ind, df_c.columns.get_loc('e_c_cmltv')] = df_f['e_c'].max() + df_c.iloc[c_ind-1,df_c.columns.get_loc('e_c_cmltv')]
                    df_c.iloc[c_ind, df_c.columns.get_loc('e_d_cmltv')] = df_f['e_d'].max() + df_c.iloc[c_ind-1,df_c.columns.get_loc('e_d_cmltv')]
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
                        
                    if df_c.iloc[c_ind, df_c.columns.get_loc('e_c_cmltv')] == 0:
                        df_c.iloc[c_ind, df_c.columns.get_loc('e_eff_cmltv')] = 0
                    else:
                        df_c.iloc[c_ind, df_c.columns.get_loc('e_eff_cmltv')] = df_c.iloc[c_ind, df_c.columns.get_loc('e_d_cmltv')] / \
                                                                        df_c.iloc[c_ind, df_c.columns.get_loc('e_c_cmltv')]
                except Exception as e:
                    logging.info("Exception @ x: " + str(x))
                    logging.info(e)
                    
        logging.info("cycle: " + str(x))
        logging.info("cell_id: "+ df_c['cell_id'])
        df_cc = df_c[df_c['cycle_index'] > 0]
        return df_cc
    
    def calc_cycle_quantities(self, df:pd.DataFrame) -> pd.DataFrame:
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
      
    def populate_metadata(self) -> tuple[pd.DataFrame,pd.DataFrame]: 
        # Build cell metadata
        df_cell_md = pd.DataFrame()
        df_cell_md['cell_id'] = [self.md['cell_id']]
        df_cell_md['flow_pattern'] = [self.md['flow pattern']]
        df_cell_md['ne_material'] = [self.md['NE material']]
        df_cell_md['pe_material'] = [self.md['PE material']]
        df_cell_md['membrane'] = [self.md['membrane']]
        df_cell_md['membrane_size'] = [self.md['membrane size (cm2)']]
        df_cell_md['ne_active'] = [self.md['NE active']]
        df_cell_md['initial_ne_active'] = [self.md['initial [NE active], M']]
        df_cell_md['pe_active'] = [self.md['PE active']]
        df_cell_md['initial_pe_active'] = [self.md['initial [PE active], M']]
        df_cell_md['ne_volume'] = [self.md['NE volume (L)']]
        df_cell_md['pe_volume'] = [self.md['PE volume (L)']]  
        df_cell_md['flow_rate'] = [self.md['flow rate (L/min)']]
        df_cell_md['test_type'] = [self.md['test type']]
        #df_cell_md['source'] = [self.md['source']]
        df_cell_md['test'] = [self.md['test']]
        df_cell_md['tester'] = [self.md['tester']]
        
        # Build cycle metadata - TODO
        df_cycle_md = pd.DataFrame()
        
        return df_cell_md, df_cycle_md
