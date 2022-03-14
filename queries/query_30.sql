/*
Name: Filters: Min State of Charge
Data source: 1
Created By: admin
Last Update At: 2022-03-05T20:49:04.207Z
Visualizations: [{'id': 34, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-02-27T21:57:14.922Z', 'created_at': '2022-02-27T21:57:14.922Z'}]
*/
select distinct soc_min as a, count(*) from cycle_metadata group by a order by a