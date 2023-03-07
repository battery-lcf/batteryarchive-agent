/*
Name: Filters: SOC
Data source: 1
Created By: admin
Last Update At: 2022-09-07T21:55:45.953Z
Visualizations: [{'id': 15, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:02.498Z', 'created_at': '2022-05-31T19:26:02.498Z'}, {'id': 37, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:03.688Z', 'created_at': '2022-05-31T19:26:03.688Z'}]
*/

select distinct soc as a, count(*) from abuse_metadata group by a order by a