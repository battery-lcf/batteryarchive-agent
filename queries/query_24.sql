/*
Name: Filters: Number of Cycles
Data source: 1
Created By: admin
Last Update At: 2022-03-12T19:39:17.108Z
Visualizations: [{'id': 28, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-02-27T21:57:13.465Z', 'created_at': '2022-02-27T21:57:13.465Z'}]
*/
select distinct cycle_index from cycle_stats where cycle_index%10 = 0 order by cycle_index