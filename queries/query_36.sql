/*
Name: Filters: Indentor
Data source: 1
Created By: admin
Last Update At: 2022-03-12T16:40:36.205Z
Visualizations: [{'id': 42, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-03-12T16:39:53.887Z', 'created_at': '2022-03-12T16:39:53.887Z'}]
*/
select distinct indentor as a, count(*) from abuse_metadata group by a order by a