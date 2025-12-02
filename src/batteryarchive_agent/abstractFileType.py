# coding: utf-8
# Copyright 2025 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.
from abc import ABC, abstractmethod

class AbstractFileType(ABC):
    def __init__(self):
        self.tester =  ''
        self.reader_func = ''
        self.col_mapping = ''
        self.unit_mult = ''

    @abstractmethod
    def file_to_df(self):
        #converts file to df 
        #mostly will just use default pd function, but some need more processing (i.e. matlab)
        pass

    @abstractmethod
    def datetime_to_testtime(self):
        pass