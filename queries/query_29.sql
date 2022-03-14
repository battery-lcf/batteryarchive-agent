/*
Name: Filters: Max State of Charge
Data source: 1
Created By: admin
Last Update At: 2022-03-05T20:49:20.096Z
Visualizations: [{'id': 33, 'type': 'TABLE', 'name': 'Table', 'description': '', 'options': {}, 'updated_at': '2022-02-27T21:57:14.684Z', 'created_at': '2022-02-27T21:57:14.684Z'}]
*/
select distinct soc_max as a, count(*) from cycle_metadata group by a order by a