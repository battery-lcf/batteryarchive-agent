/*
Name: Filters: Thickness
Data source: 1
Created By: admin
Last Update At: 2022-03-12T16:41:43.903Z
Visualizations: [{'id': 44, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-03-12T16:41:14.352Z', 'created_at': '2022-03-12T16:41:14.352Z'}]
*/
select distinct thickness as a, count(*) from abuse_metadata group by a order by a