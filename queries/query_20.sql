/*
Name: Disruptive Test: Force
Data source: 1
Created By: admin
Last Update At: 2022-12-31T17:37:17.343Z
Visualizations: [{'id': 20, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:02.810Z', 'created_at': '2022-05-31T19:26:02.810Z'}, {'id': 35, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:03.630Z', 'created_at': '2022-05-31T19:26:03.630Z'}, {'id': 34, 'type': 'CHART', 'name': 'Force', 'description': '', 'options': {'globalSeriesType': 'scatter', 'sortX': True, 'legend': {'enabled': True, 'placement': 'auto', 'traceorder': 'normal'}, 'xAxis': {'type': '-', 'labels': {'enabled': True}, 'title': {'text': 'Time (s)'}}, 'yAxis': [{'type': 'linear', 'title': {'text': 'Force (N)'}}, {'type': 'linear', 'opposite': True}], 'alignYAxesAtZero': True, 'error_y': {'type': 'data', 'visible': True}, 'series': {'stacking': None, 'error_y': {'type': 'data', 'visible': True}}, 'seriesOptions': {}, 'valuesOptions': {}, 'columnMapping': {'test_time': 'x', 'value': 'y', 'series': 'series'}, 'direction': {'type': 'counterclockwise'}, 'sizemode': 'diameter', 'coefficient': 1, 'numberFormat': '0,0[.]00000', 'percentFormat': '0[.]00%', 'textFormat': '', 'missingValuesAsZero': True, 'showDataLabels': False, 'dateTimeFormat': 'DD/MM/YY HH:mm', 'swappedAxes': False}, 'updated_at': '2022-12-31T00:59:37.074Z', 'created_at': '2022-05-31T19:26:03.595Z'}]
*/

SELECT KEY || ': ' || r.cell_id AS series,
              r.test_time,
              value
FROM
  (SELECT abuse_timeseries.cell_id,
          test_time,
          json_build_object(
            'F', axial_f,
            'D', axial_d
        ) AS line
   FROM abuse_timeseries TABLESAMPLE BERNOULLI (10)
   WHERE cell_id IN ({{cell_id}})) AS r
JOIN LATERAL json_each_text(r.line) ON (KEY ~ '[F,D]')
where cast(value as decimal) <> '0' 
ORDER BY r.cell_id,
         r.test_time,
         KEY