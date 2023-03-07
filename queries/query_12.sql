/*
Name: Filters: Min State of Charge
Data source: 1
Created By: admin
Last Update At: 2022-05-31T21:05:35.449Z
Visualizations: [{'id': 12, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:02.310Z', 'created_at': '2022-05-31T19:26:02.310Z'}, {'id': 46, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:04.008Z', 'created_at': '2022-05-31T19:26:04.008Z'}]
*/

select distinct soc_min as a, count(*) from cycle_metadata group by a order by a