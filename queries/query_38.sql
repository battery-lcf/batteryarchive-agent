/*
Name: Validate Cycle Test DD
Data source: 1
Created By: admin
Last Update At: 2022-12-30T18:49:20.856Z
Visualizations: [{'id': 90, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-12-30T18:48:53.249Z', 'created_at': '2022-12-30T18:48:53.249Z'}, {'id': 91, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-12-30T18:48:53.249Z', 'created_at': '2022-12-30T18:48:53.249Z'}]
*/


select cell_id from cell_metadata where status = 'validate' and test = 'cycle' order by cell_id