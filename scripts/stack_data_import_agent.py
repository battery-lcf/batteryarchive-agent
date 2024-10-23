#!/usr/bin/env python
# coding: utf-8
import os
import argparse
import glob
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
pd.options.mode.chained_assignment = None  # default='warn'
import yaml
import sys, getopt
import logging
import logging.config
import time
from sqlalchemy import MetaData, Table
from sqlalchemy import create_engine, select, insert, update, delete, func

# Copyright 2021 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.

metadata_obj = MetaData()

def get_cycle_index_max(cell_id,engine):
    buffer_table = Table("flow_cycle_timeseries_buffer", metadata_obj, autoload_with=engine)

    stmt = select(func.max(buffer_table.c.cycle_index).label("max_cycles")).where(buffer_table.c.cell_id == cell_id)
    with engine.connect() as conn:
        result = conn.execute(stmt).first()
        conn.commit()

        if result is not None and result[0] is not None:
            print("buffer cycle_index_max: " + str(result[0]))
            return result[0]
        else:
            print("buffer cycle_index_max: 0")
            return 0


def get_cycle_stats_index_max(cell_id,engine):
    cycle_stats_table = Table("flow_cycle_stats", metadata_obj, autoload_with=engine)

    stmt = select(func.max(cycle_stats_table.c.cycle_index).label("max_cycles")).where(cycle_stats_table.c.cell_id == cell_id)
    with engine.connect() as conn:
        result = conn.execute(stmt).first()
        conn.commit()

        if result is not None and result[0] is not None:
            print("stats cycle_index_max: " + str(result[0]))
            return result[0]
        else:
            print("stats cycle_index_max: 0")
            return 0


def get_environment():
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

    return conn, plot, save, style


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
def calc_stats(df_t, ID, engine):

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
    with engine.connect() as conn:
        init = pd.read_sql("select max(e_c_cmltv) from flow_cycle_stats where cell_id='"+ID+"'", conn).iloc[0,0] #for continuity btwn calc_stats calls
        init = 0 if init == None else init
        df_c['e_c_cmltv'] = init 
        init = pd.read_sql("select max(e_d_cmltv) from flow_cycle_stats where cell_id='"+ID+"'", conn).iloc[0,0]
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
                df_f = calc_cycle_quantities(df_f)

                df_t['cycle_time'] = df_t['cycle_time'].astype('float64') #to address dtype warning
                
                df_t.loc[df_t.cycle_index == x, 'cycle_time'] = df_f['cycle_time']
                df_t.loc[df_t.cycle_index == x, 'ah_c'] = df_f['ah_c']
                df_t.loc[df_t.cycle_index == x, 'e_c'] = df_f['e_c']
                df_t.loc[df_t.cycle_index == x, 'ah_d'] = df_f['ah_d']
                df_t.loc[df_t.cycle_index == x, 'e_d'] = df_f['e_d']
                df_t.loc[df_t.cycle_index == x, 'w'] = df_f['i'] * df_f['v'] #power

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
    df_tt = df_t[df_t['cycle_index'] > 0]

    return df_cc, df_tt


def clear_buffer(cell_id, engine):
    # Remove all data from the buffer table for the given parent id
    buffer_table = Table("flow_cycle_timeseries_buffer", metadata_obj, autoload_with=engine)
    stmt = delete(buffer_table).where(buffer_table.c.cell_id==cell_id)
    with engine.connect() as conn:
        conn.execute(stmt)


def excel_to_dataframe(excel_filename, excel_sheetname=0):
    return pd.read_excel(excel_filename, excel_sheetname)

def csv_to_dataframe(filename):
    return pd.read_csv(filename)

def import_cell_data():
    pass

def get_cell_status(cell_id, engine):
    cell_metadata_table = Table("flow_cell_metadata", metadata_obj, autoload_with=engine)
    stmt = select(cell_metadata_table.c.status).where(cell_metadata_table.c.cell_id==cell_id)
    with engine.connect() as conn:
        result = conn.execute(stmt).first()
        if result is not None:
            return result[0]
        else:
            return None

def set_cell_status(cell_id, status, engine):
    cell_metadata_table = Table("flow_cell_metadata", metadata_obj, autoload_with=engine)
    stmt = update(cell_metadata_table).where(cell_metadata_table.c.cell_id==cell_id).values(status=status)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

##maybe should rename functions and stack_id for clarity
def get_stack_status(stack_id, engine):
    stack_metadata_table = Table("stack_metadata", metadata_obj, autoload_with=engine)
    stmt = select(stack_metadata_table.c.status).where(stack_metadata_table.c.stack_id==stack_id)
    with engine.connect() as conn:
        result = conn.execute(stmt).first()
        if result is not None:
            return result[0]
        else:
            return None

def set_stack_status(stack_id, status, engine):
    stack_metadata_table = Table("stack_metadata", metadata_obj, autoload_with=engine)
    stmt = update(stack_metadata_table).where(stack_metadata_table.c.stack_id==stack_id).values(status=status)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()


