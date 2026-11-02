-- Labour cost % of sales by day (paid hours = shift length minus unpaid break).
WITH labour AS (
  SELECT r.venue_id, date(r.shift_start) AS day,
         SUM(((julianday(r.shift_end) - julianday(r.shift_start)) * 24 - r.break_mins / 60.0)
             * s.hourly_rate_aud_sample) AS labour_cost
  FROM roster r JOIN staff s USING (staff_id) GROUP BY r.venue_id, day
), rev AS (
  SELECT venue_id, date(timestamp_hour) AS day, SUM(revenue_aud) AS revenue
  FROM sales GROUP BY venue_id, day
)
SELECT l.venue_id, l.day, strftime('%w', l.day) AS dow,
       ROUND(r.revenue, 0) AS revenue, ROUND(l.labour_cost, 0) AS labour_cost,
       ROUND(100.0 * l.labour_cost / r.revenue, 1) AS labour_pct,
       ROUND(AVG(100.0 * l.labour_cost / r.revenue) OVER (
         PARTITION BY l.venue_id ORDER BY l.day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) AS labour_pct_7d_avg
FROM labour l JOIN rev r USING (venue_id, day) ORDER BY l.venue_id, l.day;
