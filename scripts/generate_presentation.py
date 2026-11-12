"""
Script: scripts/generate_presentation.py
Description: Generates a professional PowerPoint presentation (Project_2_Presentation.pptx)
for Project 2: Preparation of Crash Pattern Diagrams at Selected Urban Intersections.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
PPTX_PATH = os.path.join(BASE_DIR, "Project_2_Presentation.pptx")

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color Palette: Deep Navy, Crimson, Slate Gray, Pure White
NAVY = RGBColor(15, 23, 42)       # #0F172A
BLUE = RGBColor(30, 64, 175)      # #1E40AF
AMBER = RGBColor(217, 119, 6)     # #D97706
RED = RGBColor(220, 38, 38)       # #DC2626
GRAY = RGBColor(71, 85, 105)      # #475569
LIGHT_BG = RGBColor(248, 250, 252) # #F8FAFC
WHITE = RGBColor(255, 255, 255)

def add_header(slide, title_text, category_text="SAFETY ENGINEERING COURSEWORK | PROJECT 2"):
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.9))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p0 = tf.paragraphs[0]
    p0.text = category_text.upper()
    p0.font.size = Pt(10)
    p0.font.bold = True
    p0.font.color.rgb = BLUE
    
    p1 = tf.add_paragraph()
    p1.text = title_text
    p1.font.size = Pt(22)
    p1.font.bold = True
    p1.font.color.rgb = NAVY

def add_card(slide, left, top, width, height, bg_color=WHITE, border_color=RGBColor(226, 232, 240)):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.5)
    return shape

# -------------------------------------------------------------
# SLIDE 1: Title Slide (Dark Theme)
# -------------------------------------------------------------
slide1 = prs.slides.add_slide(prs.slide_layouts[6])
bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg1.fill.solid()
bg1.fill.fore_color.rgb = NAVY
bg1.line.fill.background()

tb1 = slide1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(3.8))
tf1 = tb1.text_frame
tf1.word_wrap = True

p = tf1.paragraphs[0]
p.text = "SAFETY ENGINEERING COURSEWORK — PROJECT 2"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = RGBColor(96, 165, 250)

p = tf1.add_paragraph()
p.text = "Preparation of Crash Pattern Diagrams at Selected Urban Intersections"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = WHITE
p.space_before = Pt(14)

p = tf1.add_paragraph()
p.text = "Empirical Collision Analysis, Pattern Typology, and Collision Mapping at Flatbush Ave Ext & Tillary St, Brooklyn, NY"
p.font.size = Pt(16)
p.font.color.rgb = RGBColor(203, 213, 225)
p.space_before = Pt(12)

p = tf1.add_paragraph()
p.text = "Author: Rishabh Prajapat | Dataset: NYPD Motor Vehicle Collisions (2012–2024, N = 1,211 Collisions)"
p.font.size = Pt(12)
p.font.color.rgb = RGBColor(148, 163, 184)
p.space_before = Pt(28)

# -------------------------------------------------------------
# SLIDE 2: Executive Summary & Study Location
# -------------------------------------------------------------
slide2 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide2, "Executive Overview: Study Location & Scope")

# Left Column: Location & Context
card_loc = add_card(slide2, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4))
tb_loc = slide2.shapes.add_textbox(Inches(1.1), Inches(1.6), Inches(5.0), Inches(5.0))
tf_loc = tb_loc.text_frame
tf_loc.word_wrap = True

p = tf_loc.paragraphs[0]
p.text = "Study Location Profile"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = BLUE

bullets_loc = [
    "Location: Flatbush Avenue Extension & Tillary Street (Downtown Brooklyn, NY).",
    "Functional Classification: Major Urban Arterial Intersection (AADT > 65,000 veh/day).",
    "Corridor Role: Southern portal of Manhattan Bridge (Flatbush) intersecting gateway to Brooklyn Bridge & BQE (Tillary).",
    "Geometry: 6-8 lanes, dual turn bays, pedestrian crosswalks on all 4 approaches.",
    "Vision Zero Designation: Ranked as a top-tier NYC DOT Priority Intersection for safety interventions."
]
for b in bullets_loc:
    p = tf_loc.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(12.5)
    p.font.color.rgb = GRAY
    p.space_before = Pt(8)

# Right Column: Analytical Scope & Sample
card_scope = add_card(slide2, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.4))
tb_scope = slide2.shapes.add_textbox(Inches(7.1), Inches(1.6), Inches(5.1), Inches(5.0))
tf_scope = tb_scope.text_frame
tf_scope.word_wrap = True

p = tf_scope.paragraphs[0]
p.text = "Data Sample & Analytical Metrics"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = BLUE

metrics = [
    ("Total Recorded Collisions", "1,211 Crashes"),
    ("Historical Study Horizon", "July 2012 – October 2024 (12.3 Years)"),
    ("Matched Vehicle Records", "2,432 Vehicles (99.8% Match Rate)"),
    ("Casualty Burden", "222 Persons Injured | 1 Fatality"),
    ("Property Damage Only (PDO)", "1,056 Incidents (87.20%)"),
    ("Injury-Incurring Collisions", "154 Incidents (12.72%)")
]
for label, val in metrics:
    p = tf_scope.add_paragraph()
    p.text = f"{label}: "
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = NAVY
    p.space_before = Pt(6)
    
    run = p.add_run()
    run.text = val
    run.font.bold = False
    run.font.color.rgb = BLUE

# -------------------------------------------------------------
# SLIDE 3: Methodology & Deterministic Classification
# -------------------------------------------------------------
slide3 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide3, "Methodology: Data Pipeline & Collision Typology Logic")

steps = [
    ("Step 1: Chunk-Based Extraction", "Streamed 2.3M crash records and 4.5M vehicle records in 100k chunks. Filtered bidirectional matches across ON, OFF, and CROSS street columns without sampling bias.", BLUE),
    ("Step 2: Relational Entity Resolution", "Linked vehicle movement dynamics, pre-crash maneuvers, impact points, travel directions, and contributing factors using unique COLLISION_ID keys (2,432 vehicles).", NAVY),
    ("Step 3: Objective Classification", "Engineered a deterministic hierarchy based strictly on recorded physical variables—avoiding speculative driver assumptions—yielding 8 standard FHWA/HSM collision types.", AMBER),
    ("Step 4: Geometric Layout & Mapping", "Constructed a true-scale 4-way schematic model (lanes, medians, crosswalks, stop bars) and mapped collision patterns to physical conflict zones at 300 DPI.", RED)
]

for i, (title, desc, col) in enumerate(steps):
    left = Inches(0.8 + (i % 2) * 5.9)
    top = Inches(1.5 + (i // 2) * 2.7)
    card = add_card(slide3, left, top, Inches(5.7), Inches(2.4))
    
    tb = slide3.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), Inches(5.2), Inches(2.0))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = col
    
    p = tf.add_paragraph()
    p.text = desc
    p.font.size = Pt(11.5)
    p.font.color.rgb = GRAY
    p.space_before = Pt(6)

# -------------------------------------------------------------
# SLIDE 4: Empirical Findings - Collision Pattern Breakdown
# -------------------------------------------------------------
slide4 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide4, "Empirical Results: Collision Typology & Severity Breakdown")

# Add summary table
table_shape = slide4.shapes.add_table(10, 5, Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.3))
table = table_shape.table

headers = ["Collision Pattern Category", "Count (N)", "% Share", "Injuries", "Injury Severity Rate"]
for col_idx, h in enumerate(headers):
    cell = table.cell(0, col_idx)
    cell.text = h
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY
    p = cell.text_frame.paragraphs[0]
    p.font.bold = True
    p.font.size = Pt(11.5)
    p.font.color.rgb = WHITE

rows_data = [
    ("Rear-End Collision", "291", "24.03%", "69", "23.71%"),
    ("Right-Turn / Merging Conflict", "175", "14.45%", "10", "5.71%"),
    ("Left-Turn / Opposing-Flow Conflict", "144", "11.89%", "46", "31.94% (High Risk)"),
    ("Sideswipe (Same Direction)", "118", "9.74%", "7", "5.93%"),
    ("Turning / Angle Conflict", "40", "3.30%", "4", "10.00%"),
    ("Right-Angle (Broadside) Collision", "39", "3.22%", "16 (1 Fatal)", "41.03% (Maximum Trauma)"),
    ("Single Vehicle / Fixed Object", "25", "2.06%", "8", "32.00%"),
    ("Pedestrian Collision", "16", "1.32%", "17", "106.25% (Extreme VRU Risk)"),
    ("Bicycle / Micromobility Collision", "13", "1.07%", "8", "61.54%")
]

for row_idx, r in enumerate(rows_data, start=1):
    for col_idx, val in enumerate(r):
        cell = table.cell(row_idx, col_idx)
        cell.text = val
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(241, 245, 249) if row_idx % 2 == 0 else WHITE
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(10.5)
        p.font.color.rgb = NAVY if col_idx != 4 else (RED if "High" in val or "Maximum" in val or "Extreme" in val else NAVY)
        p.font.bold = True if col_idx in [0, 4] else False

# -------------------------------------------------------------
# SLIDE 5: Master Schematic Crash Pattern Diagram
# -------------------------------------------------------------
slide5 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide5, "Master Schematic Collision Pattern Diagram (FHWA Scaled Layout)")

diag_img = os.path.join(OUTPUTS_DIR, "crash_pattern_diagram.png")
if os.path.exists(diag_img):
    slide5.shapes.add_picture(diag_img, Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.5))

# -------------------------------------------------------------
# SLIDE 6: Longitudinal Trends & Temporal Dynamics
# -------------------------------------------------------------
slide6 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide6, "Temporal Dynamics & Safety Impact of NYC Vision Zero Reconstruction")

sup_img = os.path.join(OUTPUTS_DIR, "supplementary_analysis.png")
if os.path.exists(sup_img):
    slide6.shapes.add_picture(sup_img, Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.5))

# -------------------------------------------------------------
# SLIDE 7: Engineering Discussion & Conflict Analysis
# -------------------------------------------------------------
slide7 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide7, "Engineering Discussion: Conflict Mechanics & Contributing Factors")

findings = [
    ("Rear-End Shockwaves (n = 291)", "Heavy Manhattan Bridge descent traffic abruptly encounters signalized queue spillback. Primary recorded factors: Following Too Closely (n = 162) and Driver Inattention (n = 222).", AMBER),
    ("Permissive Left-Turn Hazards (n = 144)", "Permissive left turns across 3 opposing through lanes force gap estimation under sight-distance masking, resulting in 46 injuries (31.9% injury rate).", RED),
    ("Broadside Trauma & Fatality (n = 39)", "Right-angle collisions yielded 16 injuries and 1 motorist fatality (Failure to Yield Right-of-Way), reflecting the severe vulnerability of vehicle side compartments.", RED),
    ("Multi-Lane Weaving & Sideswipes (n = 118)", "Heavy commercial vehicles (12.8% of fleet) and abrupt bridge ramp weaving drive side-impacts. Factors: Improper Lane Usage (n = 173), Unsafe Lane Changing (n = 108).", BLUE)
]

for i, (title, desc, col) in enumerate(findings):
    left = Inches(0.8 + (i % 2) * 5.9)
    top = Inches(1.5 + (i // 2) * 2.7)
    card = add_card(slide7, left, top, Inches(5.7), Inches(2.4))
    
    tb = slide7.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), Inches(5.2), Inches(2.0))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = col
    
    p = tf.add_paragraph()
    p.text = desc
    p.font.size = Pt(11.5)
    p.font.color.rgb = GRAY
    p.space_before = Pt(6)

# -------------------------------------------------------------
# SLIDE 8: Actionable Safety Engineering Recommendations
# -------------------------------------------------------------
slide8 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide8, "Actionable Countermeasures & Safety Recommendations")

recs = [
    ("1. Signal Phasing: Protected Left-Turns", "Eliminate all permissive green ball left turns on Flatbush and Tillary. Dedicated turn arrows directly target the crossing conflict mechanism (46 injuries).", BLUE),
    ("2. Pedestrian Safety: Leading Pedestrian Intervals", "Implement 7-10 second LPI phases prior to concurrent green indications to establish pedestrian right-of-way and mitigate the 106% VRU casualty ratio.", RED),
    ("3. Channelization: Raised Lane Separators", "Install physical lane delineators 150 ft upstream of stop lines to suppress abrupt multi-lane weaving and sideswipe collisions (118 crashes).", AMBER),
    ("4. Advanced Queue Detection & Enforcement", "Deploy bridge approach dynamic warning signs for queue shockwaves and maintain automated red-light enforcement cameras to eliminate broadside fatalities.", NAVY)
]

for i, (title, desc, col) in enumerate(recs):
    left = Inches(0.8 + (i % 2) * 5.9)
    top = Inches(1.5 + (i // 2) * 2.7)
    card = add_card(slide8, left, top, Inches(5.7), Inches(2.4))
    
    tb = slide8.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), Inches(5.2), Inches(2.0))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = col
    
    p = tf.add_paragraph()
    p.text = desc
    p.font.size = Pt(11.5)
    p.font.color.rgb = GRAY
    p.space_before = Pt(6)

# -------------------------------------------------------------
# SLIDE 9: Conclusion & Deliverables Summary (Dark Theme)
# -------------------------------------------------------------
slide9 = prs.slides.add_slide(prs.slide_layouts[6])
bg9 = slide9.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg9.fill.solid()
bg9.fill.fore_color.rgb = NAVY
bg9.line.fill.background()

tb9 = slide9.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(4.5))
tf9 = tb9.text_frame
tf9.word_wrap = True

p = tf9.paragraphs[0]
p.text = "PROJECT 2 COMPLETION & REPOSITORY DELIVERABLES"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = RGBColor(96, 165, 250)

p = tf9.add_paragraph()
p.text = "All Project Deliverables Successfully Executed & Verified"
p.font.size = Pt(28)
p.font.bold = True
p.font.color.rgb = WHITE
p.space_before = Pt(10)

delivs = [
    "scripts/process_crashes.py: Fully automated data extraction, entity matching, and safety classification.",
    "scripts/generate_diagram.py: High-resolution schematic intersection model & crash pattern visualization.",
    "outputs/crash_pattern_diagram.png: Scaled 300 DPI master collision diagram with analytical dashboard.",
    "outputs/summary_stats.csv: Tabular statistical summary across all collision and severity metrics.",
    "Project_2_Report.md: Academic-grade comprehensive technical safety engineering report.",
    "Project_2_Presentation.pptx: Complete executive presentation deck."
]
for d in delivs:
    p = tf9.add_paragraph()
    p.text = "✓ " + d
    p.font.size = Pt(12.5)
    p.font.color.rgb = RGBColor(226, 232, 240)
    p.space_before = Pt(6)

prs.save(PPTX_PATH)
print(f"[SUCCESS] Generated Presentation Deck at:\n  {PPTX_PATH}")
