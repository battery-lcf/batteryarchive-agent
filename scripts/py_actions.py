import os, sys
currentdir = os.getcwd()
sys.path.append(os.path.join(currentdir))
sys.path.append(os.path.join(currentdir, 'app'))
from os.path import exists
from app.archive_constants import DB_URL, LIVE_DB_URL, FORMAT
from app.controllers import cell_controller as cc 

def py_cell_import(cell_list_path):
    cc.import_cells_xls_to_db(cell_list_path)


# TODO: read cell IDs from cell_list and export also the cycle_stats.csv file
def py_cell_export(cell_id, cell_list_path):
    cc.export_cycle_ts_data_csv(cell_id, cell_list_path)


def py_cell_update(cell_list_path):
    cc.update_cycle_cells(cell_list_path)