/*
Name: Abuse Test Temperatures
Data source: 1
Created By: admin
Last Update At: 2022-03-12T20:37:57.250Z
Visualizations: [{'id': 25, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-03-06T00:49:15.089Z', 'created_at': '2022-02-27T21:57:12.725Z'}, {'id': 52, 'type': 'CHART', 'name': 'Chart', 'description': '', 'options': {'globalSeriesType': 'line', 'sortX': True, 'legend': {'enabled': True, 'placement': 'auto', 'traceorder': 'normal'}, 'xAxis': {'type': '-', 'labels': {'enabled': True}, 'title': {'text': 'Time (s)'}}, 'yAxis': [{'type': 'linear', 'title': {'text': 'Temperature (T)'}}, {'type': 'linear', 'opposite': True}], 'alignYAxesAtZero': False, 'error_y': {'type': 'data', 'visible': True}, 'series': {'stacking': None, 'error_y': {'type': 'data', 'visible': True}}, 'seriesOptions': {}, 'valuesOptions': {}, 'columnMapping': {'test_time': 'x', 'value': 'y', 'series_1': 'series'}, 'direction': {'type': 'counterclockwise'}, 'sizemode': 'diameter', 'coefficient': 1, 'numberFormat': '0,0[.]00000', 'percentFormat': '0[.]00%', 'textFormat': '', 'missingValuesAsZero': False, 'showDataLabels': False, 'dateTimeFormat': 'DD/MM/YY HH:mm', 'swappedAxes': False}, 'updated_at': '2022-03-12T20:38:54.977Z', 'created_at': '2022-03-12T20:05:26.441Z'}]
*/


SELECT KEY || ': ' || r.cell_id AS series_1,
KEY || ': ' || r.cell_id AS series_2,
              r.test_time,
              value
FROM
  (SELECT abuse_timeseries.cell_id,
          test_time,
          json_build_object(
            'Tbp',below_punch_temperature,   
            'Tap', above_punch_temperature,
            'Tlb', left_bottom_temperature, 
            'Trb', right_bottom_temperature,
            'Tpt', pos_terminal_temperature,
            'Tnp', neg_terminal_temperature
        ) AS line
   FROM abuse_timeseries TABLESAMPLE BERNOULLI ({{sample}})
   WHERE cell_id IN ({{cell_id}})) AS r
JOIN LATERAL json_each_text(r.line) ON (KEY ~ '[Tbp,Tap,Tlb,Trb,Tpt,Tnp]')
where value <> '0' 
ORDER BY r.cell_id,
         r.test_time,
         KEY