# coding: utf-8
# Copyright 2025 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.
from abc import ABC, abstractmethod

class AbstractCell(ABC):
    def __init__(self):
        self.cell_metadata_table = ''
        self.cycle_metadata_table = ''
        self.timeseries_table = ''
        self.buffer_table = ''
        self.stats_table = ''

    @abstractmethod
    def set_tester(self):
        pass
    
    @abstractmethod
    def set_path(self, path):
        pass

    @abstractmethod
    def set_cell_id(self, id):
        return
    
    @abstractmethod
    def set_file_id(self):
        pass
    
    @abstractmethod
    def set_file_type(self):
        pass
   
    @abstractmethod
    def calc_timeseries(self):
        pass
    
    @abstractmethod
    def calc_cycle(self, df, *args):
        pass
    
    @abstractmethod
    def calc_cycle_quantities(self):
        pass
    
    @abstractmethod
    def populate_metadata(self): 
        return
