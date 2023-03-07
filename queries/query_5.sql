/*
Name: Filters: Cycle Cells Nominal Capacity (Ah)
Data source: 1
Created By: admin
Last Update At: 2022-10-18T20:19:01.708Z
Visualizations: [{'id': 5, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:01.806Z', 'created_at': '2022-05-31T19:26:01.806Z'}, {'id': 59, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:04.563Z', 'created_at': '2022-05-31T19:26:04.563Z'}]
*/

select distinct ah as a, count(*) from cell_metadata where test = 'cycle' group by a order by a