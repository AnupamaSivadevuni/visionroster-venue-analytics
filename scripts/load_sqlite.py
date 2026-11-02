"""Load the CSVs into data/venue.db (SQLite), with light cleaning views."""
import sqlite3, pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
con = sqlite3.connect(ROOT / "data" / "venue.db")
for t in ["occupancy", "sales", "roster", "staff", "dim_date", "dim_hour", "dim_venue"]:
    pd.read_csv(ROOT / "data" / f"{t}.csv").to_sql(f"raw_{t}" if t in ("occupancy", "sales", "roster") else t, con, if_exists="replace", index=False)
con.executescript(open(ROOT / "sql" / "00_clean_views.sql").read())
print("Loaded", ROOT / "data" / "venue.db")
