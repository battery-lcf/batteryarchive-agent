/*
Name: Charge voltage by step
Data source: 1
Created By: admin
Last Update At: 2022-07-25T05:25:48.665Z
Visualizations: [{'id': 72, 'type': 'CHART', 'name': 'Chart', 'description': '', 'options': {'globalSeriesType': 'line', 'sortX': True, 'legend': {'enabled': True, 'placement': 'auto', 'traceorder': 'normal'}, 'xAxis': {'type': '-', 'labels': {'enabled': True}, 'title': {'text': 'Cycle Time (s)'}}, 'yAxis': [{'type': 'linear', 'title': {'text': 'Voltage (V)'}}, {'type': 'linear', 'opposite': True}], 'alignYAxesAtZero': False, 'error_y': {'type': 'data', 'visible': True}, 'series': {'stacking': None, 'error_y': {'type': 'data', 'visible': True}}, 'seriesOptions': {}, 'valuesOptions': {}, 'columnMapping': {'cycle_time': 'x', 'v': 'y', 'label': 'series'}, 'direction': {'type': 'counterclockwise'}, 'sizemode': 'diameter', 'coefficient': 1, 'numberFormat': '0,0[.]00000', 'percentFormat': '0[.]00%', 'textFormat': '', 'missingValuesAsZero': True, 'showDataLabels': False, 'dateTimeFormat': 'DD/MM/YY HH:mm', 'swappedAxes': False}, 'updated_at': '2022-07-25T04:58:36.801Z', 'created_at': '2022-07-11T02:07:14.507Z'}, {'id': 70, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-07-11T02:07:14.507Z', 'created_at': '2022-07-11T02:07:14.507Z'}, {'id': 71, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-07-11T02:07:14.507Z', 'created_at': '2022-07-11T02:07:14.507Z'}]
*/

SELECT t.*
FROM (
  SELECT cell_id, cycle_time, v, cell_id  || ' ' || cycle_index as label, row_number() OVER(ORDER BY cell_id, test_time ASC) AS row
  FROM cycle_timeseries where cell_id IN ({{cell_id}}) and (cycle_index = {{Step_1}} or cycle_index = {{Step_2}} or cycle_index = {{Step_3}}) and i>0 
) t
WHERE t.row % (select step from cycle_metadata where cell_id = t.cell_id) = 0