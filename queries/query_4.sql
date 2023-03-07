/*
Name: Filters: Anode
Data source: 1
Created By: admin
Last Update At: 2022-05-31T21:02:25.118Z
Visualizations: [{'id': 4, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:01.744Z', 'created_at': '2022-05-31T19:26:01.744Z'}, {'id': 40, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:03.777Z', 'created_at': '2022-05-31T19:26:03.777Z'}]
*/

select distinct anode as a, count(*) from cell_metadata group by a order by a