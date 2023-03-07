/*
Name: Filters: testers abuse test
Data source: 1
Created By: admin
Last Update At: 2022-10-18T21:17:55.296Z
Visualizations: [{'id': 82, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-10-18T21:17:20.667Z', 'created_at': '2022-10-18T21:17:20.667Z'}, {'id': 83, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-10-18T21:17:20.667Z', 'created_at': '2022-10-18T21:17:20.667Z'}]
*/

select distinct tester as a, count(*) from cell_metadata where test = 'abuse' group by a order by a