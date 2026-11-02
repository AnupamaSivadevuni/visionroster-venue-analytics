"""Quick pandas cleaning + sanity checks on the raw CSVs."""
import pandas as pd
from pathlib import Path
D = Path(__file__).resolve().parent.parent / "data"
occ = pd.read_csv(D / "occupancy.csv"); sales = pd.read_csv(D / "sales.csv"); ros = pd.read_csv(D / "roster.csv")
staff = pd.read_csv(D / "staff.csv")
print("Raw rows:", len(occ), len(sales), len(ros))
print("Duplicate rows -> occupancy:", occ.duplicated().sum(), "sales:", sales.duplicated().sum())
print("Nulls ->", {"people_count": occ.people_count.isna().sum(), "revenue": sales.revenue_aud.isna().sum(), "break_mins": ros.break_mins.isna().sum()})
print("Venue name variants:", sorted(occ.venue.unique()))

occ = occ.drop_duplicates().dropna(subset=["people_count"])
occ["venue_id"] = occ.venue.str.lower().map(lambda s: "V01" if "brunswick" in s else "V02")
sales = sales.drop_duplicates().dropna(subset=["revenue_aud"])
for c in ["shift_start", "shift_end"]:
    ros[c] = pd.to_datetime(ros[c])
hrs = (ros.shift_end - ros.shift_start).dt.total_seconds() / 3600
ros["break_mins"] = ros.break_mins.fillna((hrs > 5) * 30)
ros["paid_hours"] = hrs - ros.break_mins / 60
ros = ros.merge(staff[["staff_id", "hourly_rate_aud_sample"]], on="staff_id")
ros["cost"] = ros.paid_hours * ros.hourly_rate_aud_sample

lab = ros.groupby("venue_id").cost.sum(); rev = sales.groupby("venue_id").revenue_aud.sum()
print("\nLabour % of sales (8 weeks):"); print((100 * lab / rev).round(1).to_string())
assert (ros.shift_end > ros.shift_start).all(), "shift ends before it starts"
assert occ.people_count.ge(0).all()
print("\nChecks passed.")
