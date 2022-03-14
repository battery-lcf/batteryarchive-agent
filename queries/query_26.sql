/*
Name: Filters: Cathode
Data source: 1
Created By: admin
Last Update At: 2022-03-05T20:49:45.089Z
Visualizations: [{'id': 30, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-02-27T21:57:13.957Z', 'created_at': '2022-02-27T21:57:13.957Z'}]
*/
select distinct cathode as a, count(*) from cell_metadata group by a order by a