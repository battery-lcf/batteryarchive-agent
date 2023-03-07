/*
Name: Filters: Form Factor
Data source: 1
Created By: admin
Last Update At: 2022-10-18T20:48:12.833Z
Visualizations: [{'id': 7, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:01.948Z', 'created_at': '2022-05-31T19:26:01.948Z'}, {'id': 67, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:04.913Z', 'created_at': '2022-05-31T19:26:04.913Z'}]
*/

select distinct form_factor as a, count(*) from cell_metadata group by a order by a