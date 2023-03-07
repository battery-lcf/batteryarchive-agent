/*
Name: Filters: Cathode cycle test
Data source: 1
Created By: admin
Last Update At: 2022-10-18T20:30:05.978Z
Visualizations: [{'id': 3, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:01.679Z', 'created_at': '2022-05-31T19:26:01.679Z'}, {'id': 51, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:04.210Z', 'created_at': '2022-05-31T19:26:04.210Z'}]
*/

select distinct cathode as a, count(*) from cell_metadata where test = 'cycle' group by a order by a