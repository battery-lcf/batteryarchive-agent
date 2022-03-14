/*
Name: Filters: Anode
Data source: 1
Created By: admin
Last Update At: 2022-03-05T20:37:48.166Z
Visualizations: [{'id': 39, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-02-27T21:57:16.107Z', 'created_at': '2022-02-27T21:57:16.107Z'}]
*/
select distinct anode as a, count(*) from cell_metadata group by a order by a