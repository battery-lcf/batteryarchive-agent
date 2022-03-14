/*
Name: Filters: C charge Rate
Data source: 1
Created By: admin
Last Update At: 2022-03-05T20:37:57.794Z
Visualizations: [{'id': 38, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-02-27T21:57:15.860Z', 'created_at': '2022-02-27T21:57:15.860Z'}]
*/
select distinct crate_c as a, count(*) from cycle_metadata group by a order by a