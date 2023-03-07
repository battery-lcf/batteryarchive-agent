/*
Name: Compare Cycle Voltage and Current
Data source: 1
Created By: admin
Last Update At: 2022-05-31T21:24:56.366Z
Visualizations: [{'id': 27, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:03.197Z', 'created_at': '2022-05-31T19:26:03.197Z'}, {'id': 63, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:04.738Z', 'created_at': '2022-05-31T19:26:04.738Z'}, {'id': 64, 'type': 'CHART', 'name': 'Compare by Cycle Time', 'description': '', 'options': {'globalSeriesType': 'line', 'sortX': True, 'legend': {'enabled': True, 'placement': 'auto', 'traceorder': 'normal'}, 'xAxis': {'type': '-', 'labels': {'enabled': True}, 'title': {'text': 'Cycle time (s)'}}, 'yAxis': [{'type': 'linear', 'title': {'text': 'Voltage (V)/Current (A)'}}, {'type': 'linear', 'opposite': True}], 'alignYAxesAtZero': False, 'error_y': {'type': 'data', 'visible': True}, 'series': {'stacking': None, 'error_y': {'type': 'data', 'visible': True}}, 'seriesOptions': {}, 'valuesOptions': {}, 'columnMapping': {'cycle_time': 'x', 'value': 'y', 'series_2': 'series'}, 'direction': {'type': 'counterclockwise'}, 'sizemode': 'diameter', 'coefficient': 1, 'numberFormat': '0,0[.]00000', 'percentFormat': '0[.]00%', 'textFormat': '', 'missingValuesAsZero': True, 'showDataLabels': False, 'dateTimeFormat': 'DD/MM/YY HH:mm', 'swappedAxes': False}, 'updated_at': '2022-07-04T15:17:16.265Z', 'created_at': '2022-05-31T19:26:04.770Z'}]
*/


SELECT KEY || ': ' || r.cell_id AS series_1,
KEY || ' ' || cycle_index || ': ' || r.cell_id AS series_2,
              r.cycle_index,
              r.test_time,
              r.cycle_time,
              value
FROM
  (SELECT cycle_timeseries.cell_id,
          cycle_index,
          test_time,
          cycle_time,
          json_build_object('V', v, 'C', i) AS line
   FROM cycle_timeseries TABLESAMPLE BERNOULLI ({{sample}})
   WHERE cell_id IN ({{cell_id}})
     AND (cycle_index = {{cycle_1}} or cycle_index = {{cycle_2}})) AS r
JOIN LATERAL json_each_text(r.line) ON (KEY ~ '[V,C]')
ORDER BY r.cell_id,
         r.test_time,
         r.cycle_time,
         KEY   