def import_stack_metadata(df_stack_metadata: pd.DataFrame, stack_id: str, engine):
    stack_metadata_table = Table("stack_metadata", metadata_obj, autoload_with=engine)
    stack_status = get_stack_status(stack_id, engine)
    if stack_status is not None:
        return
    series_stack_metadata = df_stack_metadata[df_stack_metadata["stack_id"] == stack_id].iloc[0]
    with engine.connect() as conn:
        stmt = insert(stack_metadata_table).values(
            stack_id=stack_id,
            #configuration=series_stack_metadata["Configuration"],
            #num_parallel=int(series_stack_metadata["# cells in parallel"]),
            num_series=int(series_stack_metadata["# cells in series"]),
            status="buffering"
        )
        result = conn.execute(stmt)
        conn.commit()


def import_stack_cell_metadata(df_configuration: pd.DataFrame, df_stack_metadata: pd.DataFrame, stack_id: str, engine):
    cell_metadata_table = Table("flow_cell_metadata", metadata_obj, autoload_with=engine)
    cycle_metadata_table = Table("flow_cycle_metadata", metadata_obj, autoload_with=engine)
    series_stack_metadata = df_stack_metadata[df_stack_metadata["stack_id"] == stack_id].iloc[0]
    for index, row in df_configuration.iterrows():
        if row["Type"] == "Stack":
            # stacks are not added to cell metadata tables
            continue
        cell_id = "{}_{}".format(series_stack_metadata["stack_id"], row["Name"])
        # See if cell is already in the cell metadata table
        current_cell_status = get_cell_status(cell_id, engine)
        if current_cell_status is None:
            with engine.connect() as conn:
                stmt = insert(cell_metadata_table).values(
                    cell_id=cell_id,
                    flow_pattern=series_stack_metadata["flow pattern"],
                    ne_material=series_stack_metadata["NE material"],
                    pe_material=series_stack_metadata["PE material"],
                    membrane=str(series_stack_metadata["membrane"]),
                    membrane_size=float(series_stack_metadata["membrane size (cm2)"]),
                    ne_active=series_stack_metadata["NE active"],
                    initial_ne_active=float(series_stack_metadata["initial [NE active], M"]),
                    pe_active=series_stack_metadata["PE active"],
                    initial_pe_active=float(series_stack_metadata["initial [PE active], M"]),
                    ne_volume=float(series_stack_metadata["NE volume (L)"]),
                    pe_volume=float(series_stack_metadata["PE volume (L)"]),
                    flow_rate=float(series_stack_metadata['flow rate (L/min)']),
                    test_type=series_stack_metadata["test type"],
                    test=series_stack_metadata["test"],
                    tester=series_stack_metadata["tester"],
                    #source=series_stack_metadata["source"],
                    parent_id=stack_id,
                    status="buffering"
                )
                result = conn.execute(stmt)
                stmt = insert(cycle_metadata_table).values(
                    cell_id=cell_id
                )
                result = conn.execute(stmt)
                conn.commit()
                current_cell_status = "buffering"


def import_stack_data_into_buffer(df_configuration: pd.DataFrame, df_stack_data: pd.DataFrame, stack_id: str, engine):
    df_configuration.fillna(value=0, inplace=True)
    for index, row in df_configuration.iterrows():
        cell_id = "{}_{}".format(stack_id, row["Name"])
        df_cell_data = pd.DataFrame()
        if row["Type"] == "Stack":
            cell_id = stack_id
            component_level = "stack"
            if get_stack_status(stack_id, engine) != "buffering":
                continue
        else:
            component_level = "cell"
            if get_cell_status(cell_id, engine) != "buffering":
                continue
        if row["Voltage column"]:
            df_cell_data["v"] = df_stack_data[row["Voltage column"]]
        if row["Current column"]:
            df_cell_data["i"] = df_stack_data[row["Current column"]]
        if row["Internal temperature column"]:
            df_cell_data["cell_temperature"] = df_stack_data[row["Internal temperature column"]]
        if row["Ambient temperature column"]:
            df_cell_data["env_temperature"] = df_stack_data[row["Ambient temperature column"]]
        df_cell_data["date_time"] = df_stack_data[row["Timestamp column"]]
        df_cell_data["test_time"] = df_stack_data[row["Test time column"]]
        df_cell_data["cycle_index"] = df_stack_data[row["Cycle index column"]]
        df_cell_data["cell_id"] = cell_id
        df_cell_data["component_level"] = component_level
        clear_buffer(cell_id, engine)
        df_cell_data.to_sql('flow_cycle_timeseries_buffer', con=engine, if_exists='append', chunksize=1000, index=False)
        if row["Type"] == "Stack":
            set_stack_status(stack_id, "processing", engine)
        else:
            set_cell_status(cell_id, "processing", engine)

