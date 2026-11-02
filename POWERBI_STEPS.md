# Power BI build guide (do it yourself, step by step)

Save the file as `powerbi/Visionroster_Venue_Labour.pbix`. Tick each step as you go.

## 1. Import
Home > Get Data > Text/CSV. Import all CSVs in `data/`: occupancy, sales, roster, staff, dim_date, dim_hour, dim_venue. Click **Transform Data** (not Load).

## 2. Power Query cleaning
**occupancy**
1. Trim + Clean the `venue` column (Transform > Format > Trim, then Clean).
2. Add Conditional Column `venue_id`: if `venue` contains "brunswick" (ignore case) then V01, else if contains "footscray" then V02.
   Tip: Text.Contains(Text.Lower([venue]), "brunswick").
3. Remove the old `venue` column.
4. Change types: timestamp_hour = Date/Time, people_count = Whole Number.
5. Remove rows where people_count is null (camera dropouts). Note this in the README.
6. Remove Duplicates (select all columns first).
7. Add `date` = DateTime.Date([timestamp_hour]) and `hour` = Time.Hour([timestamp_hour]).

**sales**: types, remove null revenue, remove duplicates, add `date` and `hour` the same way.

**roster**
1. Types: shift_start / shift_end = Date/Time.
2. Add `shift_hours` = Duration.TotalHours([shift_end] - [shift_start]).
3. Replace null `break_mins`: Custom column `break_fixed` = if [break_mins] = null then (if [shift_hours] > 5 then 30 else 0) else [break_mins].
4. Add `paid_hours` = [shift_hours] - [break_fixed] / 60. Add `date` = DateTime.Date([shift_start]).

**shift_hourly** (fact table, one row per staff per hour on shift)
Reference `roster` (right click > Reference), rename `shift_hourly`, then add a custom column:
```
List.Numbers(Time.Hour(DateTime.Time([shift_start])),
  Number.RoundUp(Duration.TotalHours([shift_end] - DateTime.From([date]))) - Time.Hour(DateTime.Time([shift_start])))
```
Expand the list to new rows and rename it `hour`. Add `hour_fraction`:
```
let s = [date] & #time([hour],0,0), e = s + #duration(0,1,0,0),
    a = if [shift_start] > s then [shift_start] else s,
    b = if [shift_end] < e then [shift_end] else e
in Duration.TotalHours(b - a)
```
Keep shift_id, venue_id, staff_id, role, date, hour, hour_fraction.

**dim_date**: date = Date type. **dim_hour**: hour = Whole Number. Close & Apply.

## 3. Star schema (Model view)
Facts: `occupancy`, `sales`, `shift_hourly`, `roster`. Dims: `dim_date`, `dim_hour`, `dim_venue`, `staff`.

| From (many) | To (one) |
|---|---|
| occupancy[date], sales[date], shift_hourly[date], roster[date] | dim_date[date] |
| occupancy[hour], sales[hour], shift_hourly[hour] | dim_hour[hour] |
| occupancy[venue_id], sales[venue_id], shift_hourly[venue_id], roster[venue_id] | dim_venue[venue_id] |
| roster[staff_id], shift_hourly[staff_id] | staff[staff_id] |

All single direction, one-to-many. Mark `dim_date` as a date table (Table tools > Mark as date table). Hide the key columns on fact tables.
Sort `dim_date[weekday]` by `weekday_no`.

## 4. DAX measures (create a blank table `_Measures` to hold them)
```DAX
Revenue = SUM ( sales[revenue_aud] )

Labour Cost =
SUMX ( roster, roster[paid_hours] * RELATED ( staff[hourly_rate_aud_sample] ) )

Labour % = DIVIDE ( [Labour Cost], [Revenue] )

Foot Traffic = CALCULATE ( SUM ( occupancy[people_count] ), occupancy[zone] = "entrance" )

Staff Hours = SUM ( shift_hourly[hour_fraction] )

Staff on Shift (avg) =
AVERAGEX ( SUMMARIZE ( shift_hourly, dim_date[date], dim_hour[hour], dim_venue[venue_id] ), [Staff Hours] )

Customers per Staff = DIVIDE ( [Foot Traffic], [Staff Hours] )

Required Staff =
SUMX (
    SUMMARIZE ( occupancy, dim_date[date], dim_hour[hour], dim_venue[venue_id] ),
    MAX ( 2, ROUND ( DIVIDE ( [Foot Traffic], 15 ), 0 ) )
)

Under-staffed Hours =
COUNTROWS (
    FILTER (
        SUMMARIZE ( occupancy, dim_date[date], dim_hour[hour], dim_venue[venue_id] ),
        [Staff Hours] - MAX ( 2, ROUND ( DIVIDE ( [Foot Traffic], 15 ), 0 ) ) <= -1
    )
)

Over-staffed Hours =
COUNTROWS (
    FILTER (
        SUMMARIZE ( occupancy, dim_date[date], dim_hour[hour], dim_venue[venue_id] ),
        [Staff Hours] - MAX ( 2, ROUND ( DIVIDE ( [Foot Traffic], 15 ), 0 ) ) >= 1
    )
)

Revenue Prev Week = CALCULATE ( [Revenue], DATEADD ( dim_date[date], -7, DAY ) )

Revenue WoW % = DIVIDE ( [Revenue] - [Revenue Prev Week], [Revenue Prev Week] )

Labour % Prev Week =
DIVIDE ( CALCULATE ( [Labour Cost], DATEADD ( dim_date[date], -7, DAY ) ), [Revenue Prev Week] )

Revenue per Labour Hour = DIVIDE ( [Revenue], SUM ( roster[paid_hours] ) )
```
Format Labour %, Revenue WoW % as percentage (1 dp); Revenue and Labour Cost as currency.
Check: Labour % for the whole period should be about 25% (Brunswick) and 27.5% (Footscray). If it isn't, compare against `python scripts/eda.py`.
Note: WoW in Power BI works on a week grain; put `dim_date[week_no]` on the axis.

## 5. Report pages
1. **Executive overview**: cards (Revenue, Labour Cost, Labour %, Revenue per Labour Hour, Revenue WoW %), line chart of Labour % by week_no with a constant line at 30% target, slicer for venue.
2. **Staffing vs demand heatmap**: matrix with rows = dim_date[weekday], columns = dim_hour[hour_label], values = Customers per Staff. Conditional formatting > background colour (green low, red high). Second matrix: Staff Hours - Required Staff.
3. **Shift coverage**: clustered column chart of Staff Hours vs Required Staff by hour; stacked bar of Over/Under-staffed Hours by venue; table of shifts by role.
4. **Venue comparison**: Brunswick vs Footscray side by side: Labour %, Customers per Staff, Under-staffed Hours, peak zone (occupancy by zone column chart).

## 6. Polish
- **Tooltip page**: new page, Page information > Allow use as tooltip, size Tooltip. Add Revenue, Staff Hours, Customers per Staff. Set it as the tooltip on the heatmap.
- **Bookmarks**: View > Bookmarks. Make "Lunch" and "Dinner" bookmarks with daypart slicer set, add two buttons to switch.
- Consistent theme (View > Themes), page titles, a small "Data is fictional" text box in the footer.

## 7. Export
- File > Export > PDF, save to `powerbi/Visionroster_Venue_Labour.pdf`.
- Screenshot each page (Cmd+Shift+4 on Mac), save to `images/` as overview.png, heatmap.png, coverage.png, venues.png, then update the README image links.
