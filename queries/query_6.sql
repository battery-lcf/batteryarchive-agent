/*
Name: Filters: Source cycle test
Data source: 1
Created By: admin
Last Update At: 2023-01-09T19:16:14.379Z
Visualizations: [{'id': 6, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:01.876Z', 'created_at': '2022-05-31T19:26:01.876Z'}, {'id': 61, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:04.623Z', 'created_at': '2022-05-31T19:26:04.623Z'}]
*/

select distinct source as a, count(*) from cell_metadata where test = 'cycle' and source <> 'commercial' group by a order by a 