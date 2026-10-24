"""
Synthetic Construction Project dataset generator.
Creates 5 linked CSV tables for SQL + Python + Power BI practice.
NOTE: All data is synthetic. Mention this in your portfolio.
Run:  python generate_construction_data.py
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N_PROJECTS = 300
N_CONTRACTORS = 25

# ---------------------------------------------------------------- contractors
contractor_names = [
    "Apex Infra", "BuildRight Constructions", "Shree Ganesh Builders", "Metro Civil Works",
    "Sunrise Developers", "Titan Projects", "Bharat Engineering", "Kaveri Constructions",
    "Himalaya Infra", "Orion Builders", "Vishwakarma & Sons", "Prime Structures",
    "Deccan Civil", "Ganga Infratech", "Lotus Builders", "Rajdhani Constructions",
    "Skyline Engineers", "Narmada Projects", "Mahalaxmi Builders", "Zenith Infra",
    "Surya Constructions", "Konkan Developers", "Trident Civil", "Aravali Builders",
    "Pioneer Infra",
]
contractors = pd.DataFrame({
    "contractor_id": [f"C{str(i+1).zfill(3)}" for i in range(N_CONTRACTORS)],
    "contractor_name": contractor_names,
    "years_experience": rng.integers(3, 35, N_CONTRACTORS),
    "grade": rng.choice(["A", "B", "C"], N_CONTRACTORS, p=[0.3, 0.45, 0.25]),
    "workforce_size": rng.integers(40, 900, N_CONTRACTORS),
})
# hidden reliability: drives delays/overruns (do NOT include in final data)
grade_base = contractors["grade"].map({"A": 0.8, "B": 0.55, "C": 0.3}).values
reliability = np.clip(grade_base + rng.normal(0, 0.12, N_CONTRACTORS), 0.05, 0.95)
contractors["safety_incidents_last_3y"] = np.clip(
    np.round((1 - reliability) * 10 + rng.normal(0, 1.5, N_CONTRACTORS)), 0, None
).astype(int)

# ------------------------------------------------------------ material prices
months = pd.period_range("2021-01", "2026-09", freq="M")
cement = 360 + np.cumsum(rng.normal(1.2, 4, len(months)))       # INR per 50kg bag
steel = 55000 + np.cumsum(rng.normal(180, 900, len(months)))    # INR per tonne
sand = 1400 + np.cumsum(rng.normal(8, 30, len(months)))         # INR per tonne
bricks = 7.5 + np.cumsum(rng.normal(0.02, 0.08, len(months)))   # INR per brick
material_prices = pd.DataFrame({
    "month": months.astype(str),
    "cement_per_bag": cement.round(1),
    "steel_per_tonne": steel.round(0),
    "sand_per_tonne": sand.round(0),
    "bricks_per_unit": bricks.round(2),
})
mp = material_prices.set_index("month")

# ------------------------------------------------------------------- projects
cities = ["Mumbai", "Pune", "Delhi", "Bengaluru", "Hyderabad", "Chennai",
          "Ahmedabad", "Kolkata", "Nagpur", "Jaipur"]
city_cost_factor = dict(zip(cities, [1.35, 1.1, 1.25, 1.2, 1.1, 1.1, 1.0, 1.05, 0.9, 0.9]))
types = ["Residential", "Commercial", "Road", "Bridge", "Industrial", "Water Pipeline"]
type_params = {  # (base budget crore, base duration months, delay risk)
    "Residential": (25, 20, 0.05), "Commercial": (45, 24, 0.07), "Road": (30, 14, 0.06),
    "Bridge": (60, 28, 0.12), "Industrial": (40, 18, 0.08), "Water Pipeline": (20, 12, 0.04),
}

rows = []
for i in range(N_PROJECTS):
    ptype = rng.choice(types, p=[0.3, 0.2, 0.18, 0.08, 0.14, 0.10])
    city = rng.choice(cities)
    cidx = rng.integers(0, N_CONTRACTORS)
    base_budget, base_dur, type_risk = type_params[ptype]
    budget = base_budget * city_cost_factor[city] * rng.lognormal(0, 0.45)       # crore INR
    size_sqft = int(rng.lognormal(11.2, 0.6)) if ptype in ("Residential", "Commercial", "Industrial") else np.nan
    planned_months = int(np.clip(base_dur * (budget / base_budget) ** 0.35 * rng.normal(1, 0.12), 6, 48))
    start = pd.Timestamp("2021-01-01") + pd.Timedelta(days=int(rng.integers(0, 365 * 4 + 120)))
    planned_end = start + pd.DateOffset(months=planned_months)
    planned_days = (planned_end - start).days

    # monsoon months overlap (Jun-Sep)
    span = pd.date_range(start, planned_end, freq="MS")
    monsoon_share = np.mean([d.month in (6, 7, 8, 9) for d in span]) if len(span) else 0
    monsoon_exposure = 1 if ptype in ("Road", "Bridge", "Water Pipeline") else 0.6

    permit_delay = int(max(0, rng.normal(25, 20)))
    # steel price change during project
    s0 = mp.loc[start.strftime("%Y-%m"), "steel_per_tonne"] if start.strftime("%Y-%m") in mp.index else steel[-1]
    sm = min(planned_end.strftime("%Y-%m"), "2026-09")
    s1 = mp.loc[sm, "steel_per_tonne"]
    steel_change = (s1 - s0) / s0

    delay_factor = (
        0.30 * (1 - reliability[cidx])
        + type_risk
        + 0.18 * monsoon_share * monsoon_exposure
        + permit_delay / 900
        + rng.normal(0, 0.05)
    )
    delay_days = int(max(0, delay_factor * planned_days * rng.uniform(0.6, 1.4) - 20))
    actual_end = planned_end + pd.Timedelta(days=delay_days)
    status = "Completed" if actual_end < pd.Timestamp("2026-09-30") else "In Progress"

    overrun_pct = (
        0.04 + 0.35 * (1 - reliability[cidx]) * 0.5
        + 0.10 * max(steel_change, 0)
        + 0.12 * (delay_days / planned_days)
        + rng.normal(0, 0.03)
    )
    overrun_pct = float(np.clip(overrun_pct, -0.05, 0.6))
    actual_cost = budget * (1 + overrun_pct)

    rows.append({
        "project_id": f"P{str(i+1).zfill(4)}",
        "project_name": f"{city} {ptype} Project {i+1}",
        "project_type": ptype,
        "city": city,
        "contractor_id": contractors.loc[cidx, "contractor_id"],
        "start_date": start.date(),
        "planned_end_date": planned_end.date(),
        "actual_end_date": actual_end.date() if status == "Completed" else None,
        "planned_duration_days": planned_days,
        "delay_days": delay_days if status == "Completed" else None,
        "permit_delay_days": permit_delay,
        "size_sqft": size_sqft,
        "planned_budget_cr": round(budget, 2),
        "actual_cost_cr": round(actual_cost, 2) if status == "Completed" else None,
        "status": status,
    })

projects = pd.DataFrame(rows)

# ---------------------------------------------------------- cost breakdown
cost_rows = []
for _, p in projects[projects.status == "Completed"].iterrows():
    shares = rng.dirichlet([30, 28, 20, 10, 12])  # material, labour, equipment, overhead, other
    for cat, sh in zip(["Material", "Labour", "Equipment", "Overhead", "Other"], shares):
        cost_rows.append({
            "project_id": p.project_id, "cost_category": cat,
            "planned_cost_cr": round(p.planned_budget_cr * sh, 2),
            "actual_cost_cr": round(p.actual_cost_cr * sh * rng.normal(1, 0.04), 2),
        })
cost_breakdown = pd.DataFrame(cost_rows)

# ----------------------------------------------------------------- labour
labour_rows = []
for _, p in projects.iterrows():
    for trade in ["Mason", "Carpenter", "Electrician", "Helper", "Supervisor"]:
        labour_rows.append({
            "project_id": p.project_id, "trade": trade,
            "avg_workers": int(max(2, rng.normal(20 if trade == "Helper" else 8, 4))),
            "daily_wage_inr": int(rng.normal({"Mason": 800, "Carpenter": 750, "Electrician": 900,
                                              "Helper": 500, "Supervisor": 1200}[trade], 60)),
            "absenteeism_pct": round(float(np.clip(rng.normal(8, 3), 1, 25)), 1),
        })
labour = pd.DataFrame(labour_rows)

# ------------------------------------- light data-quality issues (for cleaning practice)
projects.loc[rng.choice(projects.index, 8, replace=False), "permit_delay_days"] = np.nan
projects.loc[rng.choice(projects.index, 5, replace=False), "city"] = (
    projects.loc[rng.choice(projects.index, 5, replace=False), "city"].str.lower().values
)
projects = pd.concat([projects, projects.sample(4, random_state=1)], ignore_index=True)  # 4 duplicates

# ----------------------------------------------------------------- save
contractors.to_csv("contractors.csv", index=False)
projects.to_csv("projects.csv", index=False)
material_prices.to_csv("material_prices.csv", index=False)
cost_breakdown.to_csv("cost_breakdown.csv", index=False)
labour.to_csv("labour.csv", index=False)

print("projects:", projects.shape, "| contractors:", contractors.shape)
print("material_prices:", material_prices.shape, "| cost_breakdown:", cost_breakdown.shape,
      "| labour:", labour.shape)
done = projects[projects.status == "Completed"]
print("Completed projects:", len(done))
print("Avg cost overrun %:", round(((done.actual_cost_cr / done.planned_budget_cr - 1) * 100).mean(), 1))
print("Avg delay days:", round(done.delay_days.mean(), 1))
