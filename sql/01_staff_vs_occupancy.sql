-- Hourly staff on shift vs entrance foot traffic, with customers per staff.
WITH staff_hr AS (
  SELECT venue_id, timestamp_hour, ROUND(SUM(frac_days) * 24, 2) AS staff_on_shift
  FROM shift_hours GROUP BY venue_id, timestamp_hour
), traffic AS (
  SELECT venue_id, timestamp_hour, SUM(people_count) AS entries
  FROM occupancy WHERE zone = 'entrance' GROUP BY venue_id, timestamp_hour
)
SELECT t.venue_id, CAST(strftime('%H', t.timestamp_hour) AS INT) AS hour,
       ROUND(AVG(t.entries), 1) AS avg_entries,
       ROUND(AVG(COALESCE(s.staff_on_shift, 0)), 2) AS avg_staff,
       ROUND(AVG(t.entries) / NULLIF(AVG(s.staff_on_shift), 0), 1) AS entries_per_staff
FROM traffic t LEFT JOIN staff_hr s USING (venue_id, timestamp_hour)
GROUP BY t.venue_id, hour ORDER BY t.venue_id, hour;
