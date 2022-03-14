/*
Name: Filters: Nail speed
Data source: 1
Created By: admin
Last Update At: 2022-03-12T16:41:08.651Z
Visualizations: [{'id': 43, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-03-12T16:40:42.465Z', 'created_at': '2022-03-12T16:40:42.465Z'}]
*/
select distinct nail_speed as a, count(*) from abuse_metadata group by a order by a