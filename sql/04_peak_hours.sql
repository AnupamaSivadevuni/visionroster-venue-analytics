-- Top 3 busiest weekday-hour slots per venue and zone (RANK window).
WITH slot AS (
  SELECT venue_id, zone, strftime('%w', timestamp_hour) AS dow,
         CAST(strftime('%H', timestamp_hour) AS INT) AS hour, AVG(people_count) AS avg_count
  FROM occupancy GROUP BY venue_id, zone, dow, hour
), ranked AS (
  SELECT *, RANK() OVER (PARTITION BY venue_id, zone ORDER BY avg_count DESC) AS rnk FROM slot
)
SELECT venue_id, zone,
       CASE dow WHEN '0' THEN 'Sun' WHEN '1' THEN 'Mon' WHEN '2' THEN 'Tue' WHEN '3' THEN 'Wed'
                WHEN '4' THEN 'Thu' WHEN '5' THEN 'Fri' ELSE 'Sat' END AS weekday,
       hour, ROUND(avg_count, 1) AS avg_count, rnk
FROM ranked WHERE rnk <= 3 ORDER BY venue_id, zone, rnk;
