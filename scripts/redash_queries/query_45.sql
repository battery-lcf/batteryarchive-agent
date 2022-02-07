/*
Name: Filters: Number of Cycles
Data source: 1
Created By: admin
Last Update At: 2021-07-02T17:19:06.573Z
*/

select distinct cycle_index from cycle_stats where cycle_index%50 = 0 order by cycle_index