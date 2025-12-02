# coding: utf-8
# Copyright 2025 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.

import logging
import pandas as pd
import pathlib

from abstractModule import AbstractModule
from lithiumCell import LithiumCell

class LithiumModule(AbstractModule):
    def __init__(self, path:str, md:pd.DataFrame):
        self.module_metadata_table = 'module_metadata'
        self.cycle_metadata_table = 'cycle_metadata'
        self.timeseries_table = 'cycle_timeseries'
        self.buffer_table = 'cycle_timeseries_buffer'
        self.stats_table = 'cycle_stats'
        self.md = md #metadata from module?
        self.child_type = type(LithiumCell)

        self.module_id = self.md['module_id']
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

    def populate_metadata(self) -> tuple[pd.DataFrame,pd.DataFrame]:
        # Build module metadata
        df_module_md = pd.DataFrame()
        df_module_md['module_id'] = [self.md['module_id']]
        df_module_md['configuration'] = [self.md['configuration']]
        df_module_md['num_parallel'] = [self.md['cathode']]
        df_module_md['num_series'] = [self.md['source']]
        # create virtual 'cell_list.xlsx' as a dataframe
        config = pd.ExcelFile(self.configuration_file)
        insert_md = pd.DataFrame({'cathode':None,'anode':None,'temperature':None,'soc_max':None,'soc_min':None,'source':None,'crate_c':None,'crate_d':None,'ah':None,'form_factor':None,'tester':None,'test':None,'file_type':None})
        insert_md = df_module_md[insert_md.columns]
        df_cell_md = pd.DataFrame()
        for index, row in config: 
            df_cell_md.loc[index] = insert_md
            if row['Type'] == 'Cell':
                df_cell_md.loc[index] = insert_md
                df_cell_md.at[index,'cell_id'] = df_module_md['module_id'] + '_' + row['Name'] #create cell_id by concat
                df_cell_md.at[index,'file_id'] = self.file_id
        print(df_cell_md) #temp for testing
        return df_module_md, df_cell_md
    
    def create_cell_df(self, path:str, row) -> pd.DataFrame:
        #creates timeseries dataframe for a single cell from the module data timeseries excel file
        data_files = glob.glob(os.path.join(path, f"*.xlsx"))
        data_files = [file for file in data_files if not self.configuration_file and "~$" not in os.path.basename(file)]
        df_module_file = pd.ExcelFile(data_files[0])
        df_cell_ts = pd.DataFrame
        #Column names
        df_cell_ts.columns = ['Date_Time', 'Cycle_Index', 'Test_Time(s)', 'Current(A)', 'Voltage(V)']
        #Timeseries data
        df_cell_ts['Date_Time'] = df_module_file[row['Timestamp Column']]
        df_cell_ts['Cycle_Index'] = df_module_file[row['Cycle index column']]
        df_cell_ts['Test_Time(s)'] = df_module_file[row['Test time column']]
        df_cell_ts['Current(A)'] = df_module_file[row['Current column']]
        df_cell_ts['Voltage(V)'] = df_module_file[row['Voltage column']]
        return df_cell_ts
