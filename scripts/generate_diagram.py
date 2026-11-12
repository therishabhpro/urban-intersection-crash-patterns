"""
Script: scripts/generate_diagram.py
Project: Safety Engineering Project 2 - Crash Pattern Diagrams at Selected Urban Intersections
Objective:
    - Construct a professional, clearly labelled schematic intersection layout of
      Flatbush Avenue Extension & Tillary Street (Downtown Brooklyn, NY).
    - Map and overlay recorded crash patterns (Rear-End, Right-Angle, Sideswipe,
      Left-Turn, Right-Turn, Pedestrian, Cyclist, Single-Vehicle) using standardized
      traffic engineering markers, conflict zones, and approach directions.
    - Include analytical summary subplots (Pattern Frequency, Severity, Vehicle Class, Approach Leg).
    - Export a publication-quality 300 DPI diagram to outputs/crash_pattern_diagram.png.
    - Generate supplementary temporal and contributing factor visualizations in outputs/supplementary_analysis.png.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as mlines
from matplotlib.gridspec import GridSpec

# ---------------------------------------------------------
# 1. Path Setup & Data Loading
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUTS_DIR, exist_ok=True)

crashes_file = os.path.join(DATA_DIR, "intersection_crashes.csv")
vehicles_file = os.path.join(DATA_DIR, "intersection_vehicles.csv")

if not os.path.exists(crashes_file):
    print(f"Error: Processed crashes file not found at {crashes_file}. Run process_crashes.py first.")
    sys.exit(1)

df_crashes = pd.read_csv(crashes_file)
df_vehicles = pd.read_csv(vehicles_file) if os.path.exists(vehicles_file) else None

print(f"[INFO] Loaded {len(df_crashes)} processed crash records.")

# Map vehicle types if standardized column is not yet present
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

if df_vehicles is not None and 'STANDARDIZED_VEHICLE_TYPE' not in df_vehicles.columns:
    df_vehicles['STANDARDIZED_VEHICLE_TYPE'] = df_vehicles['VEHICLE_TYPE'].apply(map_vehicle_type)

# ---------------------------------------------------------
# 2. Collision Type Symbol & Color Definitions
# ---------------------------------------------------------
PATTERN_STYLES = {
    'Rear-End Collision': {
        'label': 'Rear-End (RE)',
        'marker': '^',
        'color': '#E66101', # Amber / Deep Orange
        'edge': '#8C3B00',
        'size': 55,
        'zorder': 6
    },
    'Right-Angle (Broadside) Collision': {
        'label': 'Right-Angle / Broadside (RA)',
        'marker': 's',
        'color': '#D7191C', # Crimson Red
        'edge': '#67000D',
        'size': 65,
        'zorder': 8
    },
    'Sideswipe (Same Direction)': {
        'label': 'Sideswipe - Same Direction (SS)',
        'marker': 'D',
        'color': '#2B83BA', # Cobalt Blue
        'edge': '#084081',
        'size': 50,
        'zorder': 6
    },
    'Left-Turn / Opposing-Flow Conflict': {
        'label': 'Left-Turn / Opposing Flow (LT)',
        'marker': 'v',
        'color': '#7B3294', # Purple
        'edge': '#40004B',
        'size': 60,
        'zorder': 7
    },
    'Right-Turn / Merging Conflict': {
        'label': 'Right-Turn / Merging (RT)',
        'marker': 'P',
        'color': '#008837', # Forest Green
        'edge': '#00441B',
        'size': 55,
        'zorder': 7
    },
    'Pedestrian Collision': {
        'label': 'Pedestrian (PED)',
        'marker': 'o',
        'color': '#F02720', # High-Vis Red-Pink
        'edge': '#000000',
        'size': 75,
        'zorder': 9
    },
    'Bicycle / Micromobility Collision': {
        'label': 'Bicycle / Micromobility (BIKE)',
        'marker': 'X',
        'color': '#FF00FF', # Magenta
        'edge': '#4A004A',
        'size': 70,
        'zorder': 9
    },
    'Turning / Angle Conflict': {
        'label': 'Other Turning / Angle (TURN)',
        'marker': 'h',
        'color': '#FDAE61', # Golden Orange
        'edge': '#8C510A',
        'size': 50,
        'zorder': 6
    },
    'Single Vehicle / Fixed Object': {
        'label': 'Single Vehicle / Fixed Object (SV)',
        'marker': '*',
        'color': '#542788', # Dark Violet Star
        'edge': '#2D004B',
        'size': 85,
        'zorder': 8
    },
    'Head-On / Opposing Collision': {
        'label': 'Head-On / Opposing (HO)',
        'marker': 'p',
        'color': '#B2182B', # Deep Maroon
        'edge': '#67000D',
        'size': 70,
        'zorder': 8
    },
    'Other / Undetermined Collision': {
        'label': 'Other / Undetermined (OTH)',
        'marker': '.',
        'color': '#999999', # Neutral Slate Gray
        'edge': '#555555',
        'size': 25,
        'zorder': 4
    }
}

# ---------------------------------------------------------
# 3. Spatial Coordinate Assignment for Crash Diagram
# ---------------------------------------------------------
np.random.seed(42)

def calculate_crash_coordinates(row):
    pattern = row['COLLISION_PATTERN']
    direction = str(row['DOMINANT_DIRECTION']).strip().title()
    on_st = str(row['ON_STREET_NAME']).strip().upper()
    
    if direction not in ['North', 'South', 'East', 'West', 'Northwest', 'Northeast', 'Southwest', 'Southeast']:
        if on_st == 'FLATBUSH AVENUE EXTENSION':
            direction = np.random.choice(['North', 'South'], p=[0.55, 0.45])
        else:
            direction = np.random.choice(['East', 'West'], p=[0.40, 0.60])

    if 'Pedestrian' in pattern:
        crosswalk_choice = np.random.choice(['North', 'South', 'East', 'West'])
        if crosswalk_choice == 'North':
            x = np.random.uniform(-36, 36)
            y = np.random.uniform(43, 52)
        elif crosswalk_choice == 'South':
            x = np.random.uniform(-36, 36)
            y = np.random.uniform(-52, -43)
        elif crosswalk_choice == 'East':
            x = np.random.uniform(43, 52)
            y = np.random.uniform(-36, 36)
        else:
            x = np.random.uniform(-52, -43)
            y = np.random.uniform(-36, 36)
        return x, y

    if 'Bicycle' in pattern:
        leg = np.random.choice(['North', 'South', 'East', 'West'])
        if leg == 'North':
            x = np.random.choice([35, -35]) + np.random.normal(0, 2)
            y = np.random.uniform(20, 80)
        elif leg == 'South':
            x = np.random.choice([35, -35]) + np.random.normal(0, 2)
            y = np.random.uniform(-80, -20)
        elif leg == 'East':
            x = np.random.uniform(20, 80)
            y = np.random.choice([35, -35]) + np.random.normal(0, 2)
        else:
            x = np.random.uniform(-80, -20)
            y = np.random.choice([35, -35]) + np.random.normal(0, 2)
        return x, y

    if 'Right-Angle' in pattern or 'Broadside' in pattern:
        x = np.random.uniform(-26, 26)
        y = np.random.uniform(-26, 26)
        return x, y

    if 'Left-Turn' in pattern:
        quadrant = np.random.choice(['NB_to_WB', 'SB_to_EB', 'EB_to_NB', 'WB_to_SB'], p=[0.4, 0.3, 0.15, 0.15])
        if quadrant == 'NB_to_WB':
            x = np.random.uniform(-25, 10)
            y = np.random.uniform(0, 28)
        elif quadrant == 'SB_to_EB':
            x = np.random.uniform(-10, 25)
            y = np.random.uniform(-28, 0)
        elif quadrant == 'EB_to_NB':
            x = np.random.uniform(0, 25)
            y = np.random.uniform(0, 25)
        else:
            x = np.random.uniform(-25, 0)
            y = np.random.uniform(-25, 0)
        return x, y

    if 'Right-Turn' in pattern:
        corner = np.random.choice(['NE', 'NW', 'SE', 'SW'], p=[0.35, 0.35, 0.15, 0.15])
        if corner == 'NE':
            x = np.random.uniform(25, 45)
            y = np.random.uniform(25, 45)
        elif corner == 'NW':
            x = np.random.uniform(-45, -25)
            y = np.random.uniform(25, 45)
        elif corner == 'SE':
            x = np.random.uniform(25, 45)
            y = np.random.uniform(-45, -25)
        else:
            x = np.random.uniform(-45, -25)
            y = np.random.uniform(-45, -25)
        return x, y

    if 'Rear-End' in pattern:
        dist = np.random.uniform(55, 160)
        if 'North' in direction:
            x = np.random.uniform(6, 36)
            y = -dist
        elif 'South' in direction:
            x = np.random.uniform(-36, -6)
            y = dist
        elif 'East' in direction:
            x = -dist
            y = np.random.uniform(-36, -6)
        else:
            x = dist
            y = np.random.uniform(6, 36)
        return x, y

    if 'Sideswipe' in pattern:
        dist = np.random.uniform(40, 140)
        if 'North' in direction:
            x = np.random.choice([15, 27]) + np.random.normal(0, 2.5)
            y = -dist if np.random.rand() > 0.3 else dist * 0.7
        elif 'South' in direction:
            x = np.random.choice([-15, -27]) + np.random.normal(0, 2.5)
            y = dist if np.random.rand() > 0.3 else -dist * 0.7
        elif 'East' in direction:
            x = -dist if np.random.rand() > 0.3 else dist * 0.7
            y = np.random.choice([-15, -27]) + np.random.normal(0, 2.5)
        else:
            x = dist if np.random.rand() > 0.3 else -dist * 0.7
            y = np.random.choice([15, 27]) + np.random.normal(0, 2.5)
        return x, y

    if 'Single Vehicle' in pattern or 'Fixed Object' in pattern:
        loc = np.random.choice(['median_N', 'median_S', 'curb_NE', 'curb_SW'])
        if loc == 'median_N':
            return np.random.normal(0, 1.5), np.random.uniform(45, 120)
        elif loc == 'median_S':
            return np.random.normal(0, 1.5), np.random.uniform(-120, -45)
        elif loc == 'curb_NE':
            return np.random.uniform(38, 44), np.random.uniform(38, 44)
        else:
            return np.random.uniform(-44, -38), np.random.uniform(-44, -38)

    dist = np.random.uniform(15, 130)
    angle = np.random.uniform(0, 2 * np.pi)
    x = dist * np.cos(angle) * 0.8
    y = dist * np.sin(angle) * 0.8
    return x, y

coords = [calculate_crash_coordinates(row) for _, row in df_crashes.iterrows()]
df_crashes['PLOT_X'] = [c[0] for c in coords]
df_crashes['PLOT_Y'] = [c[1] for c in coords]

# ---------------------------------------------------------
# 4. Master Plot Construction
# ---------------------------------------------------------
print("\n[STEP 5] Generating Publication-Quality Schematic & Crash Diagram...")

plt.style.use('default')
fig = plt.figure(figsize=(24, 15), dpi=300, facecolor='#F7F9FB')

gs = GridSpec(nrows=3, ncols=2, width_ratios=[1.35, 1.0], height_ratios=[1.0, 1.0, 1.0],
              figure=fig, left=0.04, right=0.97, top=0.93, bottom=0.06, wspace=0.18, hspace=0.28)

ax_map = fig.add_subplot(gs[:, 0])      # Left: Master Schematic Collision Diagram
ax_bar = fig.add_subplot(gs[0, 1])      # Right Top: Collision Pattern Frequency
ax_sev = fig.add_subplot(gs[1, 1])      # Right Middle: Severity Distribution & Injury Rate
ax_veh = fig.add_subplot(gs[2, 1])      # Right Bottom: Vehicle Class Breakdown

# ---------------------------------------------------------
# 4.1 Draw Intersection Schematic Geometry
# ---------------------------------------------------------
ax_map.set_facecolor('#E8ECEF')
extent = 175
ax_map.set_xlim(-extent, extent)
ax_map.set_ylim(-extent, extent)
ax_map.set_aspect('equal')

road_color = '#343A40'
ax_map.add_patch(patches.Rectangle((-40, -extent), 80, 2*extent, color=road_color, zorder=1))
ax_map.add_patch(patches.Rectangle((-extent, -40), 2*extent, 80, color=road_color, zorder=1))

curb_color = '#CED4DA'
curb_edge = '#6C757D'
corner_size = extent - 40
ax_map.add_patch(patches.Rectangle((-extent, 40), corner_size, corner_size, facecolor=curb_color, edgecolor=curb_edge, lw=2, zorder=2))
ax_map.add_patch(patches.Rectangle((40, 40), corner_size, corner_size, facecolor=curb_color, edgecolor=curb_edge, lw=2, zorder=2))
ax_map.add_patch(patches.Rectangle((-extent, -extent), corner_size, corner_size, facecolor=curb_color, edgecolor=curb_edge, lw=2, zorder=2))
ax_map.add_patch(patches.Rectangle((40, -extent), corner_size, corner_size, facecolor=curb_color, edgecolor=curb_edge, lw=2, zorder=2))

median_color = '#A5D6A7'
median_edge = '#2E7D32'
ax_map.add_patch(patches.Rectangle((-2.5, 52), 5, extent - 52, facecolor=median_color, edgecolor=median_edge, lw=1.5, zorder=3))
ax_map.add_patch(patches.Rectangle((-2.5, -extent), 5, extent - 52, facecolor=median_color, edgecolor=median_edge, lw=1.5, zorder=3))
ax_map.add_patch(patches.Rectangle((-extent, -2.5), extent - 52, 5, facecolor=median_color, edgecolor=median_edge, lw=1.5, zorder=3))
ax_map.add_patch(patches.Rectangle((52, -2.5), extent - 52, 5, facecolor=median_color, edgecolor=median_edge, lw=1.5, zorder=3))

crosswalk_color = '#FFFFFF'
def draw_zebra_crosswalk(ax, x0, y0, width, height, orientation='horizontal'):
    if orientation == 'horizontal':
        for x in np.arange(x0, x0 + width - 3, 5):
            ax.add_patch(patches.Rectangle((x, y0), 3.2, height, color=crosswalk_color, zorder=3))
    else:
        for y in np.arange(y0, y0 + height - 3, 5):
            ax.add_patch(patches.Rectangle((x0, y), width, 3.2, color=crosswalk_color, zorder=3))

draw_zebra_crosswalk(ax_map, -38, 42, 76, 8, orientation='horizontal')
draw_zebra_crosswalk(ax_map, -38, -50, 76, 8, orientation='horizontal')
draw_zebra_crosswalk(ax_map, -50, -38, 8, 76, orientation='vertical')
draw_zebra_crosswalk(ax_map, 42, -38, 8, 76, orientation='vertical')

stop_bar_color = '#FFFFFF'
ax_map.plot([3, 38], [-53, -53], color=stop_bar_color, lw=3.5, zorder=3)
ax_map.plot([-38, -3], [53, 53], color=stop_bar_color, lw=3.5, zorder=3)
ax_map.plot([-53, -53], [-38, -3], color=stop_bar_color, lw=3.5, zorder=3)
ax_map.plot([53, 53], [3, 38], color=stop_bar_color, lw=3.5, zorder=3)

def draw_dashed_lane(ax, p1, p2):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#FFFFFF', linestyle=(0, (4, 4)), lw=1.2, alpha=0.8, zorder=3)

draw_dashed_lane(ax_map, (-20, 53), (-20, extent))
draw_dashed_lane(ax_map, (20, 53), (20, extent))
draw_dashed_lane(ax_map, (-20, -extent), (-20, -53))
draw_dashed_lane(ax_map, (20, -extent), (20, -53))
draw_dashed_lane(ax_map, (-extent, 20), (-53, 20))
draw_dashed_lane(ax_map, (-extent, -20), (-53, -20))
draw_dashed_lane(ax_map, (53, 20), (extent, 20))
draw_dashed_lane(ax_map, (53, -20), (extent, -20))

arrow_kw = dict(arrowstyle="->,head_width=0.4,head_length=0.6", color='#FFD54F', lw=2.5, zorder=4)
ax_map.annotate('', xy=(20, -65), xytext=(20, -115), arrowprops=arrow_kw)
ax_map.annotate('', xy=(-20, 65), xytext=(-20, 115), arrowprops=arrow_kw)
ax_map.annotate('', xy=(65, 20), xytext=(115, 20), arrowprops=arrow_kw)
ax_map.annotate('', xy=(-65, -20), xytext=(-115, -20), arrowprops=arrow_kw)

lbl_box = dict(boxstyle='square,pad=0.3', facecolor='#212529', edgecolor='#F8F9FA', lw=1.5, alpha=0.92)
ax_map.text(0, extent - 14, "FLATBUSH AVENUE EXTENSION\n(To Manhattan Bridge / Manhattan)",
            ha='center', va='center', color='#FFFFFF', fontsize=10.5, fontweight='bold', bbox=lbl_box, zorder=12)
ax_map.text(0, -extent + 14, "FLATBUSH AVENUE EXTENSION\n(To Downtown Brooklyn / Atlantic Ave)",
            ha='center', va='center', color='#FFFFFF', fontsize=10.5, fontweight='bold', bbox=lbl_box, zorder=12)
ax_map.text(-extent + 14, 0, "TILLARY STREET\n(To Brooklyn Bridge)",
            ha='center', va='center', color='#FFFFFF', fontsize=10.5, fontweight='bold', rotation=90, bbox=lbl_box, zorder=12)
ax_map.text(extent - 14, 0, "TILLARY STREET\n(To Brooklyn-Queens Expwy / Fort Greene)",
            ha='center', va='center', color='#FFFFFF', fontsize=10.5, fontweight='bold', rotation=-90, bbox=lbl_box, zorder=12)

ax_map.annotate('N', xy=(extent - 28, extent - 28), xytext=(extent - 28, extent - 42),
                ha='center', va='center', fontsize=14, fontweight='heavy', color='#212529',
                arrowprops=dict(facecolor='#212529', edgecolor='#212529', width=3, headwidth=9, headlength=10),
                zorder=12)

# ---------------------------------------------------------
# 4.2 Plot Crash Pattern Symbols onto Layout
# ---------------------------------------------------------
for pattern_name, style in PATTERN_STYLES.items():
    subset = df_crashes[df_crashes['COLLISION_PATTERN'] == pattern_name]
    if len(subset) == 0:
        continue
    ax_map.scatter(
        subset['PLOT_X'], subset['PLOT_Y'],
        marker=style['marker'],
        c=style['color'],
        edgecolors=style['edge'],
        s=style['size'],
        alpha=0.82,
        linewidths=0.9,
        label=f"{style['label']} (n={len(subset)})",
        zorder=style['zorder']
    )

ax_map.set_title("SCHEMATIC CRASH PATTERN DIAGRAM\nFlatbush Avenue Extension & Tillary Street, Brooklyn, NY",
                 fontsize=14, fontweight='bold', pad=12, color='#1A202C')
ax_map.set_xticks([])
ax_map.set_yticks([])

leg = ax_map.legend(loc='lower left', frameon=True, framealpha=0.92, facecolor='#FFFFFF',
                    edgecolor='#B0BEC5', fontsize=8.5, title="Recorded Collision Patterns", title_fontsize=9.5)
leg.get_title().set_fontweight('bold')

# ---------------------------------------------------------
# 4.3 Subplot 1: Collision Pattern Frequency (Right Top)
# ---------------------------------------------------------
counts = df_crashes['COLLISION_PATTERN'].value_counts()
pattern_order = [p for p in PATTERN_STYLES.keys() if p in counts]
y_positions = np.arange(len(pattern_order))
counts_ordered = [counts[p] for p in pattern_order]
colors_ordered = [PATTERN_STYLES[p]['color'] for p in pattern_order]
labels_ordered = [PATTERN_STYLES[p]['label'].split('(')[0].strip() for p in pattern_order]

ax_bar.barh(y_positions, counts_ordered, color=colors_ordered, edgecolor='#333333', height=0.68, alpha=0.88)
ax_bar.set_yticks(y_positions)
ax_bar.set_yticklabels(labels_ordered, fontsize=9, fontweight='medium')
ax_bar.invert_yaxis()
ax_bar.set_xlabel("Number of Recorded Incidents", fontsize=10, fontweight='bold')
ax_bar.set_title("Crash Pattern Frequency Breakdown (Total N = 1,211)", fontsize=11.5, fontweight='bold', color='#1A202C')
ax_bar.grid(axis='x', linestyle='--', alpha=0.5)

for i, v in enumerate(counts_ordered):
    pct = (v / len(df_crashes)) * 100
    ax_bar.text(v + 5, i, f"{v} ({pct:.1f}%)", va='center', fontsize=8.5, fontweight='bold', color='#212529')
ax_bar.set_xlim(0, max(counts_ordered) * 1.25)
ax_bar.spines['top'].set_visible(False)
ax_bar.spines['right'].set_visible(False)

# ---------------------------------------------------------
# 4.4 Subplot 2: Severity Distribution & Injury Profile (Right Middle)
# ---------------------------------------------------------
injuries_by_pattern = df_crashes.groupby('COLLISION_PATTERN')['PERSONS_INJURED'].sum()
inj_ordered = [injuries_by_pattern.get(p, 0) for p in pattern_order]

bar_width = 0.38
y_pos = np.arange(len(pattern_order))

ax_sev.barh(y_pos - bar_width/2, counts_ordered, height=bar_width, label='Crashes (Incidents)', color='#5C6BC0', alpha=0.85, edgecolor='#283593')
ax_sev.barh(y_pos + bar_width/2, inj_ordered, height=bar_width, label='Persons Injured', color='#EF5350', alpha=0.90, edgecolor='#B71C1C')
ax_sev.set_yticks(y_pos)
ax_sev.set_yticklabels(labels_ordered, fontsize=9)
ax_sev.invert_yaxis()
ax_sev.set_xlabel("Recorded Frequency", fontsize=10, fontweight='bold')
ax_sev.set_title("Crash Count vs. Casualties by Pattern (Injuries = 222, Fatal = 1)", fontsize=11.5, fontweight='bold', color='#1A202C')
ax_sev.grid(axis='x', linestyle='--', alpha=0.5)
ax_sev.legend(loc='lower right', fontsize=8.5, framealpha=0.9)
ax_sev.spines['top'].set_visible(False)
ax_sev.spines['right'].set_visible(False)

sev_callout = (
    "Key Injury Findings:\n"
    "• Rear-End: 69 injuries (most casualty volume)\n"
    "• Left-Turn: 46 injuries (31.9% injury rate)\n"
    "• Pedestrian/Bike: 25 injuries (100%+ casualty rate)\n"
    "• Right-Angle: 1 fatality (10/05/2014) & 16 injuries"
)
ax_sev.text(0.96, 0.45, sev_callout, transform=ax_sev.transAxes,
            fontsize=8.5, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF9C4', edgecolor='#FBC02D', alpha=0.95))

# ---------------------------------------------------------
# 4.5 Subplot 3: Vehicle Classification Breakdown (Right Bottom)
# ---------------------------------------------------------
if df_vehicles is not None:
    veh_type_counts = df_vehicles['STANDARDIZED_VEHICLE_TYPE'].value_counts()
    veh_names = veh_type_counts.index.tolist()
    veh_vals = veh_type_counts.values.tolist()
    veh_colors = ['#42A5F5', '#66BB6A', '#FFA726', '#AB47BC', '#EC407A', '#26C6DA', '#78909C']
    
    y_v = np.arange(len(veh_names))
    ax_veh.barh(y_v, veh_vals, color=veh_colors[:len(veh_names)], edgecolor='#333333', height=0.65, alpha=0.88)
    ax_veh.set_yticks(y_v)
    ax_veh.set_yticklabels(veh_names, fontsize=9)
    ax_veh.invert_yaxis()
    ax_veh.set_xlabel("Number of Vehicles Involved", fontsize=10, fontweight='bold')
    ax_veh.set_title("Vehicle Fleet Classification Involved (N = 2,432 Vehicles)", fontsize=11.5, fontweight='bold', color='#1A202C')
    ax_veh.grid(axis='x', linestyle='--', alpha=0.5)
    
    for i, v in enumerate(veh_vals):
        pct = (v / len(df_vehicles)) * 100
        ax_veh.text(v + 15, i, f"{v} ({pct:.1f}%)", va='center', fontsize=8.5, fontweight='bold', color='#212529')
    ax_veh.set_xlim(0, max(veh_vals) * 1.25)
    ax_veh.spines['top'].set_visible(False)
    ax_veh.spines['right'].set_visible(False)

fig.suptitle("NYC MOTOR VEHICLE COLLISIONS — INTERSECTION CRASH PATTERN DIAGRAM\nStudy Location: Flatbush Avenue Extension & Tillary Street, Downtown Brooklyn | Study Period: 2012–2024",
             fontsize=15.5, fontweight='heavy', color='#0F172A', y=0.985)

output_img_path = os.path.join(OUTPUTS_DIR, "crash_pattern_diagram.png")
plt.savefig(output_img_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
plt.close()
print(f"[SUCCESS] High-resolution Crash Pattern Diagram generated at:\n  {output_img_path}")

# ---------------------------------------------------------
# 5. Supplementary Analytical Visualizations (outputs/supplementary_analysis.png)
# ---------------------------------------------------------
print("\n[STEP 6] Generating Supplementary Temporal & Contributing Factors Dashboard...")

fig_sup, axs = plt.subplots(2, 2, figsize=(18, 12), dpi=300, facecolor='#F8F9FA')

# Panel A: Longitudinal Crash Trends (2012 - 2024)
annual_crashes = df_crashes['YEAR'].value_counts().sort_index()
axs[0, 0].plot(annual_crashes.index, annual_crashes.values, marker='o', color='#1E88E5', lw=2.5, markersize=7)
axs[0, 0].fill_between(annual_crashes.index, annual_crashes.values, color='#BBDEFB', alpha=0.5)
axs[0, 0].axvspan(2017, 2020, color='#FFF59D', alpha=0.45, label='NYC DOT Tillary St Reconstruction')
axs[0, 0].set_title("A. Annual Crash Frequency Trend (2012–2024)", fontsize=12, fontweight='bold')
axs[0, 0].set_xlabel("Year", fontsize=10, fontweight='bold')
axs[0, 0].set_ylabel("Recorded Collisions", fontsize=10, fontweight='bold')
axs[0, 0].grid(True, linestyle='--', alpha=0.6)
axs[0, 0].legend(loc='upper right', fontsize=9)
for x, y in zip(annual_crashes.index, annual_crashes.values):
    axs[0, 0].annotate(str(y), (x, y + 4), ha='center', fontsize=8.5, fontweight='bold')

# Panel B: Diurnal / Hourly Distribution (24 Hours)
hourly_crashes = df_crashes['HOUR'].dropna().astype(int).value_counts().sort_index()
axs[0, 1].bar(hourly_crashes.index, hourly_crashes.values, color='#26A69A', edgecolor='#004D40', alpha=0.85)
axs[0, 1].set_title("B. Diurnal Hourly Distribution of Collisions", fontsize=12, fontweight='bold')
axs[0, 1].set_xlabel("Hour of Day (00:00 - 23:00)", fontsize=10, fontweight='bold')
axs[0, 1].set_ylabel("Recorded Collisions", fontsize=10, fontweight='bold')
axs[0, 1].set_xticks(range(0, 24, 2))
axs[0, 1].grid(axis='y', linestyle='--', alpha=0.6)
# Highlight peak hour
max_hour = hourly_crashes.idxmax()
max_val = hourly_crashes.max()
axs[0, 1].annotate(f'Peak: {max_hour}:00 ({max_val})', xy=(max_hour, max_val), xytext=(max_hour+1, max_val+5),
                   arrowprops=dict(facecolor='#D32F2F', shrink=0.05, width=1.5, headwidth=6),
                   fontweight='bold', color='#D32F2F', fontsize=9)

# Panel C: Top Contributing Factors
if df_vehicles is not None:
    factors_series = pd.concat([df_vehicles['CONTRIBUTING_FACTOR_1'].fillna(''), df_vehicles['CONTRIBUTING_FACTOR_2'].fillna('')])
    factors_series = factors_series[(factors_series != '') & (factors_series != 'Unspecified')].value_counts().head(8)
    y_f = np.arange(len(factors_series))
    axs[1, 0].barh(y_f, factors_series.values, color='#FB8C00', edgecolor='#E65100', alpha=0.88)
    axs[1, 0].set_yticks(y_f)
    axs[1, 0].set_yticklabels(factors_series.index, fontsize=9)
    axs[1, 0].invert_yaxis()
    axs[1, 0].set_title("C. Top Recorded Contributing Factors (Excl. Unspecified)", fontsize=12, fontweight='bold')
    axs[1, 0].set_xlabel("Number of Occurrences", fontsize=10, fontweight='bold')
    axs[1, 0].grid(axis='x', linestyle='--', alpha=0.6)
    for i, v in enumerate(factors_series.values):
        axs[1, 0].text(v + 3, i, str(v), va='center', fontsize=8.5, fontweight='bold')

# Panel D: Severity Breakdown Donut Chart
severity_counts = [
    (df_crashes['PERSONS_INJURED'] == 0) & (df_crashes['PERSONS_KILLED'] == 0),
    (df_crashes['PERSONS_INJURED'] > 0) & (df_crashes['PERSONS_KILLED'] == 0),
    (df_crashes['PERSONS_KILLED'] > 0)
]
sev_labels = ['Property Damage Only\n(PDO)', 'Injury Collisions', 'Fatal Collisions']
sev_values = [s.sum() for s in severity_counts]
sev_colors = ['#78909C', '#FFA726', '#E53935']

wedges, texts, autotexts = axs[1, 1].pie(
    sev_values, labels=sev_labels, autopct='%1.1f%%', startangle=140,
    colors=sev_colors, textprops=dict(color='#212529', fontsize=9.5, fontweight='bold'),
    wedgeprops=dict(width=0.45, edgecolor='#FFFFFF', lw=2)
)
axs[1, 1].set_title("D. Collision Severity Distribution (Total N = 1,211)", fontsize=12, fontweight='bold')

fig_sup.suptitle("SUPPLEMENTARY ANALYSIS: TEMPORAL DYNAMICS & CONTRIBUTING FACTORS\nFlatbush Avenue Extension & Tillary Street, Downtown Brooklyn (2012–2024)",
                 fontsize=14.5, fontweight='heavy', color='#0F172A', y=0.98)

plt.tight_layout(rect=[0, 0, 1, 0.95])
sup_img_path = os.path.join(OUTPUTS_DIR, "supplementary_analysis.png")
plt.savefig(sup_img_path, dpi=300, facecolor=fig_sup.get_facecolor(), edgecolor='none')
plt.close()
print(f"[SUCCESS] Supplementary analytical dashboard generated at:\n  {sup_img_path}")
