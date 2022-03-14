/*
Name: Filters: Nominal Capacity (Ah)
Data source: 1
Created By: admin
Last Update At: 2022-03-06T00:06:28.204Z
Visualizations: [{'id': 23, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-02-27T21:57:12.249Z', 'created_at': '2022-02-27T21:57:12.249Z'}]
*/
select distinct ah as a, count(*) from cell_metadata group by a order by a