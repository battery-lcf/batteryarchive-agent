/*
Name: Energy and Capacity Decay
Data source: 1
Created By: admin
Last Update At: 2022-12-31T14:42:58.843Z
Visualizations: [{'id': 26, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:03.144Z', 'created_at': '2022-05-31T19:26:03.144Z'}, {'id': 57, 'type': 'CHART', 'name': 'Time Series Data', 'description': '', 'options': {'globalSeriesType': 'scatter', 'sortX': True, 'legend': {'enabled': True, 'placement': 'auto', 'traceorder': 'normal'}, 'xAxis': {'type': '-', 'labels': {'enabled': True}, 'title': {'text': 'Time (s)'}}, 'yAxis': [{'type': 'linear', 'title': {'text': 'Wh/Ah'}}, {'type': 'linear', 'opposite': True}], 'alignYAxesAtZero': False, 'error_y': {'type': 'data', 'visible': True}, 'series': {'stacking': None, 'error_y': {'type': 'data', 'visible': True}}, 'seriesOptions': {}, 'valuesOptions': {}, 'columnMapping': {'test_time': 'x', 'value': 'y', 'series': 'series'}, 'direction': {'type': 'counterclockwise'}, 'sizemode': 'diameter', 'coefficient': 1, 'numberFormat': '0,0[.]00000', 'percentFormat': '0[.]00%', 'textFormat': '', 'missingValuesAsZero': True, 'showDataLabels': False, 'dateTimeFormat': 'DD/MM/YY HH:mm', 'swappedAxes': False}, 'updated_at': '2022-05-31T19:26:05.163Z', 'created_at': '2022-05-31T19:26:04.497Z'}, {'id': 56, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:04.466Z', 'created_at': '2022-05-31T19:26:04.466Z'}, {'id': 58, 'type': 'CHART', 'name': 'Cycle Index Data', 'description': '', 'options': {'globalSeriesType': 'line', 'sortX': True, 'legend': {'enabled': True, 'placement': 'auto', 'traceorder': 'normal'}, 'xAxis': {'type': '-', 'labels': {'enabled': True}, 'title': {'text': 'Cycle Index'}}, 'yAxis': [{'type': 'linear', 'title': {'text': 'Ah/Wh'}}, {'type': 'linear', 'opposite': True}], 'alignYAxesAtZero': False, 'error_y': {'type': 'data', 'visible': True}, 'series': {'stacking': None, 'error_y': {'type': 'data', 'visible': True}}, 'seriesOptions': {}, 'valuesOptions': {}, 'columnMapping': {'cycle_index': 'x', 'value': 'y', 'series': 'series'}, 'direction': {'type': 'counterclockwise'}, 'sizemode': 'diameter', 'coefficient': 1, 'numberFormat': '0,0[.]00000', 'percentFormat': '0[.]00%', 'textFormat': '', 'missingValuesAsZero': True, 'showDataLabels': False, 'dateTimeFormat': 'DD/MM/YY HH:mm', 'swappedAxes': False}, 'updated_at': '2022-05-31T19:26:04.982Z', 'created_at': '2022-05-31T19:26:04.531Z'}]
*/

SELECT
   key || ': ' || r.cell_id as series,
   r.cycle_index,
   r.test_time,
   value
FROM (SELECT cell_id, trunc(cycle_index,0) as cycle_index, test_time, json_build_object('e_d', e_d, 'ah_d', ah_d, 'e_c', e_c, 'ah_c', ah_c ) AS line 
FROM cycle_stats
where cell_id IN ({{cell_id}}) and ah_eff<1.1) as r
JOIN LATERAL json_each_text(r.line) ON (key ~ '[e,ah]_[d,c]')
where cast(value as numeric)!=0
GROUP by r.cell_id, r.cycle_index,  r.test_time, json_each_text.key, json_each_text.value      
order by r.cell_id,r.cycle_index, key    
