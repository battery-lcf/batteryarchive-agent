/*
Name: Abuse Force and Displacement
Data source: 1
Created By: admin
Last Update At: 2022-03-12T20:32:11.223Z
Visualizations: [{'id': 54, 'type': 'CHART', 'name': 'Force and Displacement', 'description': '', 'options': {'globalSeriesType': 'scatter', 'sortX': True, 'legend': {'enabled': True, 'placement': 'auto', 'traceorder': 'normal'}, 'xAxis': {'type': '-', 'labels': {'enabled': True}, 'title': {'text': 'Time (s)'}}, 'yAxis': [{'type': 'linear', 'title': {'text': 'Force (N) / Displacement '}}, {'type': 'linear', 'opposite': True}], 'alignYAxesAtZero': True, 'error_y': {'type': 'data', 'visible': True}, 'series': {'stacking': None, 'error_y': {'type': 'data', 'visible': True}}, 'seriesOptions': {}, 'valuesOptions': {}, 'columnMapping': {'test_time': 'x', 'value': 'y', 'series': 'series'}, 'direction': {'type': 'counterclockwise'}, 'sizemode': 'diameter', 'coefficient': 1, 'numberFormat': '0,0[.]00000', 'percentFormat': '0[.]00%', 'textFormat': '', 'missingValuesAsZero': True, 'showDataLabels': False, 'dateTimeFormat': 'DD/MM/YY HH:mm', 'swappedAxes': False}, 'updated_at': '2022-03-12T20:39:10.143Z', 'created_at': '2022-03-12T20:15:33.818Z'}, {'id': 53, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-03-12T20:14:41.826Z', 'created_at': '2022-03-12T20:14:41.826Z'}]
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
   FROM abuse_timeseries TABLESAMPLE BERNOULLI ({{sample}})
   WHERE cell_id IN ({{cell_id}})) AS r
JOIN LATERAL json_each_text(r.line) ON (KEY ~ '[F,D]')
where value <> '0' 
ORDER BY r.cell_id,
         r.test_time,
         KEY