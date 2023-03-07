/*
Name: Filters: Number of Cycles
Data source: 1
Created By: admin
Last Update At: 2022-05-31T21:07:24.575Z
Visualizations: [{'id': 24, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:03.034Z', 'created_at': '2022-05-31T19:26:03.034Z'}, {'id': 53, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:04.269Z', 'created_at': '2022-05-31T19:26:04.269Z'}]
*/

select distinct cycle_index from cycle_stats where cycle_index%10 = 0 order by cycle_index