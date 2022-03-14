/*
Name: Filters: Temperature
Data source: 1
Created By: admin
Last Update At: 2022-03-12T16:18:46.880Z
Visualizations: [{'id': 22, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-02-27T21:57:12.008Z', 'created_at': '2022-02-27T21:57:12.008Z'}]
*/
select distinct temperature as a, count(*) from cycle_metadata group by a order by a