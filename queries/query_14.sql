/*
Name: Filters: Nail speed
Data source: 1
Created By: admin
Last Update At: 2022-05-31T21:05:50.782Z
Visualizations: [{'id': 14, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:02.438Z', 'created_at': '2022-05-31T19:26:02.438Z'}, {'id': 38, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:03.715Z', 'created_at': '2022-05-31T19:26:03.715Z'}]
*/

select distinct nail_speed as a, count(*) from abuse_metadata group by a order by a