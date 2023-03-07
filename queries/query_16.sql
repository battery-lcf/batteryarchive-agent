/*
Name: Filters: Initial Voltage
Data source: 1
Created By: admin
Last Update At: 2022-05-31T21:06:00.412Z
Visualizations: [{'id': 16, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:02.568Z', 'created_at': '2022-05-31T19:26:02.568Z'}, {'id': 36, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:03.660Z', 'created_at': '2022-05-31T19:26:03.660Z'}]
*/

select distinct v_init as a, count(*) from abuse_metadata group by a order by a