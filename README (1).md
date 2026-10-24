# Construction Project Cost & Delay Analysis

An end-to-end data analytics project using **Python, SQL and Power BI** to find out why construction projects go over budget and miss deadlines, and which projects are most at risk.

> **Note:** All data in this repository is **synthetic**, generated with `generate_construction_data.py` for learning and portfolio purposes. It is not real company data.

## Business Question

Why do construction projects exceed their budget and timeline, and which contractors, project types, cities and conditions carry the highest risk?

## Dataset

| File | Rows | Description |
|---|---|---|
| `projects.csv` | 304 | Project details: type, city, contractor, planned vs actual dates, delay days, planned budget and actual cost (in crore INR), status |
| `contractors.csv` | 25 | Contractor grade (A/B/C), experience, workforce size, safety incidents |
| `material_prices.csv` | 69 | Monthly cement, steel, sand and brick prices (Jan 2021 - Sep 2026) |
| `cost_breakdown.csv` | 1,310 | Planned vs actual cost by category (Material, Labour, Equipment, Overhead, Other) |
| `labour.csv` | 1,500 | Workers, daily wages and absenteeism by trade for each project |

### Data notes
- 265 projects are `Completed`; 39 are `In Progress` (their `actual_end_date`, `delay_days` and `actual_cost_cr` are blank). Cost and delay analysis should use completed projects only.
- `projects.csv` intentionally contains missing values (`permit_delay_days`), inconsistent city casing and 4 duplicate rows, for data-cleaning practice.
- Re-running the script reproduces the same data (random seed is fixed).

## Planned Analysis

1. **SQL:** cost overrun % and delay days per project, contractor scorecard, city and project-type performance, top delayed projects (joins, CTEs, window functions).
2. **Python (pandas, seaborn):** cleaning, EDA, and correlation of overrun with project size, steel price change, monsoon exposure, permit delays and contractor grade.
3. **Optional ML:** logistic regression or random forest to predict whether a project will be delayed.
4. **Power BI dashboard:** KPI cards (total budget, actual spend, average overrun %, on-time %), contractor scorecard, city and project-type breakdown, monthly cost trend, slicers.
5. **Recommendations:** for example penalty clauses for repeat-delay contractors, advance procurement of steel and cement, scheduling critical work before the monsoon.

## How to Regenerate the Data

```bash
pip install pandas numpy
python generate_construction_data.py
```

## Tools

Python (pandas, numpy, seaborn, matplotlib) · SQL · Power BI
