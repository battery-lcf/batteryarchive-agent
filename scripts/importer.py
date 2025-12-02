# coding: utf-8
# Copyright 2025 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.

import logging
import logging.config
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import pathlib
import psycopg2
import sys, getopt
from sqlalchemy import create_engine, text, Engine
import time
import yaml

import batteryarchive_agent as ba


##QUESTIONS:
# most logical naming for args?
# come up with standardized names for 'generic' csv

# done 0) find place for column conversion date_time <-> test_time 
# done 1) update data
# done 1.5) move column mapping to file type classes
# 2) add module data
# done 3) add flow cells
# done 4) add additional file types (arbin, matlab-stanfordTRI, generic-uconn)
# done 5) create __init__ and package
# 5.5 improve CLI with click
# 6) docstrings and types
# 7) test for typical errors ('break' code intentionally) and improve speed/efficiency (create test suite)
def add_module_stack_data(engine:Engine, conn:str, modules_to_import:list[ba.AbstractModule]): #for modules and stacks
    #1) import module metadata
    for ind, module in enumerate(modules_to_import):
        id = module.module_id

        print(module.md)
        module_md, cell_md = module.populate_metadata()

        try:
            status = get_status(id, module.module_metadata_table, conn, id_type='module')
        except psycopg2.OperationalError:
            print('Database is not available.')
        if status=='completed':
            #logging skipping module id 
            pass
        if status=='new':
            logging.info('save module metadata')
            module_md.to_sql(module.module_metadata_table, con=engine, if_exists='append', chunksize=1000, index=False)
            cells_to_import = [module.child_type(module.file_path,row) for ind, row in cell_md.iterrows()]
            #need to convert module to cell ts first
            add_cell_data(engine, conn, cell_md, cells_to_import)
    #2) convert module format to cell
    #3) import cell data (call add_cell_data)

def add_cell_data(engine:Engine, conn:str, cells_to_import:list[ba.AbstractCell]): 
    #adds data to database
    #logging
    for ind, cell in enumerate(cells_to_import):
        id = cell.cell_id
        cell.set_file_id()
        cell.set_file_type()
        cell.set_tester()
    
        print(cell.md) #print current cell metadata
        cell_md, cycle_md = cell.populate_metadata()
        
        try:
            status = get_status(id, cell.cell_metadata_table, conn, id_type='cell_id')
        except psycopg2.OperationalError:
            print('Database is not available.')
        if status=='completed':
            #logging skipping cell id 
            pass
        if status=='new':
            logging.info('save cell metadata')
            cell_md.to_sql(cell.cell_metadata_table, con=engine, if_exists='append', chunksize=1000, index=False)
            logging.info('save cycle metadata')
            cycle_md.to_sql(cell.cycle_metadata_table, con=engine, if_exists='append', chunksize=1000, index=False)
            status = 'buffering'
            set_status(id, cell.cell_metadata_table, conn, status, id_type='cell_id')
        if status=='buffering':
            logging.info('adding files')
            start_time = time.time()
            df_ts = buffer(cell, get_file_type_obj(cell.tester))
            df_ts.to_sql(cell.buffer_table, con=engine, if_exists='append', chunksize=1000, index=False)
            print("saved=" + cell.cell_id + " time: " + str(time.time() - start_time))
            start_time = time.time()
            status='processing'
            set_status(id, cell.cell_metadata_table, conn, status, id_type='cell_id')
        if status=='processing':
            process(cell, engine, conn)
        set_status(id, cell.cell_metadata_table, conn, status='completed', id_type='cell_id')
        clear_buffer(id, cell.buffer_table, conn, id_type='cell_id')

def update_cell_data(engine, conn:str, cells_to_import:list[ba.AbstractCell]):
    for cell in cells_to_import:
        id = cell.cell_id
        status = get_status(id, cell.cell_metadata_table, conn, id_type='cell_id')
        if status == 'completed':
            status = 'buffering'
            set_status(id, cell.cell_metadata_table, conn, status, id_type='cell_id')
        if status == 'new':
            add_cell_data(engine, conn, cells_to_import)
        if status == 'buffering':
            logging.info('adding files')
            start_time = time.time()
            df_ts = buffer(cell, get_file_type_obj(cell.tester))
            df_ts.to_sql(cell.buffer_table, con=engine, if_exists='append', chunksize=1000, index=False)
            print("saved=" + cell.cell_id + " time: " + str(time.time() - start_time))
            start_time = time.time()
            #remove old data
            delete_data(conn, tables_to_delete=(cell.timeseries_table,cell.stats_table), cells_to_delete=[cell], id_type='cell_id')
            status='processing'
            set_status(id, cell.cell_metadata_table, conn, status, id_type='cell_id')
        if status=='processing':
            process(cell, engine, conn)
        set_status(id, cell.cell_metadata_table, conn, status='completed', id_type='cell_id')
        clear_buffer(id, cell.buffer_table, conn, id_type='cell_id')

