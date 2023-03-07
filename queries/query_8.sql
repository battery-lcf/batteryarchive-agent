/*
Name: Filters: Temperature
Data source: 1
Created By: admin
Last Update At: 2022-05-31T21:03:22.094Z
Visualizations: [{'id': 8, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:02.028Z', 'created_at': '2022-05-31T19:26:02.028Z'}, {'id': 60, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:04.594Z', 'created_at': '2022-05-31T19:26:04.594Z'}]
*/

select distinct temperature as a, count(*) from cycle_metadata group by a order by a