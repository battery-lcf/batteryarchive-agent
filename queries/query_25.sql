/*
Name: Disruptive Test: Temperatures
Data source: 1
Created By: admin
Last Update At: 2022-12-31T17:38:09.303Z
Visualizations: [{'id': 25, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:03.090Z', 'created_at': '2022-05-31T19:26:03.090Z'}, {'id': 54, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:04.348Z', 'created_at': '2022-05-31T19:26:04.348Z'}, {'id': 55, 'type': 'CHART', 'name': 'Chart', 'description': '', 'options': {'globalSeriesType': 'line', 'sortX': True, 'legend': {'enabled': True, 'placement': 'auto', 'traceorder': 'normal'}, 'xAxis': {'type': '-', 'labels': {'enabled': True}, 'title': {'text': 'Time (s)'}}, 'yAxis': [{'type': 'linear', 'title': {'text': 'Temperature (C)'}}, {'type': 'linear', 'opposite': True}], 'alignYAxesAtZero': False, 'error_y': {'type': 'data', 'visible': True}, 'series': {'stacking': None, 'error_y': {'type': 'data', 'visible': True}}, 'seriesOptions': {'Tnp: ORNL_Abuse': {'zIndex': 3, 'index': 0, 'type': 'line', 'yAxis': 0}, 'Tnp: SNL_Abuse': {'zIndex': 9, 'index': 0, 'type': 'line', 'yAxis': 0}, 'Tlb: ORNL_Abuse': {'zIndex': 2, 'index': 0, 'type': 'line', 'yAxis': 0}, 'Tap: SNL_Abuse': {'zIndex': 6, 'index': 0, 'type': 'line', 'yAxis': 0}, 'Trb: SNL_Abuse': {'zIndex': 11, 'index': 0, 'type': 'line', 'yAxis': 0}, 'Tbp: SNL_Abuse': {'zIndex': 7, 'index': 0, 'type': 'line', 'yAxis': 0}, 'Trb: ORNL_Abuse': {'zIndex': 5, 'index': 0, 'type': 'line', 'yAxis': 0}, 'Tap: ORNL_Abuse': {'zIndex': 0, 'index': 0, 'type': 'line', 'yAxis': 0}, 'Tpt: SNL_Abuse': {'zIndex': 10, 'index': 0, 'type': 'line', 'yAxis': 0}, 'Tlb: SNL_Abuse': {'zIndex': 8, 'index': 0, 'type': 'line', 'yAxis': 0}, 'Tpt: ORNL_Abuse': {'zIndex': 4, 'index': 0, 'type': 'line', 'yAxis': 0}, 'Tbp: ORNL_Abuse': {'zIndex': 1, 'index': 0, 'type': 'line', 'yAxis': 0}}, 'valuesOptions': {}, 'columnMapping': {'test_time': 'x', 'value': 'y', 'series_1': 'series'}, 'direction': {'type': 'counterclockwise'}, 'sizemode': 'diameter', 'coefficient': 1, 'numberFormat': '0,0[.]00000', 'percentFormat': '0[.]00%', 'textFormat': '', 'missingValuesAsZero': False, 'showDataLabels': False, 'dateTimeFormat': 'DD/MM/YY HH:mm', 'swappedAxes': False, 'customCode': '// Available variables are x, ys, element, and Plotly\n// Type console.log(x, ys); for more info about x and ys\n// To plot your graph call Plotly.plot(element, ...)\n// Plotly examples and docs: https://plot.ly/javascript/'}, 'updated_at': '2022-12-31T01:00:24.551Z', 'created_at': '2022-05-31T19:26:04.381Z'}]
*/

SELECT KEY || ': ' || r.cell_id AS series_1,
KEY || ': ' || r.cell_id AS series_2,
              r.test_time,
              value
FROM
  (SELECT abuse_timeseries.cell_id,
          test_time,
          json_build_object(
            'Top_Indent', top_indent_temperature,   
            'Top_Back', top_back_temperature,
            'Left_Bottom', left_bottom_temperature, 
            'Right_Bottom', right_bottom_temperature,
            'Above_Punch', above_punch_temperature,
            'Below_Punch', below_punch_temperature
        ) AS line
   FROM abuse_timeseries TABLESAMPLE BERNOULLI (10)
   WHERE cell_id IN ({{cell_id}})) AS r
JOIN LATERAL json_each_text(r.line) ON (KEY ~ '[Top_Indent,Top_Back,Left_Bottom,Right_Bottom,Above_Punch,Below_Punch]')
where value <> '0.0' 
ORDER BY r.cell_id,
         r.test_time,
         KEY