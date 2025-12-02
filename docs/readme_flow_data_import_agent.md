# Flow Data Import Agent Breakdown
The flow importer contains most of the same functions as the original data_import_agent.py script. There are only two types of supported flow data in the current script: csv and arbin. Some of the functions are changed to accomodate the different metadata columns and timeseries data columns. 

## Function List
| Function | Description |
| -------- | ----------- |
|calc_cycle_quantities(df):| Calculates certain quantities to be used in calc_stats()
|calc_stats(df_t, ID):| Calculates statistics for each cycle, in chunks of 30 cycles per call
|read_save_timeseries(cell_id, file_path):| Loads arbin-type data files into the buffer table
|read_save_timeseries_generic(cell_id, file_path, source, engine, conn):| Loads csv files in to the buffer table
|populate_cycle_metadata(df_c_md):| Loads metadata into the cell and cycle metadata tables
|clear_buffer(cell_id, conn):| Clears the buffer table once all data is processed.
|set_cell_status(cell_id, status, conn):| Updates the status of the cell (i.e. new, buffering, processing, completed)
|get_cycle_index_max(cell_id,conn):| Gets the current/largest cycle index from the buffer table.
|get_cycle_stats_index_max(cell_id,conn):| Gets the current/largest cycle index from the stats table.
|check_cell_status(cell_id,conn):| Gets the status of the cell (i.e. new, buffering, processing, completed) |
|buffered_sheetnames(cell_id, conn): | Gets the sheetnames in the buffered file. Used in arbin function |
|add_ts_md_cycle(cell_list, conn, save, plot, path, slash):| Import new data file(s) by checking the status and calling the appropriate function for the data type. Saves the data from the buffer to the timeseries table.
|main(argv):| Sets up command line run capability


```python

```
