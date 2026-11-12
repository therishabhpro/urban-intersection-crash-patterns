"""
Script: scripts/process_crashes.py
Project: Safety Engineering Project 2 - Crash Pattern Diagrams at Selected Urban Intersections
Objective:
    - Load the NYC Motor Vehicle Collisions datasets (Crashes and Vehicles).
    - Clean and standardize column names and attributes.
    - Filter to the selected high-activity urban intersection:
      Flatbush Avenue Extension & Tillary Street (Downtown Brooklyn, NY).
    - Link vehicle movements, impact points, travel directions, and contributing factors.
    - Classify collisions into standardized safety engineering crash patterns.
    - Standardize vehicle type classifications.
    - Generate summary statistics for collision types, severity, and vehicle types.
    - Save outputs to data/ and outputs/ directories.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# ---------------------------------------------------------
# 1. Configuration & Path Setup
# ---------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

CRASHES_RAW_CANDIDATES = [
    os.path.join(DATA_DIR, "crashes.csv"),
    os.path.join(DATA_DIR, "export.csv"),
    os.path.join(os.path.dirname(DATA_DIR), "export.csv")
]

VEHICLES_RAW_CANDIDATES = [
    os.path.join(DATA_DIR, "vehicles.csv"),
    os.path.join(DATA_DIR, "export (1).csv"),
    os.path.join(os.path.dirname(DATA_DIR), "export (1).csv")
]

crashes_path = next((p for p in CRASHES_RAW_CANDIDATES if os.path.exists(p)), None)
vehicles_path = next((p for p in VEHICLES_RAW_CANDIDATES if os.path.exists(p)), None)

if not crashes_path or not vehicles_path:
    print(f"Error: Raw dataset files not found. Checked: {CRASHES_RAW_CANDIDATES}")
    sys.exit(1)

print(f"[INFO] Using Crashes Dataset:  {crashes_path}")
print(f"[INFO] Using Vehicles Dataset: {vehicles_path}")

# Target Intersection: Flatbush Avenue Extension & Tillary Street, Brooklyn
TARGET_STREET_1 = "FLATBUSH AVENUE EXTENSION"
TARGET_STREET_2 = "TILLARY STREET"
TARGET_BOROUGH = "BROOKLYN"

# ---------------------------------------------------------
# 2. Load & Filter Crash Dataset
# ---------------------------------------------------------
print("\n[STEP 1] Filtering NYC Crash Records for Selected Intersection...")
filtered_crashes = []
chunk_size = 100000

# Standardized column mappings
col_crashes = {
    'COLLISION_ID': 'COLLISION_ID',
    'CRASH DATE': 'CRASH_DATE',
    'CRASH TIME': 'CRASH_TIME',
    'BOROUGH': 'BOROUGH',
    'ZIP CODE': 'ZIP_CODE',
    'LATITUDE': 'LATITUDE',
    'LONGITUDE': 'LONGITUDE',
    'ON STREET NAME': 'ON_STREET_NAME',
    'CROSS STREET NAME': 'CROSS_STREET_NAME',
    'OFF STREET NAME': 'OFF_STREET_NAME',
    'NUMBER OF PERSONS INJURED': 'PERSONS_INJURED',
    'NUMBER OF PERSONS KILLED': 'PERSONS_KILLED',
    'NUMBER OF PEDESTRIANS INJURED': 'PEDESTRIANS_INJURED',
    'NUMBER OF PEDESTRIANS KILLED': 'PEDESTRIANS_KILLED',
    'NUMBER OF CYCLIST INJURED': 'CYCLISTS_INJURED',
    'NUMBER OF CYCLIST KILLED': 'CYCLISTS_KILLED',
    'NUMBER OF MOTORIST INJURED': 'MOTORISTS_INJURED',
    'NUMBER OF MOTORIST KILLED': 'MOTORISTS_KILLED',
    'CONTRIBUTING FACTOR VEHICLE 1': 'CONTRIBUTING_FACTOR_VEH_1',
    'CONTRIBUTING FACTOR VEHICLE 2': 'CONTRIBUTING_FACTOR_VEH_2',
    'VEHICLE TYPE CODE 1': 'VEHICLE_TYPE_1',
    'VEHICLE TYPE CODE 2': 'VEHICLE_TYPE_2'
}

for chunk in pd.read_csv(crashes_path, chunksize=chunk_size, low_memory=False, dtype=str):
    on_st = chunk['ON STREET NAME'].fillna('').str.strip().str.upper()
    off_st = chunk['OFF STREET NAME'].fillna('').str.strip().str.upper()
    cross_st = chunk['CROSS STREET NAME'].fillna('').str.strip().str.upper()
    
    match_1 = (on_st == TARGET_STREET_1) & (off_st == TARGET_STREET_2)
    match_2 = (on_st == TARGET_STREET_2) & (off_st == TARGET_STREET_1)
    match_3 = (on_st == TARGET_STREET_1) & (cross_st == TARGET_STREET_2)
    match_4 = (on_st == TARGET_STREET_2) & (cross_st == TARGET_STREET_1)
    
    mask = match_1 | match_2 | match_3 | match_4
    matched_chunk = chunk[mask]
    if len(matched_chunk) > 0:
        filtered_crashes.append(matched_chunk)

df_crashes = pd.concat(filtered_crashes, ignore_index=True)
print(f"[INFO] Successfully filtered {len(df_crashes)} crash records for {TARGET_STREET_1} & {TARGET_STREET_2}.")

# Standardize columns
avail_cols = [c for c in col_crashes.keys() if c in df_crashes.columns]
df_crashes = df_crashes[avail_cols].rename(columns=col_crashes)

# Convert numeric fields
numeric_cols = [
    'PERSONS_INJURED', 'PERSONS_KILLED', 'PEDESTRIANS_INJURED', 'PEDESTRIANS_KILLED',
    'CYCLISTS_INJURED', 'CYCLISTS_KILLED', 'MOTORISTS_INJURED', 'MOTORISTS_KILLED'
]
for nc in numeric_cols:
    if nc in df_crashes.columns:
        df_crashes[nc] = pd.to_numeric(df_crashes[nc], errors='coerce').fillna(0).astype(int)

# Standardize dates and times
df_crashes['CRASH_DATE'] = pd.to_datetime(df_crashes['CRASH_DATE'], errors='coerce')
df_crashes['YEAR'] = df_crashes['CRASH_DATE'].dt.year
df_crashes['MONTH'] = df_crashes['CRASH_DATE'].dt.month
df_crashes['DAY_OF_WEEK'] = df_crashes['CRASH_DATE'].dt.day_name()
df_crashes['HOUR'] = pd.to_datetime(df_crashes['CRASH_TIME'], format='%H:%M', errors='coerce').dt.hour

collision_id_set = set(df_crashes['COLLISION_ID'].dropna().unique())

# ---------------------------------------------------------
# 3. Load & Filter Vehicle Dataset
# ---------------------------------------------------------
print("\n[STEP 2] Filtering NYC Vehicle Records for Matched Collision IDs...")
filtered_vehicles = []
for chunk in pd.read_csv(vehicles_path, chunksize=chunk_size, low_memory=False, dtype=str):
    matched = chunk[chunk['COLLISION_ID'].isin(collision_id_set)]
    if len(matched) > 0:
        filtered_vehicles.append(matched)

df_vehicles = pd.concat(filtered_vehicles, ignore_index=True)
print(f"[INFO] Successfully filtered {len(df_vehicles)} vehicle records across {len(collision_id_set)} collisions.")

# Standardize vehicle column names
df_vehicles.columns = [c.strip().upper() for c in df_vehicles.columns]

# Standardize vehicle types
def map_vehicle_type(vt):
    vt_str = str(vt).upper()
    if any(k in vt_str for k in ['SEDAN', '4 DR', '2 DR', 'CONVERTIBLE', 'COUPE']):
        return "Passenger Sedan"
    if any(k in vt_str for k in ['SPORT UTILITY', 'STATION WAGON', 'SUV']):
        return "SUV / Station Wagon"
    if any(k in vt_str for k in ['TAXI', 'LIVERY', 'FOR HIRE']):
        return "Taxi / For-Hire Vehicle"
    if any(k in vt_str for k in ['BOX TRUCK', 'VAN', 'PICK-UP', 'FLAT BED', 'TRACTOR', 'TRUCK', 'COM VEH']):
        return "Commercial Truck / Delivery Van"
    if any(k in vt_str for k in ['BUS']):
        return "Transit / School Bus"
    if any(k in vt_str for k in ['MOTORCYCLE', 'MOPED', 'SCOOTER', 'E-SCOOTER', 'BICYCLE', 'BIKE', 'E-BIKE']):
        return "Motorcycle / Micromobility"
    return "Other / Unspecified"

df_vehicles['STANDARDIZED_VEHICLE_TYPE'] = df_vehicles['VEHICLE_TYPE'].apply(map_vehicle_type)

# ---------------------------------------------------------
# 4. Standardized Collision Pattern Classification Logic
# ---------------------------------------------------------
print("\n[STEP 3] Performing Traffic Engineering Collision Pattern Classification...")

vehicles_by_id = {}
for cid, group in df_vehicles.groupby('COLLISION_ID'):
    vehicles_by_id[cid] = group.to_dict('records')

def classify_collision_record(row):
    cid = row['COLLISION_ID']
    vehs = vehicles_by_id.get(cid, [])
    
    # 1. Vulnerable Road Users (Pedestrians / Cyclists)
    if row.get('PEDESTRIANS_INJURED', 0) > 0 or row.get('PEDESTRIANS_KILLED', 0) > 0:
        return "Pedestrian Collision"
    if row.get('CYCLISTS_INJURED', 0) > 0 or row.get('CYCLISTS_KILLED', 0) > 0:
        return "Bicycle / Micromobility Collision"
    
    for v in vehs:
        vt = str(v.get('VEHICLE_TYPE', '')).upper()
        if any(b in vt for b in ['BICYCLE', 'BIKE', 'E-BIKE', 'SCOOTER']):
            return "Bicycle / Micromobility Collision"

    # 2. Single Vehicle Incidents
    if len(vehs) == 1:
        pc = str(vehs[0].get('PRE_CRASH', '')).upper()
        if 'BACKING' in pc:
            return "Backing Incident"
        if 'PARKED' in pc:
            return "Parked Vehicle Incident"
        return "Single Vehicle / Fixed Object"

    if len(vehs) == 0:
        return "Unrecorded / Undetermined"

    # Multi-vehicle variables
    pre_crashes = [str(v.get('PRE_CRASH', '')).strip().title() for v in vehs]
    impacts = [str(v.get('POINT_OF_IMPACT', '')).strip().title() for v in vehs]
    directions = [str(v.get('TRAVEL_DIRECTION', '')).strip().title() for v in vehs]
    factors = [str(v.get('CONTRIBUTING_FACTOR_1', '')).strip().title() for v in vehs] + \
              [str(v.get('CONTRIBUTING_FACTOR_2', '')).strip().title() for v in vehs]
    
    pc_set = set(pre_crashes)
    imp_set = set(impacts)
    f_set = set(factors)
    
    ns_dirs = {"North", "South", "Northbound", "Southbound"}
    ew_dirs = {"East", "West", "Eastbound", "Westbound"}
    has_ns = any(d in ns_dirs for d in directions)
    has_ew = any(d in ew_dirs for d in directions)
    is_perpendicular = has_ns and has_ew
    is_opposing_ns = ("North" in directions and "South" in directions)
    is_opposing_ew = ("East" in directions and "West" in directions)
    is_opposing = is_opposing_ns or is_opposing_ew
    
    rear_impacts = {"Center Back End", "Left Rear Bumper", "Right Rear Bumper", "Left Rear Quarter Panel", "Right Rear Quarter Panel"}
    front_impacts = {"Center Front End", "Left Front Bumper", "Right Front Bumper"}
    side_impacts = {"Right Side Doors", "Left Side Doors", "Right Front Quarter Panel", "Left Front Quarter Panel"}
    
    has_rear = bool(imp_set.intersection(rear_impacts))
    has_front = bool(imp_set.intersection(front_impacts))
    has_side = bool(imp_set.intersection(side_impacts))
    
    # (A) Rear-End Collision
    if "Following Too Closely" in f_set:
        return "Rear-End Collision"
    if has_rear and (has_front or "Stopped In Traffic" in pc_set or "Slowing Or Stopping" in pc_set or "Going Straight Ahead" in pc_set):
        if not is_perpendicular:
            return "Rear-End Collision"

    # (B) Turning Conflicts
    turning_left = bool(pc_set.intersection({"Making Left Turn", "Making Left Turn On Red"}))
    turning_right = bool(pc_set.intersection({"Making Right Turn", "Making Right Turn On Red"}))
    turning_u = "Making U Turn" in pc_set
    
    if turning_left:
        return "Left-Turn / Opposing-Flow Conflict"
    if turning_right:
        return "Right-Turn / Merging Conflict"
    if turning_u or "Turning Improperly" in f_set:
        return "Turning / Angle Conflict"

    # (C) Sideswipe (Same Direction)
    lane_actions = bool(pc_set.intersection({"Changing Lanes", "Passing", "Merging"}))
    lane_factors = bool(f_set.intersection({"Passing Or Lane Usage Improper", "Unsafe Lane Changing", "Passing Too Closely"}))
    if lane_actions or lane_factors or (has_side and not is_perpendicular and not is_opposing):
        return "Sideswipe (Same Direction)"

    # (D) Right-Angle (Broadside) Collision
    angle_factors = bool(f_set.intersection({"Failure To Yield Right-Of-Way", "Traffic Control Disregarded"}))
    if (is_perpendicular and (has_front or has_side)) or angle_factors:
        return "Right-Angle (Broadside) Collision"

    # (E) Head-On / Opposing Stream Collision
    if is_opposing and has_front:
        return "Head-On / Opposing Collision"

    # Secondary checks
    if has_rear:
        return "Rear-End Collision"
    if has_side:
        return "Sideswipe (Same Direction)"

    return "Other / Undetermined Collision"

# Apply classification
df_crashes['COLLISION_PATTERN'] = df_crashes.apply(classify_collision_record, axis=1)

def determine_primary_approach(row):
    cid = row['COLLISION_ID']
    vehs = vehicles_by_id.get(cid, [])
    dirs = [str(v.get('TRAVEL_DIRECTION', '')).strip().title() for v in vehs if v.get('TRAVEL_DIRECTION')]
    if dirs:
        return max(set(dirs), key=dirs.count)
    return "Unspecified"

df_crashes['DOMINANT_DIRECTION'] = df_crashes.apply(determine_primary_approach, axis=1)

# Save processed datasets to data/
processed_crashes_file = os.path.join(DATA_DIR, "intersection_crashes.csv")
processed_vehicles_file = os.path.join(DATA_DIR, "intersection_vehicles.csv")

df_crashes.to_csv(processed_crashes_file, index=False)
df_vehicles.to_csv(processed_vehicles_file, index=False)
print(f"[INFO] Saved processed crash subset:   {processed_crashes_file}")
print(f"[INFO] Saved processed vehicle subset: {processed_vehicles_file}")

# ---------------------------------------------------------
# 5. Generate Summary Statistics Table (`outputs/summary_stats.csv`)
# ---------------------------------------------------------
print("\n[STEP 4] Compiling Detailed Engineering Summary Statistics...")

pattern_counts = df_crashes['COLLISION_PATTERN'].value_counts()
pattern_pcts = df_crashes['COLLISION_PATTERN'].value_counts(normalize=True) * 100

summary_pattern_list = []
for p, count in pattern_counts.items():
    pct = pattern_pcts[p]
    subset = df_crashes[df_crashes['COLLISION_PATTERN'] == p]
    inj = subset['PERSONS_INJURED'].sum()
    kill = subset['PERSONS_KILLED'].sum()
    ped_inj = subset['PEDESTRIANS_INJURED'].sum()
    cyc_inj = subset['CYCLISTS_INJURED'].sum()
    mot_inj = subset['MOTORISTS_INJURED'].sum()
    
    summary_pattern_list.append({
        'Category': 'Collision Pattern',
        'Attribute': p,
        'Count': int(count),
        'Percentage': round(pct, 2),
        'Total_Injuries': int(inj),
        'Total_Fatalities': int(kill),
        'Pedestrian_Injuries': int(ped_inj),
        'Cyclist_Injuries': int(cyc_inj),
        'Motorist_Injuries': int(mot_inj)
    })

total_crashes = len(df_crashes)
total_injuries = df_crashes['PERSONS_INJURED'].sum()
total_fatalities = df_crashes['PERSONS_KILLED'].sum()
injury_crashes = (df_crashes['PERSONS_INJURED'] > 0).sum()
fatal_crashes = (df_crashes['PERSONS_KILLED'] > 0).sum()
penn_only_crashes = total_crashes - injury_crashes - fatal_crashes

severity_items = [
    ('Total Recorded Crashes', total_crashes, 100.0),
    ('Property Damage Only (PDO) Crashes', penn_only_crashes, round(penn_only_crashes / total_crashes * 100, 2)),
    ('Injury-Incurring Crashes', injury_crashes, round(injury_crashes / total_crashes * 100, 2)),
    ('Fatal Crashes', fatal_crashes, round(fatal_crashes / total_crashes * 100, 2)),
    ('Total Persons Injured', total_injuries, np.nan),
    ('Total Persons Killed', total_fatalities, np.nan),
    ('Pedestrians Injured', df_crashes['PEDESTRIANS_INJURED'].sum(), np.nan),
    ('Cyclists Injured', df_crashes['CYCLISTS_INJURED'].sum(), np.nan),
    ('Motorists Injured', df_crashes['MOTORISTS_INJURED'].sum(), np.nan)
]

for attr, cnt, pct in severity_items:
    summary_pattern_list.append({
        'Category': 'Severity Overview',
        'Attribute': attr,
        'Count': int(cnt),
        'Percentage': pct if not np.isnan(pct) else '',
        'Total_Injuries': '',
        'Total_Fatalities': '',
        'Pedestrian_Injuries': '',
        'Cyclist_Injuries': '',
        'Motorist_Injuries': ''
    })

veh_counts = df_vehicles['STANDARDIZED_VEHICLE_TYPE'].value_counts()
veh_pcts = df_vehicles['STANDARDIZED_VEHICLE_TYPE'].value_counts(normalize=True) * 100

for vt, count in veh_counts.items():
    summary_pattern_list.append({
        'Category': 'Vehicle Classification',
        'Attribute': vt,
        'Count': int(count),
        'Percentage': round(veh_pcts[vt], 2),
        'Total_Injuries': '',
        'Total_Fatalities': '',
        'Pedestrian_Injuries': '',
        'Cyclist_Injuries': '',
        'Motorist_Injuries': ''
    })

factors_series = pd.concat([
    df_vehicles['CONTRIBUTING_FACTOR_1'].fillna(''),
    df_vehicles['CONTRIBUTING_FACTOR_2'].fillna('')
])
factors_series = factors_series[factors_series != '']
factor_counts = factors_series.value_counts().head(10)
factor_pcts = (factor_counts / len(factors_series)) * 100

for f_name, count in factor_counts.items():
    summary_pattern_list.append({
        'Category': 'Top Contributing Factors',
        'Attribute': f_name,
        'Count': int(count),
        'Percentage': round(factor_pcts[f_name], 2),
        'Total_Injuries': '',
        'Total_Fatalities': '',
        'Pedestrian_Injuries': '',
        'Cyclist_Injuries': '',
        'Motorist_Injuries': ''
    })

df_summary = pd.DataFrame(summary_pattern_list)
summary_file = os.path.join(OUTPUTS_DIR, "summary_stats.csv")
df_summary.to_csv(summary_file, index=False)
print(f"[INFO] Summary statistics successfully saved to: {summary_file}")

# ---------------------------------------------------------
# 6. Display Quick Terminal Table
# ---------------------------------------------------------
print("\n" + "="*80)
print(f"CRASH PATTERN ANALYSIS SUMMARY: {TARGET_STREET_1} & {TARGET_STREET_2}")
print("="*80)
print(f"Total Collisions Analyzed: {total_crashes} | Total Vehicles Matched: {len(df_vehicles)}")
print(f"Total Persons Injured:    {total_injuries} | Total Persons Killed:   {total_fatalities}")
print(f"Date Coverage:            {df_crashes['CRASH_DATE'].min().strftime('%Y-%m-%d')} to {df_crashes['CRASH_DATE'].max().strftime('%Y-%m-%d')}")
print("-"*80)
print(f"{'Collision Pattern':<35} | {'Count':<6} | {'% of Total':<10} | {'Injuries':<8} | {'Fatalities':<10}")
print("-"*80)
for p, count in pattern_counts.items():
    pct = pattern_pcts[p]
    subset = df_crashes[df_crashes['COLLISION_PATTERN'] == p]
    inj = subset['PERSONS_INJURED'].sum()
    kill = subset['PERSONS_KILLED'].sum()
    print(f"{p:<35} | {count:<6} | {pct:>9.1f}% | {inj:<8} | {kill:<10}")
print("="*80)
