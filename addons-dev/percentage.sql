select
status,
"sellingMethod",
COUNT(id) "count",
COUNT(id) / SUM(COUNT(id)) OVER () * 100 percent_count,
SUM(value_amount) amount,
SUM(value_amount) / SUM(SUM(value_amount)) OVER () * 100 percent_amount
FROM dgf_auction da
GROUP BY status,"sellingMethod"
ORDER BY "count" DESC;