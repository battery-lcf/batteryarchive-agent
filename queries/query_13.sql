/*
Name: Filters: Indentor
Data source: 1
Created By: admin
Last Update At: 2022-05-31T21:05:42.683Z
Visualizations: [{'id': 13, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:02.375Z', 'created_at': '2022-05-31T19:26:02.375Z'}, {'id': 39, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-05-31T19:26:03.747Z', 'created_at': '2022-05-31T19:26:03.747Z'}]
*/

select distinct indentor as a, count(*) from abuse_metadata group by a order by a