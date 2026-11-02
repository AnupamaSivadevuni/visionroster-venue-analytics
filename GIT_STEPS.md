# Pushing to GitHub

1. On github.com (signed in as AnupamaSivadevuni) click **New repository**.
   Name: `visionroster-venue-analytics`, Public, **leave it empty** (no README, no .gitignore).
2. Open the folder in VS Code (File > Open Folder), then Terminal > New Terminal and run one at a time:
```bash
git init
git add .
git status
```
   Check the list: there must be **no** `venue.db`, `.venv` or `.DS_Store`. (The `.gitignore` handles this.)
```bash
git commit -m "Venue labour analytics: data, SQL, Power BI report"
git branch -M main
git remote add origin https://github.com/AnupamaSivadevuni/visionroster-venue-analytics.git
git push -u origin main
```
3. Later changes (e.g. adding screenshots):
```bash
git add .
git commit -m "Add report screenshots"
git push
```
4. On the repo page, click the gear next to About and add a description and topics:
   `power-bi`, `dax`, `sql`, `pandas`, `hospitality`, `workforce-analytics`.

Suggested description: *Power BI + SQL analysis of whether hospitality staffing matches hourly foot traffic, using fictional anonymised people-counter data.*
