-- Week-on-week revenue, labour % and change using LAG.
WITH wk AS (
  SELECT s.venue_id, d.week_no, SUM(s.revenue_aud) AS revenue
  FROM sales s JOIN dim_date d ON d.date = date(s.timestamp_hour) GROUP BY s.venue_id, d.week_no
), lab AS (
  SELECT r.venue_id, d.week_no,
         SUM(((julianday(r.shift_end) - julianday(r.shift_start)) * 24 - r.break_mins / 60.0) * st.hourly_rate_aud_sample) AS labour
  FROM roster r JOIN staff st USING (staff_id) JOIN dim_date d ON d.date = date(r.shift_start)
  GROUP BY r.venue_id, d.week_no
)
SELECT w.venue_id, w.week_no, ROUND(w.revenue) AS revenue, ROUND(l.labour) AS labour_cost,
       ROUND(100 * l.labour / w.revenue, 1) AS labour_pct,
       ROUND(100.0 * (w.revenue - LAG(w.revenue) OVER (PARTITION BY w.venue_id ORDER BY w.week_no))
             / LAG(w.revenue) OVER (PARTITION BY w.venue_id ORDER BY w.week_no), 1) AS revenue_wow_pct
FROM wk w JOIN lab l USING (venue_id, week_no) ORDER BY w.venue_id, w.week_no;