def buffer(cell:ba.AbstractCell, file_type_obj:ba.AbstractFileType) -> pd.DataFrame:
    #if file type
    print('Buffering...')
    # list of timeseries files, excluding hidden files
    list_ts_fldr = [file for file in pathlib.Path(cell.file_path).glob('./*') if not any(part.startswith('.') for part in file.parts)]
    #check if enough files exist (more than 1)
    for i in range(len(list_ts_fldr)):
        print(list_ts_fldr[i])
    for file_path in list_ts_fldr:
        df_ts = pd.DataFrame() #df to send to database
        try:
            df_ts_file, sheetname = file_type_obj.file_to_df(file_path)#order to do this??
        except ValueError as e:
            print('\nI got a ValueError - reason: ' + str(e))
            print('Make sure metadata and data files (and hidden files) are closed. \n')
        try:
            keys = {'cycle_index','i','v','date_time','test_time','env_temperature','cell_temperature'}
            for key in keys:
                if key in file_type_obj.col_mapping:
                    df_ts[key] = df_ts_file[file_type_obj.col_mapping[key]]
                if 'date_time' == key and 'test_time' not in file_type_obj.col_mapping:
                    df_ts['test_time'] = file_type_obj.datetime_to_testtime(df_ts_file)
                elif 'test_time' not in file_type_obj.col_mapping and 'date_time' not in file_type_obj.col_mapping:#change to check if all necessary columns exist
                    #exit code
                    print('There is no time data in the timeseries file.')
            df_ts['cell_id'] = cell.cell_id
            df_ts['sheetname'] = cell.file_id + "|" + sheetname
            df_ts['component_level'] = 'cell'
            cycle_index_file_max = df_ts['cycle_index'].max()

            print('saving sheet: ' + sheetname + ' with max cycle: ' +str(cycle_index_file_max))

        except KeyError as e:
            print("I got a KeyError - reason " + str(e))
            print("processing:" + sheetname)
    return df_ts

def process(cell:ba.AbstractCell, engine:Engine, conn:str):
    print('Processing...')
    chunk_size = 30 #number of cells to process at once
    cycle_index_max = get_cycle_index_max(conn, cell.buffer_table, cell.cell_id)
    cycle_stats_index_max = get_cycle_index_max(conn, cell.stats_table, cell.cell_id)
    start_cycle = 1
    start_time = time.time()
    for i in range(cycle_index_max+1):
        if (i-1) % chunk_size == 0 and i > 0 and i>cycle_stats_index_max:
            start_cycle = i
            end_cycle = start_cycle + chunk_size - 1
            sql_cell =  " cell_id='" + cell.cell_id + "'" 
            sql_cycle = " and cycle_index>=" + str(start_cycle) + " and cycle_index<=" + str(end_cycle)
            sql_str = text("select * from "+ cell.buffer_table + " where" + sql_cell + sql_cycle + " order by test_time")
            print(sql_str)
            with engine.begin() as connection:
                df_ts = pd.read_sql(sql_str, connection)

                df_ts.drop('sheetname', axis=1, inplace=True)

                if not df_ts.empty:
                    start_time = time.time()
                    df_cycle_stats = cell.calc_cycle(df_ts, engine)
                    df_cycle_timeseries = cell.calc_timeseries(df_ts)
                    print("calc_stats time: " + str(time.time() - start_time))
                    logging.info("calc_stats time: " + str(time.time() - start_time))

                    start_time = time.time()
                    df_cycle_stats.to_sql(cell.stats_table, con=engine, if_exists='append', chunksize=1000, index=False)
                    print("save stats time: " + str(time.time() - start_time))
                    logging.info("save stats time: " + str(time.time() - start_time))

                    start_time = time.time()
                    df_cycle_timeseries.to_sql(cell.timeseries_table, con=engine, if_exists='append', chunksize=1000, index=False)
                    print("save timeseries time: " + str(time.time() - start_time))
                    logging.info("save timeseries time: " + str(time.time() - start_time))

def clear_buffer(id:str, buffer_table:str, conn:str, id_type:str):
    # this method will delete data for a cell_id. Use with caution as there is no undo
    db_conn = psycopg2.connect(conn)
    curs = db_conn.cursor()
    curs.execute("delete from " + buffer_table + " where " + id_type + "='" + id + "'")
    db_conn.commit()
    curs.close()
    db_conn.close()

