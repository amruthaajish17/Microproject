# ==============================================================================
# PRO-TIER SUPPLY CHAIN OPTIMIZATION & INTERACTIVE MAPPING
# ==============================================================================

import pandas as pd
import pulp
import folium

print("🚀 Initializing Optimization Engine...\n")

# ==========================================
# 1. DATA INGESTION & PROCESSING
# ==========================================

facilities_df = pd.read_csv('../data/facilities.csv')
demands_df = pd.read_csv('../data/demands.csv')
warehouses_df = pd.read_csv('../data/warehouses.csv')
transport_df = pd.read_csv('../data/transportation_costs.csv')

fac_full_df = pd.merge(facilities_df, demands_df, on='facility_id')

TARGET_FACILITIES = ['MED_CENTER', 'ENG_BUILDING', 'SCIENCE_HALL', 'DORM_A', 'DORM_B', 'LIBRARY']
TARGET_WAREHOUSES = ['WH_NORTH', 'WH_SOUTH', 'WH_EAST']
DAYS_IN_YEAR = 365
AMORT_YEARS = 10
BUDGET = 1500000

f_df = fac_full_df[fac_full_df['facility_id'].isin(TARGET_FACILITIES)].set_index('facility_id')
w_df = warehouses_df[warehouses_df['warehouse_id'].isin(TARGET_WAREHOUSES)].set_index('warehouse_id')

annual_demand = (f_df['daily_demand'] * DAYS_IN_YEAR).to_dict()
annual_capacity = (w_df['capacity'] * DAYS_IN_YEAR).to_dict()

annual_fixed_cost = {}
for w_id, row in w_df.iterrows():
    annual_fixed_cost[w_id] = (row['construction_cost'] / AMORT_YEARS) + (row['operational_cost'] * DAYS_IN_YEAR)

trans_costs = {}
for _, row in transport_df.iterrows():
    if row['from_warehouse'] in TARGET_WAREHOUSES and row['to_facility'] in TARGET_FACILITIES:
        trans_costs[(row['from_warehouse'], row['to_facility'])] = row['cost_per_unit']

# ==========================================
# 2. MILP OPTIMIZATION MODEL
# ==========================================

prob = pulp.LpProblem("Advanced_Campus_Logistics", pulp.LpMinimize)

y = pulp.LpVariable.dicts("Open_WH", TARGET_WAREHOUSES, cat='Binary')
x = pulp.LpVariable.dicts("Ship_Flow", (TARGET_WAREHOUSES, TARGET_FACILITIES), lowBound=0)

prob += (
    pulp.lpSum(annual_fixed_cost[j] * y[j] for j in TARGET_WAREHOUSES) +
    pulp.lpSum(trans_costs[(j, i)] * x[j][i] for j in TARGET_WAREHOUSES for i in TARGET_FACILITIES)
)

for i in TARGET_FACILITIES:
    prob += pulp.lpSum(x[j][i] for j in TARGET_WAREHOUSES) == annual_demand[i]

for j in TARGET_WAREHOUSES:
    prob += pulp.lpSum(x[j][i] for i in TARGET_FACILITIES) <= annual_capacity[j] * y[j]

prob += pulp.lpSum(y[j] for j in TARGET_WAREHOUSES) == 2

prob += (
    pulp.lpSum(annual_fixed_cost[j] * y[j] for j in TARGET_WAREHOUSES) +
    pulp.lpSum(trans_costs[(j, i)] * x[j][i] for j in TARGET_WAREHOUSES for i in TARGET_FACILITIES)
    <= BUDGET
)

prob.solve()

# ==========================================
# 3. BUSINESS ANALYTICS
# ==========================================

if pulp.LpStatus[prob.status] != 'Optimal':
    print("❌ No optimal solution found.")
else:
    total_cost = pulp.value(prob.objective)
    total_units = sum(annual_demand.values())
    cost_per_unit = total_cost / total_units

    print("✅ OPTIMIZATION SUCCESSFUL")
    print("-" * 50)
    print(f"💰 Total Annual Cost:     ${total_cost:,.2f}")
    print(f"📦 Total Units Delivered: {total_units:,.0f} units")
    print(f"📈 Avg. Cost Per Unit:    ${cost_per_unit:,.2f} / unit")
    print(f"🏦 Remaining Budget:      ${BUDGET - total_cost:,.2f}\n")

    print("🏢 Warehouse Utilization Report")
    print("-" * 50)
    for j in TARGET_WAREHOUSES:
        is_open = pulp.value(y[j]) > 0.5
        used_cap = sum(pulp.value(x[j][i]) for i in TARGET_FACILITIES) if is_open else 0
        utilization = (used_cap / annual_capacity[j]) * 100 if is_open else 0
        status = "OPEN" if is_open else "CLOSED"
        print(f"{j} | {status} | Utilization: {utilization:.1f}%")

    print("\n🚚 Optimal Routing")
    print("-" * 50)
    for j in TARGET_WAREHOUSES:
        for i in TARGET_FACILITIES:
            units = pulp.value(x[j][i])
            if units > 0:
                print(f"{j} ➔ {i} : {units:,.0f} units")

# ==========================================
# 4. INTERACTIVE MAP
# ==========================================

print("\n🗺️ Generating Interactive Map...")

center_lat = f_df['latitude'].mean()
center_lon = f_df['longitude'].mean()
m = folium.Map(location=[center_lat, center_lon], zoom_start=14)

for i, row in f_df.iterrows():
    folium.Marker(
        [row['latitude'], row['longitude']],
        tooltip=f"{row['facility_name']}"
    ).add_to(m)

max_flow = max(pulp.value(x[j][i]) for j in TARGET_WAREHOUSES for i in TARGET_FACILITIES)

for j, row in w_df.iterrows():
    is_open = pulp.value(y[j]) > 0.5
    lat, lon = row['latitude'], row['longitude']

    if is_open:
        folium.Marker([lat, lon], icon=folium.Icon(color="green")).add_to(m)

        for i in TARGET_FACILITIES:
            units = pulp.value(x[j][i])
            if units > 0:
                f_lat, f_lon = f_df.loc[i, 'latitude'], f_df.loc[i, 'longitude']
                weight = 2 + (units / max_flow) * 6
                folium.PolyLine(
                    [[lat, lon], [f_lat, f_lon]],
                    weight=weight
                ).add_to(m)
    else:
        folium.Marker([lat, lon], icon=folium.Icon(color="gray")).add_to(m)

m.save("optimization_map.html")
print("📍 Map saved as optimization_map.html")