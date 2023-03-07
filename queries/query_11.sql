/*
Name: Filters: Max State of Charge
Data source: 1
Created By: admin
Last Update At: 2022-05-31T21:05:27.436Z
Visualizations: [{'id': 11, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:02.236Z', 'created_at': '2022-05-31T19:26:02.236Z'}, {'id': 47, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:04.037Z', 'created_at': '2022-05-31T19:26:04.037Z'}]
*/

select distinct soc_max as a, count(*) from cycle_metadata group by a order by a