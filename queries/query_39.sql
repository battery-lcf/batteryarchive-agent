/*
Name: Filters: Initial Voltage
Data source: 1
Created By: admin
Last Update At: 2022-03-12T16:42:13.900Z
Visualizations: [{'id': 45, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-03-12T16:41:47.596Z', 'created_at': '2022-03-12T16:41:47.596Z'}]
*/
select distinct v_init as a, count(*) from abuse_metadata group by a order by a