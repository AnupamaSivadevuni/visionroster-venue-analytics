"""Generate FICTIONAL sample data for Visionroster Venue Labour Analytics.
All venues, staff and numbers are made up. Occupancy mimics an anonymised
CCTV people-counter export: counts only, no faces, no identities. Seeded."""
import csv, random, datetime as dt
from pathlib import Path

random.seed(42)
OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)
START = dt.date(2026, 8, 31)  # Monday
DAYS = 56
OPEN, CLOSE = 11, 22  # trading hours 11:00-22:00
VENUES = {"V01": ("Slice & Co Pizza", "Brunswick", 1.0), "V02": ("Slice & Co Pizza", "Footscray", 0.8)}
NAME_VARIANTS = {"V01": ["Slice & Co - Brunswick", "slice & co brunswick", "Slice&Co Brunswick "],
                 "V02": ["Slice & Co - Footscray", "SLICE & CO FOOTSCRAY", "Slice & Co Footscray"]}
ZONES = {"entrance": 1.0, "counter": 0.55, "dining": 0.7}
DOW = [0.75, 0.8, 0.85, 0.95, 1.35, 1.45, 1.1]  # Mon..Sun
def hour_curve(h):
    return {11:.35,12:.95,13:.8,14:.35,15:.25,16:.3,17:.6,18:1.0,19:1.0,20:.7,21:.4}.get(h, 0)

def w(name, header, rows):
    with open(OUT / name, "w", newline="") as f:
        cw = csv.writer(f); cw.writerow(header); cw.writerows(rows)

# staff (sample AU casual-style hourly rates, illustrative only)
staff = []
for v, n_front, n_kitchen in [("V01", 9, 6), ("V02", 7, 5)]:
    for i in range(n_front):
        staff.append([f"{v}-F{i+1:02d}", v, "front", round(random.choice([29.85, 31.20, 32.65, 34.10]), 2), "Y" if i < 3 else "N"])
    for i in range(n_kitchen):
        staff.append([f"{v}-K{i+1:02d}", v, "kitchen", round(random.choice([31.20, 32.65, 34.10, 36.40]), 2), "Y" if i < 2 else "N"])
w("staff.csv", ["staff_id", "venue_id", "role", "hourly_rate_aud_sample", "trained_closer"], staff)
w("dim_venue.csv", ["venue_id", "brand", "suburb", "venue_name"], [[k, b, s, f"{b} - {s}"] for k, (b, s, _) in VENUES.items()])

occ, sales, roster, dates = [], [], [], []
shift_no = 0
for d in range(DAYS):
    day = START + dt.timedelta(days=d)
    dow = day.weekday()
    dates.append([day.isoformat(), day.year, day.month, day.strftime("%b"), (d // 7) + 1, dow + 1, day.strftime("%a"), "Y" if dow >= 4 else "N"])
    for v, (_, _, size) in VENUES.items():
        trend = 1 + 0.004 * d  # slow growth
        for h in range(OPEN, CLOSE):
            base = 60 * size * DOW[dow] * hour_curve(h) * trend
            ts = f"{day.isoformat()} {h:02d}:00:00"
            for z, zf in ZONES.items():
                c = max(0, int(random.gauss(base * zf, base * zf * 0.12 + 1)))
                vname = random.choice(NAME_VARIANTS[v]) if random.random() < 0.15 else NAME_VARIANTS[v][0]
                c_out = "" if random.random() < 0.006 else c  # camera dropouts
                occ.append([vname, z, ts, c_out])
            entries = max(0, base * random.uniform(0.9, 1.1))
            tx = int(entries * random.uniform(0.45, 0.52))
            rev = round(tx * random.uniform(21.5, 26.5), 2)
            sales.append([v, ts, tx, rev if random.random() > 0.004 else ""])
        # fixed template roster (not demand-driven -> gaps to find)
        pool_f = [s for s in staff if s[1] == v and s[2] == "front"]
        pool_k = [s for s in staff if s[1] == v and s[2] == "kitchen"]
        weekend = dow >= 4
        tmpl = [("front", 10.5, 15), ("front", 11, 15), ("front", 16.5, 22.5), ("kitchen", 10, 15), ("kitchen", 16, 22.5), ("front", 14.5, 18)]
        if weekend or dow == 3:
            tmpl += [("front", 17, 22), ("kitchen", 11.5, 14.5), ("front", 11.5, 14.5)]
        if v == "V01":
            tmpl += [("front", 14, 20)]  # mid shift through quiet afternoon
        if weekend and v == "V01":
            tmpl += [("kitchen", 17, 21.5)]
        used = set()
        for role, s, e in tmpl:
            pool = pool_f if role == "front" else pool_k
            p = random.choice([x for x in pool if x[0] not in used]); used.add(p[0])
            shift_no += 1
            st = dt.datetime.combine(day, dt.time()) + dt.timedelta(hours=s)
            en = dt.datetime.combine(day, dt.time()) + dt.timedelta(hours=e)
            brk = 30 if e - s > 5 else 0
            roster.append([f"S{shift_no:05d}", v, p[0], role, st.strftime("%Y-%m-%d %H:%M"), en.strftime("%Y-%m-%d %H:%M"), brk])

# messiness: duplicate rows, a null role, blank break
for _ in range(25):
    occ.append(random.choice(occ))
for _ in range(8):
    sales.append(random.choice(sales))
for i in random.sample(range(len(roster)), 6):
    roster[i][6] = ""
w("occupancy.csv", ["venue", "zone", "timestamp_hour", "people_count"], occ)
w("sales.csv", ["venue_id", "timestamp_hour", "transactions", "revenue_aud"], sales)
w("roster.csv", ["shift_id", "venue_id", "staff_id", "role", "shift_start", "shift_end", "break_mins"], roster)
w("dim_date.csv", ["date", "year", "month", "month_name", "week_no", "weekday_no", "weekday", "is_weekend"], dates)
w("dim_hour.csv", ["hour", "hour_label", "daypart"],
  [[h, f"{h:02d}:00", "Lunch" if 11 <= h < 15 else "Afternoon" if h < 17 else "Dinner" if h < 21 else "Late" if h >= 21 else "Closed"] for h in range(24)])
print(f"occupancy {len(occ)}, sales {len(sales)}, roster {len(roster)}, staff {len(staff)}")
