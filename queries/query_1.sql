/*
Name: Cycle Test DD
Data source: 1
Created By: admin
Last Update At: 2022-12-30T18:30:55.150Z
Visualizations: [{'id': 1, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:01.513Z', 'created_at': '2022-05-31T19:26:01.513Z'}, {'id': 52, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:04.239Z', 'created_at': '2022-05-31T19:26:04.239Z'}]
*/


select cell_id from cell_metadata where status = 'completed' and test = 'cycle' order by cell_id