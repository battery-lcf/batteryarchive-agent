# coding: utf-8
# Copyright 2025 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.

import logging
import pandas as pd
import pathlib

from abstractModule import AbstractModule
from flowCell import FlowCell

class FlowStack(AbstractModule):
    def __init__(self):
        self.cell_metadata_table = 'flow_cell_metadata'
        self.cycle_metadata_table = 'flow_cycle_metadata'
        self.timeseries_table = 'flow_cycle_timeseries'
        self.buffer_table = 'flow_cycle_timeseries_buffer'
        self.stats_table = 'flow_cycle_stats'
    
    def set_tester(self):
        pass
        
    def set_path(self, path):
        pass
    
    def set_file_id(self):
        pass
    
    def set_file_type(self):
        pass

    def populate_metadata(self):
        return
    
    def create_cell_df(self, path, row):
        return