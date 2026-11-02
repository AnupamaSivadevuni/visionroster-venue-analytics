-- Flag under/over-staffed hours. Target: 1 staff per 15 entrance entries, min 2.
WITH staff_hr AS (
  SELECT venue_id, timestamp_hour, SUM(frac_days) * 24 AS staff_on_shift
  FROM shift_hours GROUP BY venue_id, timestamp_hour
), demand AS (
  SELECT venue_id, timestamp_hour, SUM(people_count) AS entries,
         MAX(2, CAST(ROUND(SUM(people_count) / 15.0) AS INT)) AS required_staff
  FROM occupancy WHERE zone = 'entrance' GROUP BY venue_id, timestamp_hour
), flagged AS (
  SELECT d.*, COALESCE(s.staff_on_shift, 0) AS staff_on_shift,
         COALESCE(s.staff_on_shift, 0) - d.required_staff AS gap,
         CASE WHEN COALESCE(s.staff_on_shift, 0) - d.required_staff <= -1 THEN 'Under'
              WHEN COALESCE(s.staff_on_shift, 0) - d.required_staff >= 1 THEN 'Over'
              ELSE 'OK' END AS status
  FROM demand d LEFT JOIN staff_hr s USING (venue_id, timestamp_hour)
)
SELECT venue_id, status, COUNT(*) AS hours,
       ROUND(SUM(ABS(gap)), 1) AS staff_hours_gap,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY venue_id), 1) AS pct_of_hours
FROM flagged GROUP BY venue_id, status ORDER BY venue_id, status;
