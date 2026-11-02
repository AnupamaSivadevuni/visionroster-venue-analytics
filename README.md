# Visionroster Venue Labour Analytics

I built this project to answer a question every hospitality manager asks: **are we rostering the right number of people for the customers who actually walk in?**

I work on data and analytics at Visionroster.ai, an early-stage startup that uses the CCTV a venue already has to count people (anonymously) and then uses those counts to help build rosters. This project is my analytics side of that idea. I took hourly people counts, sales and shift data for a two-store pizza business and built a Power BI report that shows where labour lines up with demand and where it doesn't.

> **The data is fictional.** I generated it with a seeded Python script so anyone can reproduce it. The occupancy file is shaped like an anonymised people-counter export: just a venue, a zone, an hour and a count. There are no images, faces or personal identities anywhere in this project.

[ADD screenshot: images/overview.png]

## Questions I wanted to answer
1. Does staff on shift follow foot traffic hour by hour?
2. What is labour cost as a % of sales, by day and by week, and is it trending the right way?
3. Which hours are under-staffed or over-staffed, and by how much?
4. When are the peak hours for each venue and zone (entrance, counter, dining)?
5. How do the two venues compare?

## Data
| File | What it is |
|---|---|
| `occupancy.csv` | Hourly people count per venue and zone (anonymised counter export) |
| `sales.csv` | Hourly transactions and revenue |
| `roster.csv` | Shifts: staff, role (front/kitchen), start, end, break |
| `staff.csv` | Staff role and a sample hourly rate (illustrative AU casual rates, not award advice) |
| `dim_date.csv`, `dim_hour.csv`, `dim_venue.csv` | Lookup tables |

8 weeks (31 Aug – 25 Oct 2026), two venues, trading 11:00–22:00. I left some real-world mess in on purpose: duplicate rows, a few missing counts (camera dropouts), missing break minutes and the same venue written five different ways. Cleaning that is part of the project.

## Tools
- **Python / pandas** for generating and checking the data (`scripts/`)
- **SQLite + SQL** (CTEs, window functions) for the analysis queries (`sql/`)
- **Power BI** with Power Query, a star schema and DAX for the report

## Data model
Star schema with four facts (occupancy, sales, rostered shifts, and shifts expanded to one row per hour) and four dimensions (date, hour, venue, staff).

[ADD screenshot: images/model.png]

## What I found
- Labour came out at about **25% of sales in Brunswick and 27.5% in Footscray** over the 8 weeks, and it improved week by week because sales grew while the roster stayed the same.
- The roster is a fixed template, so it doesn't follow demand. Brunswick was over-staffed in roughly **40% of trading hours**, mostly the 2–5pm lull, while Footscray is short at dinner: around **21 customers per staff member at 6–7pm** compared with about 5 at 2pm.
- Saturday 6–7pm is the peak at both venues.
- The takeaway is simple: move hours from the afternoon into the dinner rush instead of adding hours.

[ADD screenshot: images/heatmap.png]
[ADD screenshot: images/coverage.png]
[ADD screenshot: images/venues.png]

## How to run it
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_data.py   # rebuild the CSVs (seeded)
python scripts/eda.py             # cleaning + sanity checks
python scripts/load_sqlite.py     # load into data/venue.db
python scripts/run_sql.py         # run every query in sql/
```
The Power BI file is in `powerbi/`, along with a PDF export. The build steps I followed are in [POWERBI_STEPS.md](POWERBI_STEPS.md).

## SQL queries
- `00_clean_views.sql`: dedupe, standardise venue names, fill missing breaks, expand shifts to hours
- `01_staff_vs_occupancy.sql`: staff on shift vs foot traffic by hour
- `02_labour_pct_by_day.sql`: daily labour % with a 7-day rolling average
- `03_under_over_staffed.sql`: hours flagged under/over against 1 staff per 15 customers (minimum 2)
- `04_peak_hours.sql`: top 3 hours per venue and zone using RANK()
- `05_week_on_week.sql`: weekly revenue, labour % and week-on-week change using LAG()

## What I'd do next
Swap the fictional data for a real pilot venue's anonymised counts, add a forecast of next week's foot traffic, and turn the "required staff" rule into something learned from the data.
