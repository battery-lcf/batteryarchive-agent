/*
Name: Filters: Abuse Cells Nominal Capacity (Ah)
Data source: 1
Created By: admin
Last Update At: 2022-09-07T22:05:10.544Z
Visualizations: [{'id': 76, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-09-07T22:04:22.584Z', 'created_at': '2022-09-07T22:04:22.584Z'}, {'id': 77, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-09-07T22:04:22.584Z', 'created_at': '2022-09-07T22:04:22.584Z'}]
*/

select distinct ah as a, count(*) from cell_metadata where test = 'abuse' group by a order by a