/*
Name: Filters: C Discharge Rate
Data source: 1
Created By: admin
Last Update At: 2022-05-31T21:05:22.273Z
Visualizations: [{'id': 10, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:02.173Z', 'created_at': '2022-05-31T19:26:02.173Z'}, {'id': 50, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:04.180Z', 'created_at': '2022-05-31T19:26:04.180Z'}]
*/

select distinct crate_d as a, count(*) from cycle_metadata group by a order by a