/*
Name: Filters: Cathode Abuse Test
Data source: 1
Created By: admin
Last Update At: 2022-10-18T21:09:50.918Z
Visualizations: [{'id': 78, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-10-18T21:09:27.917Z', 'created_at': '2022-10-18T21:09:27.917Z'}, {'id': 79, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-10-18T21:09:27.917Z', 'created_at': '2022-10-18T21:09:27.917Z'}]
*/

select distinct cathode as a, count(*) from cell_metadata where test = 'abuse' group by a order by a