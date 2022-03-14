/*
Name: Filters: Form Factor
Data source: 1
Created By: admin
Last Update At: 2022-03-06T00:36:16.498Z
Visualizations: [{'id': 14, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-02-27T21:57:10.025Z', 'created_at': '2022-02-27T21:57:10.025Z'}]
*/
select distinct form_factor as a, count(*) from cell_metadata group by a order by a