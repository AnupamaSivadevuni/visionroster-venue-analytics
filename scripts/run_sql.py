"""Run every sql/0[1-9]*.sql against data/venue.db and print results."""
import sqlite3, pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
con = sqlite3.connect(ROOT / "data" / "venue.db")
pd.set_option("display.width", 160)
for f in sorted((ROOT / "sql").glob("0[1-9]_*.sql")):
    print(f"\n=== {f.name} ===")
    print(pd.read_sql(f.read_text(), con).to_string(index=False, max_rows=30))