def process_stack_data(stack_id, engine):
    cell_metadata_table = Table("flow_cell_metadata", metadata_obj, autoload_with=engine)
    cells_to_process_stmt = select(cell_metadata_table.c.cell_id).where(cell_metadata_table.c.status=="processing")
    with engine.connect() as conn:
        result = conn.execute(cells_to_process_stmt)
        cells_to_process = [item[0] for item in result]
    for cell_id in cells_to_process:
        process_cell_timeseries_data(cell_id, engine)
        clear_buffer(cell_id, engine)
        set_cell_status(cell_id, "completed", engine)
    if get_stack_status(stack_id, engine) == "processing":
        process_cell_timeseries_data(stack_id, engine, "stack")
        clear_buffer(stack_id, engine)
        set_stack_status(stack_id, "completed", engine)

def process_cell_timeseries_data(cell_id, engine, component_level="cell"):
    # read the data back in chunks.
    block_size = 30
    buffer_table = Table("flow_cycle_timeseries_buffer", metadata_obj, autoload_with=engine)

    cycle_index_max = get_cycle_index_max(cell_id, engine)
    cycle_stats_index_max = get_cycle_stats_index_max(cell_id, engine)

    print("max cycle: " + str(cycle_index_max))

    start_cycle = 1
    start_time = time.time()

    for i in range(cycle_index_max+1):
        
        if (i-1) % block_size == 0 and i > 0 and i>cycle_stats_index_max:

            start_cycle = i
            end_cycle = start_cycle + block_size - 1
            query = select(buffer_table).where(
                    buffer_table.c.cell_id == cell_id, 
                    buffer_table.c.cycle_index >= start_cycle, 
                    buffer_table.c.cycle_index <= end_cycle
                ).order_by(buffer_table.c.test_time)

            print(query)
            df_ts = pd.read_sql(query, engine)

            df_ts.drop('sheetname', axis=1, inplace=True)

            if not df_ts.empty:
                start_time = time.time()
                df_cycle_stats, df_cycle_timeseries = calc_stats(df_ts, cell_id, engine)
                df_cycle_stats["component_level"] = component_level
                df_cycle_timeseries["component_level"] = component_level
                print("calc_stats time: " + str(time.time() - start_time))
                logging.info("calc_stats time: " + str(time.time() - start_time))

                start_time = time.time()
                df_cycle_stats.to_sql('flow_cycle_stats', con=engine, if_exists='append', chunksize=1000, index=False)
                print("save stats time: " + str(time.time() - start_time))
                logging.info("save stats time: " + str(time.time() - start_time))

                start_time = time.time()
                df_cycle_timeseries.to_sql('flow_cycle_timeseries', con=engine, if_exists='append', chunksize=1000, index=False)
                print("save timeseries time: " + str(time.time() - start_time))
                logging.info("save timeseries time: " + str(time.time() - start_time))


def import_all_stack_data(df_stack_metadata, base_filepath, engine):
    for index, row in df_stack_metadata.iterrows():
        file_id = row["file_id"]
        stack_id = row["stack_id"]
        stack_path = os.path.join(base_filepath, file_id)
        configuration_file = os.path.join(stack_path, f"{file_id}.xlsx")
        data_files = glob.glob(os.path.join(stack_path, f"*.xlsx"))
        # Filter out configuration files
        data_files = [file for file in data_files if file_id not in os.path.basename(file) and "~$" not in os.path.basename(file)]
        if not os.path.exists(configuration_file) or len(data_files) != 1:
            # Note: currently only support one sheet of data
            logging.warning(f"Could not find both configuration and data files for stack {stack_id}")
            logging.warning(f"Skipping stack...")
            continue
        df_configuration = excel_to_dataframe(configuration_file)
        xl_stack_data = pd.ExcelFile(data_files[0])
        sheetname = None
        for sheet in xl_stack_data.sheet_names:
            if "Channel" in sheet and "Chart" not in sheet:
                sheetname = sheet
        sheetname="160mA 6lpm Data" ##TODO fix sheetname
        df_stack_data = excel_to_dataframe(data_files[0], sheetname)
        logging.info(f"Importing data for stack {stack_id}")
        print("importing metadata")
        import_stack_metadata(df_stack_metadata, stack_id, engine)
        import_stack_cell_metadata(df_configuration, df_stack_metadata, stack_id, engine)
        print("importing into buffer")
        import_stack_data_into_buffer(df_configuration, df_stack_data, stack_id, engine)
        print("processing")
        process_stack_data(stack_id, engine)


if __name__ == "__main__":
    
    # initializing the logger
    logging.basicConfig(format='%(asctime)s %(message)s', filename='blc-python.log', level=logging.DEBUG)
    logging.info('starting')

    parser = argparse.ArgumentParser(
        prog="flow_stack_data_import_agent",
        description="Imports flow stack data into Battery Archive",
    )
    parser.add_argument('stack_list')
    args = parser.parse_args()

    stack_metadata_file = args.stack_list + 'stack_list.xlsx'
    conn, plot, save, style = get_environment()
    engine = create_engine(conn)
    df_stack_metadata = excel_to_dataframe(stack_metadata_file)

    import_all_stack_data(df_stack_metadata, os.path.dirname(stack_metadata_file), engine)