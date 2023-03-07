/*
Name: Filters: Source abuse test
Data source: 1
Created By: admin
Last Update At: 2022-10-18T21:14:56.553Z
Visualizations: [{'id': 80, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-10-18T21:12:38.472Z', 'created_at': '2022-10-18T21:12:38.472Z'}, {'id': 81, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-10-18T21:12:38.472Z', 'created_at': '2022-10-18T21:12:38.472Z'}]
*/

select distinct source as a, count(*) from cell_metadata where test = 'abuse' group by a order by a 