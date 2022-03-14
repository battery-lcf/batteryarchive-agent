/*
Name: Filters: Source
Data source: 1
Created By: admin
Last Update At: 2022-03-05T20:38:54.285Z
Visualizations: [{'id': 21, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-02-27T21:57:11.753Z', 'created_at': '2022-02-27T21:57:11.753Z'}]
*/
select distinct source as a, count(*) from cell_metadata group by a order by a 