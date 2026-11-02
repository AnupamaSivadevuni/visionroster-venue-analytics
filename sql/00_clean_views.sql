-- Cleaning layer: dedupe, standardise venue names, handle nulls.
DROP VIEW IF EXISTS occupancy;
CREATE VIEW occupancy AS
SELECT DISTINCT
  CASE WHEN LOWER(venue) LIKE '%brunswick%' THEN 'V01'
       WHEN LOWER(venue) LIKE '%footscray%' THEN 'V02' END AS venue_id,
  zone, timestamp_hour, people_count
FROM raw_occupancy
WHERE people_count IS NOT NULL AND people_count <> '';

DROP VIEW IF EXISTS sales;
CREATE VIEW sales AS
SELECT DISTINCT venue_id, timestamp_hour, transactions, revenue_aud
FROM raw_sales WHERE revenue_aud IS NOT NULL AND revenue_aud <> '';

DROP VIEW IF EXISTS roster;
CREATE VIEW roster AS
SELECT shift_id, venue_id, staff_id, role, shift_start, shift_end,
       COALESCE(NULLIF(break_mins, ''),
         CASE WHEN (julianday(shift_end) - julianday(shift_start)) * 24 > 5 THEN 30 ELSE 0 END) AS break_mins
FROM raw_roster;

-- Shifts expanded to one row per trading hour (fractional overlap).
DROP VIEW IF EXISTS shift_hours;
CREATE VIEW shift_hours AS
WITH RECURSIVE hrs(h) AS (SELECT 0 UNION ALL SELECT h + 1 FROM hrs WHERE h < 23)
SELECT r.shift_id, r.venue_id, r.staff_id, r.role,
       date(r.shift_start) || ' ' || printf('%02d', h) || ':00:00' AS timestamp_hour,
       MIN(julianday(r.shift_end), julianday(date(r.shift_start)) + (h + 1) / 24.0)
     - MAX(julianday(r.shift_start), julianday(date(r.shift_start)) + h / 24.0) AS frac_days
FROM roster r JOIN hrs
  ON julianday(date(r.shift_start)) + (h + 1) / 24.0 > julianday(r.shift_start)
 AND julianday(date(r.shift_start)) + h / 24.0 < julianday(r.shift_end);
