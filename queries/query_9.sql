/*
Name: Filters: C charge Rate
Data source: 1
Created By: admin
Last Update At: 2022-05-31T21:05:16.458Z
Visualizations: [{'id': 9, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:02.097Z', 'created_at': '2022-05-31T19:26:02.097Z'}, {'id': 41, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:03.806Z', 'created_at': '2022-05-31T19:26:03.806Z'}]
*/

select distinct crate_c as a, count(*) from cycle_metadata group by a order by a