/*
Name: Filters: C Discharge Rate
Data source: 1
Created By: admin
Last Update At: 2022-03-05T20:49:33.825Z
Visualizations: [{'id': 31, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-02-27T21:57:14.201Z', 'created_at': '2022-02-27T21:57:14.201Z'}]
*/
select distinct crate_d as a, count(*) from cycle_metadata group by a order by a