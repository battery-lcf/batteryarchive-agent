/*
Name: Disruptive Test DD
Data source: 1
Created By: admin
Last Update At: 2022-12-31T17:37:56.335Z
Visualizations: [{'id': 2, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:01.615Z', 'created_at': '2022-05-31T19:26:01.615Z'}, {'id': 62, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:04.654Z', 'created_at': '2022-05-31T19:26:04.654Z'}]
*/


select cell_id from cell_metadata where test = 'abuse' and status ='completed' order by cell_id