def get_status(id:str, md_table:str, conn:str, id_type:str) -> str:
    sql_str = "select status from " + md_table + " where " + id_type + "= '" + id + "'"
    db_conn = psycopg2.connect(conn)
    curs = db_conn.cursor()
    curs.execute(sql_str)
    db_conn.commit()
    record = curs.fetchall()
    if record:
        status = record[0][0]
    else:
        status = 'new'
    print('cell status is: ' + status)
    return status

def set_status(id:str, md_table:str, conn:str, status:str, id_type:str):
    sql_str = "update " + md_table + " set status = '" + status + "' where " + id_type + "= '" + id + "'"
    db_conn = psycopg2.connect(conn)
    curs = db_conn.cursor()
    curs.execute(sql_str)
    db_conn.commit()
    curs.close()
    db_conn.close()

def get_cycle_index_max(conn:str, table:str, id:str) -> int:
    #gets max cycle from database
    sql_str = "select max(cycle_index)::int as max_cycles from " + table + " where cell_id = '" + id + "'"
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

def get_file_type_obj(tester:str) -> ba.AbstractFileType:
    #make this nicer in future
    if tester == 'arbin':
        return ba.Arbin()
    elif tester == 'matlab':
        return ba.Matlab()
    elif tester == 'generic': ##this is not ideal, but all previous metadata uses 'generic'
        return ba.Uconn()
    elif tester == 'csv':
        return ba.Ezbatt()
    elif tester == 'voltaiq':
        return ba.Maccor()

def delete_data(conn:str, tables_to_delete:list[str], cells_to_delete:list[ba.AbstractCell], id_type:str):
    # this method will delete data for a cell_id. Use with caution as there is no undo
    print('Deleting...')
    all_strs = ''
    for cell in cells_to_delete:
        for table in tables_to_delete:
            sql_str = "delete from " + table + " where " + id_type + "='" + cell.cell_id + "';\n"
            all_strs = all_strs + sql_str
    print(all_strs)
    db_conn = psycopg2.connect(conn)
    curs = db_conn.cursor()
    curs.execute(all_strs)
    db_conn.commit()
    curs.close()
    db_conn.close()

def main(argv:list[str]):

    # command line variables that can be used to run from an IDE without passing arguments
    mode = 'env'
    path = r'\\'

    # initializing the logger
    logging.basicConfig(format='%(asctime)s %(message)s', filename='blc-python.log', level=logging.DEBUG)
    logging.info('starting')

    #read command line
    try:
        opts_and_args, args = getopt.getopt(argv, "hi:t:p:", ["importType=","dataType=","path="])
    except getopt.GetoptError:
        print('run as: importer.py -i <importType> -t <dataType> -p <path>')
        sys.exit(2)
    opts = [opt for opt,arg in opts_and_args]
    for opt, arg in opts_and_args:
        if opt == '-h':
            print('run as: importer.py -i <importType> -t <dataType> -p <path>')
            sys.exit()
        elif opt in ("-i", "importType"):
            import_type = arg
        elif opt in ("-p", "--path"):
            path = arg
        elif opt in ("-t", "--dataType"):
            data_type = arg
    if "-i" not in opts:
        print("Defaulting to adding data.")
        import_type = 'add'

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

    #are these used?
    plot = data['environment']['PLOT']
    save = data['environment']['SAVE']
    style = data['environment']['STYLE']

    # use default if env file not there
    if conn == '':
        conn = data['environment']['DATABASE_CONNECTION']


    logging.info('command line: ' + str(opts))
    logging.info('configuration: ' + str(data))

    #create engine
    engine = create_engine(conn)

    if data_type == 'li-cell':
        md = pd.read_excel(pathlib.PurePath(path).joinpath("cell_list.xlsx"))
        cells_to_import = [ba.LithiumCell(path,row) for ind, row in md.iterrows()]
        if import_type == 'add':
            add_cell_data(engine, conn, cells_to_import)
        elif import_type == 'update':
            update_cell_data(engine, conn, cells_to_import)
    elif data_type == 'flow-cell':
        md = pd.read_excel(pathlib.PurePath(path).joinpath("cell_list.xlsx"))
        cells_to_import = [ba.FlowCell(path, row) for ind, row in md.iterrows()]
        add_cell_data(engine, conn, cells_to_import)
    elif data_type == 'li-module':
        md = pd.read_excel(pathlib.PurePath(path).joinpath("module_list.xlsx"))
        modules_to_import = [ba.LithiumModule(path, row) for ind, row in md.iterrows()]
        add_module_stack_data(engine, conn, modules_to_import)
    return

if __name__ == "__main__":
    main(sys.argv[1:])
