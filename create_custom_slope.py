"""
Build a GeoStudio SLOPE/W project from parsed geometry commands.

External boundary, material boundaries, material definitions, and material assignments
are parsed to generate a multi-layer slope stability model.
"""

import zipfile
import os
import datetime
import math

OUTPUT_FILE = "custom_slope.gsz"
PROJECT_NAME = "custom_slope"

# ─── Parse input data ────────────────────────────────────────────────────────

# External boundary coordinates (x, y pairs)
ext_raw = [
    0,465.874, 529.046,465.874, 529.046,480, 523.756,480.349, 518.466,480.698,
    513.175,481.046, 507.885,481.395, 502.594,481.744, 497.304,482.093,
    492.013,482.441, 486.723,482.79, 481.432,483.139, 476.142,483.488,
    470.851,483.836, 465.561,484.418, 460.27,485.204, 454.98,485.991,
    449.689,486.778, 444.399,487.565, 439.109,488.187, 433.818,488.604,
    428.528,489.022, 423.237,489.44, 417.947,489.858, 412.656,490.276,
    407.366,490.694, 402.075,491.111, 396.785,491.529, 391.494,491.947,
    386.204,492.477, 380.913,493.022, 375.623,493.568, 370.333,494.114,
    365.042,494.66, 359.752,495.205, 354.461,495.751, 349.171,496.051,
    343.88,496.144, 338.59,496.237, 333.299,496.33, 328.009,496.423,
    322.718,496.516, 317.428,496.609, 312.137,496.702, 306.847,496.795,
    301.556,496.888, 296.266,496.981, 290.976,497.074, 285.685,497.167,
    280.395,497.26, 275.104,497.353, 269.814,497.446, 264.523,497.539,
    259.233,497.632, 253.942,497.725, 248.652,497.818, 243.361,497.911,
    238.071,498.004, 232.78,498.097, 227.49,498.19, 222.2,498.283,
    216.909,498.376, 211.619,498.469, 206.328,498.562, 201.038,498.655,
    195.747,498.748, 190.457,498.841, 185.166,498.934, 179.876,499.028,
    174.585,499.121, 169.295,499.214, 164.004,499.307, 158.714,499.4,
    153.423,499.493, 148.133,499.586, 142.843,499.679, 137.552,499.772,
    132.262,499.865, 126.971,499.958, 121.681,500.345, 116.39,500.975,
    111.1,501.606, 105.809,502.237, 100.519,502.868, 95.228,503.499,
    89.938,504.147, 84.647,504.861, 79.357,505.576, 74.067,506.291,
    68.776,507.005, 63.486,507.72, 58.195,509.131, 52.905,510.992,
    47.614,512.194, 42.324,512.617, 37.033,513.04, 31.743,513.463,
    26.452,513.885, 21.162,514.308, 15.871,514.731, 10.581,515.154,
    5.29,515.577, 0,516, 0,465.874,
]
ext_pts = [(ext_raw[i], ext_raw[i+1]) for i in range(0, len(ext_raw), 2)]
# Remove the closing duplicate
if ext_pts[-1] == ext_pts[0]:
    ext_pts = ext_pts[:-1]

# Material boundary 1: straight line across full width
mb1 = [(0, 497.549), (529.046, 472.448)]

# Material boundary 2: polyline (left portion only)
mb2_raw = [
    0,477.827, 0.224,477.827, 0.673,477.827, 1.347,477.827, 2.244,477.827,
    11.034,477.789, 27.717,477.715, 52.291,477.602, 84.758,477.453,
    111.577,476.631, 132.748,475.137, 150.739,472.261, 172.957,465.874,
]
mb2 = [(mb2_raw[i], mb2_raw[i+1]) for i in range(0, len(mb2_raw), 2)]

# Material boundary 3: horizontal line across full width
mb3 = [(0, 466.8), (529.046, 466.8)]

# Materials
materials = [
    {"id": 1, "name": "Layer 1", "uw": 18, "cohesion": 10, "friction": 25,
     "color": "RGB=(177,200,237)"},
    {"id": 2, "name": "Layer 2", "uw": 18, "cohesion": 10, "friction": 25,
     "color": "RGB=(200,237,177)"},
    {"id": 3, "name": "Bedrock", "uw": 18, "cohesion": 10, "friction": 25,
     "color": "RGB=(200,180,160)"},
]

# ─── Geometry helpers ─────────────────────────────────────────────────────────

def interp_line(x, p1, p2):
    """Interpolate y on line segment p1-p2 at given x."""
    if abs(p2[0] - p1[0]) < 1e-10:
        return p1[1]
    t = (x - p1[0]) / (p2[0] - p1[0])
    return p1[1] + t * (p2[1] - p1[1])


def interp_polyline(x, polyline):
    """Interpolate y on a polyline at given x."""
    for i in range(len(polyline) - 1):
        x1, x2 = polyline[i][0], polyline[i+1][0]
        if min(x1, x2) - 1e-10 <= x <= max(x1, x2) + 1e-10:
            return interp_line(x, polyline[i], polyline[i+1])
    return None


def line_intersection(p1, p2, p3, p4):
    """Find intersection of line segments p1-p2 and p3-p4."""
    x1, y1 = p1; x2, y2 = p2
    x3, y3 = p3; x4, y4 = p4
    denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if abs(denom) < 1e-12:
        return None
    t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)) / denom
    u = -((x1-x2)*(y1-y3) - (y1-y2)*(x1-x3)) / denom
    if -0.001 <= t <= 1.001 and -0.001 <= u <= 1.001:
        ix = x1 + t*(x2-x1)
        iy = y1 + t*(y2-y1)
        return (round(ix, 6), round(iy, 6))
    return None


# ─── Build simplified geometry ────────────────────────────────────────────────
# Strategy: Create regions by splitting the external boundary with mat boundaries.
#
# The external boundary has:
#   - base: y=465.874 from x=0 to x=529.046
#   - right wall: x=529.046 from y=465.874 to y=480
#   - surface: from (529.046, 480) going left up to (0, 516)
#   - left wall: x=0 from y=516 down to y=465.874
#
# Material boundaries (full-width):
#   mb1: (0,497.549) → (529.046,472.448) — divides upper/lower
#   mb3: (0,466.8) → (529.046,466.8) — thin base layer
#
# mb2: local polyline from (0,477.827) to (172.957,465.874) — subdivides left portion
#
# Regions (simplified — we create 4 main regions):
#   R1: Surface to mb1 (above mb1)
#   R2: mb1 to mb3 (main soil, right of mb2 end)
#   R3: mb2 to mb3 (below mb2, left portion) — merged into R2 since mb2 ends at base
#   R4: mb3 to base (thin bedrock layer)
#
# For mb2: it subdivides the zone between mb1 and mb3 on the left side into
# an upper part (between mb1 and mb2) and a lower part (between mb2 and base/mb3).
# But since both materials 1 and 2 have same properties, we'll include mb2 as an
# internal line for visual fidelity but merge regions where possible.

# Separate external boundary into surface and base segments
# ext_pts goes: bottom-left, bottom-right, top-right (529,480), surface points..., top-left (0,516)

# Find key indices
bottom_left_idx = 0    # (0, 465.874)
bottom_right_idx = 1   # (529.046, 465.874)
top_right_idx = 2      # (529.046, 480)
# Surface points are indices 2 through N-1
# Last point before closing is (0, 516) which is the top-left

surface_pts = ext_pts[2:]  # from (529.046,480) to (0,516)

# We need intersection points of mb1 and mb3 with the external boundary edges
# mb1 hits left wall at (0, 497.549) and right wall at (529.046, 472.448)
# mb3 hits left wall at (0, 466.8) and right wall at (529.046, 466.8)

# Also need where mb1 intersects the surface (it may pass through the surface on the right side)
# At x=529.046: mb1_y = 472.448, surface_y = 480, so mb1 is below surface — hits right wall
# At x=0: mb1_y = 497.549, surface_y = 516, so mb1 is below surface — hits left wall

# Where mb2 intersects mb1:
mb2_mb1_int = None
for i in range(len(mb2) - 1):
    pt = line_intersection(mb2[i], mb2[i+1], mb1[0], mb1[1])
    if pt and mb2[i][0] - 0.1 <= pt[0] <= mb2[i+1][0] + 0.1:
        mb2_mb1_int = pt
        break

# Where mb2 intersects mb3:
mb2_mb3_int = None
for i in range(len(mb2) - 1):
    pt = line_intersection(mb2[i], mb2[i+1], mb3[0], mb3[1])
    if pt and mb2[i][0] - 0.1 <= pt[0] <= mb2[i+1][0] + 0.1:
        mb2_mb3_int = pt
        break

print(f"mb2 intersects mb1 at: {mb2_mb1_int}")
print(f"mb2 intersects mb3 at: {mb2_mb3_int}")
print(f"mb2 ends at: {mb2[-1]}")

# ─── Build points, lines, regions ────────────────────────────────────────────
# We'll create a clean geometry with these key boundary features.
#
# To keep point count manageable while preserving the surface profile,
# we'll downsample the surface to every ~3rd point.

# Downsample surface (keep every 3rd point, plus first and last)
surface_full = surface_pts  # (529.046,480) ... (0,516)
surface_ds = [surface_full[0]]
for i in range(1, len(surface_full)-1):
    if i % 3 == 0:
        surface_ds.append(surface_full[i])
surface_ds.append(surface_full[-1])

# Similarly downsample mb2
mb2_ds = [mb2[0]]
for i in range(1, len(mb2)-1):
    if i % 2 == 0:
        mb2_ds.append(mb2[i])
mb2_ds.append(mb2[-1])

# ─── Assemble all unique points ──────────────────────────────────────────────
all_points = []
point_ids = {}  # (x,y) -> ID

def add_point(x, y):
    key = (round(x, 3), round(y, 3))
    if key not in point_ids:
        pid = len(all_points) + 1
        point_ids[key] = pid
        all_points.append(key)
    return point_ids[key]

# Base corners
bl = add_point(0, 465.874)           # bottom-left
br = add_point(529.046, 465.874)     # bottom-right

# Right wall points (bottom to top)
mb3_right = add_point(529.046, 466.8)
mb1_right = add_point(529.046, 472.448)

# Surface points (right to left, top of ext boundary)
surface_ids = []
for x, y in surface_ds:
    surface_ids.append(add_point(x, y))

# Left wall points (top to bottom)
tl = surface_ids[-1]  # (0, 516)
mb1_left = add_point(0, 497.549)
mb2_left = add_point(0, 477.827)
mb3_left = add_point(0, 466.8)

# mb1 intermediate points (we just use the two endpoints already added)
# mb3 intermediate points (just two endpoints)

# mb2 polyline points
mb2_ids = []
for x, y in mb2_ds:
    mb2_ids.append(add_point(x, y))
# mb2 ends at (172.957, 465.874) which is on the base

# Point where mb2 meets base
mb2_base = add_point(172.957, 465.874)

# ─── Define regions ──────────────────────────────────────────────────────────
# Region 1 (Top layer — between surface and mb1):
#   Surface from (529.046,480) to (0,516), then down left wall to (0,497.549),
#   then mb1 to (529.046,472.448), then up right wall to (529.046,480)
#
# Region 2 (Main soil — between mb1 and mb2/mb3, right portion):
#   mb1 from (0,497.549) to (529.046,472.448), then down right wall to (529.046,466.8),
#   then mb3 from (529.046,466.8) to (172.957,466.8)... complex with mb2
#
# Simplification: Since mb2 only extends to x=173 and materials 1 & 2 have identical
# properties, we'll create:
#   R1: Above mb1 (full width) — assign material 1
#   R2: Between mb1 and mb2 (left, x=0 to mb2 endpoint) — assign material 1
#   R3: Between mb2 and mb3 (left, x=0 to ~173) — assign material 2
#   R4: Between mb1 and mb3 (right, x=173 to 529) — assign material 1
#   R5: Between mb3 and base (full width) — assign material 3 (Bedrock)

# For R2, R3, R4 we need the intersection of mb2 with mb1
# mb2 goes from (0,477.827) down to (172.957,465.874)
# mb1 is the line from (0,497.549) to (529.046,472.448)
# At what x do they cross? mb2 starts below mb1 at x=0 (477.8 < 497.5), so mb2 is
# always below mb1 in its range. They don't actually intersect.
# So R2 = between mb1 and mb2 on left side
# And R3 = between mb2 and mb3 on left side

# Check: at x=0, mb1=497.549, mb2=477.827, mb3=466.8 ✓ (mb1 > mb2 > mb3)
# At x=172.957, mb1 = 497.549 + (472.448-497.549)*(172.957/529.046) = 497.549 - 8.205 = 489.344
# mb2 = 465.874 (at its endpoint), mb3 = 466.8
# So mb2 dips below mb3 near its end. We need the intersection of mb2 and mb3.

# Find where mb2 crosses mb3 (y=466.8)
mb2_mb3_x = None
for i in range(len(mb2) - 1):
    if (mb2[i][1] >= 466.8 and mb2[i+1][1] <= 466.8) or (mb2[i][1] <= 466.8 and mb2[i+1][1] >= 466.8):
        # Linear interpolation
        dy = mb2[i+1][1] - mb2[i][1]
        if abs(dy) > 1e-10:
            t = (466.8 - mb2[i][1]) / dy
            mb2_mb3_x = mb2[i][0] + t * (mb2[i+1][0] - mb2[i][0])
            break

if mb2_mb3_x is not None:
    print(f"mb2 crosses mb3 at x={mb2_mb3_x:.3f}")
    mb2_mb3_pt = add_point(mb2_mb3_x, 466.8)
else:
    print("mb2 does not cross mb3, using mb2 endpoint")
    mb2_mb3_x = mb2[-1][0]
    mb2_mb3_pt = add_point(mb2_mb3_x, 466.8)

# Point on mb1 above mb2/mb3 crossing
mb1_at_mb2end_y = interp_line(mb2_mb3_x, mb1[0], mb1[1])
mb1_at_mb2end = add_point(mb2_mb3_x, mb1_at_mb2end_y)

# We also need the mb2 point right at mb3 crossing (for clean region boundary)
# Filter mb2 points to only those above mb3
mb2_above = [(x,y) for x,y in mb2_ds if y >= 466.8 - 0.01]
mb2_above_ids = [add_point(x, y) for x, y in mb2_above]
# Add the crossing point
mb2_above_ids.append(mb2_mb3_pt)

# Now define regions by listing their bounding point IDs in order.

# Region 1: Above mb1 (surface to mb1, full width)
# Go along surface (right to left), then down left wall to mb1_left,
# then along mb1 (left to right), then up right wall to surface start
r1_ids = []
r1_ids.extend(surface_ids)              # surface right→left
r1_ids.append(mb1_left)                 # down left wall
r1_ids.append(mb1_at_mb2end)            # along mb1 (intermediate point)
r1_ids.append(mb1_right)                # mb1 right end
# mb1_right is at (529.046, 472.448), surface starts at (529.046, 480)
# They share x=529.046, connected via right wall

# Region 2: Between mb1 and mb2 (left portion, x=0 to mb2_mb3_x)
r2_ids = [mb1_left, mb1_at_mb2end]
r2_ids.extend(reversed(mb2_above_ids))  # mb2 from crossing back to left

# Region 3: Between mb2 and mb3 (left portion)
r3_ids = list(mb2_above_ids)            # mb2 from left to crossing
r3_ids.append(mb3_left)                 # down to mb3 on left wall

# Region 4: Between mb1 and mb3 (right portion, mb2_mb3_x to 529.046)
r4_ids = [mb1_at_mb2end, mb1_right, mb3_right]
r4_ids.append(mb2_mb3_pt)              # back to the mb2/mb3 crossing

# Region 5: Between mb3 and base (full width, thin bedrock)
r5_ids = [mb3_left, mb2_mb3_pt, mb3_right, br, bl]

# ─── Deduplicate region point lists and ensure valid ─────────────────────────
def clean_region(ids):
    """Remove consecutive duplicates."""
    clean = [ids[0]]
    for pid in ids[1:]:
        if pid != clean[-1]:
            clean.append(pid)
    if clean[-1] == clean[0]:
        clean = clean[:-1]
    return clean

r1_ids = clean_region(r1_ids)
r2_ids = clean_region(r2_ids)
r3_ids = clean_region(r3_ids)
r4_ids = clean_region(r4_ids)
r5_ids = clean_region(r5_ids)

print(f"\nPoints: {len(all_points)}")
print(f"R1 ({len(r1_ids)} pts): above mb1")
print(f"R2 ({len(r2_ids)} pts): mb1-mb2 left")
print(f"R3 ({len(r3_ids)} pts): mb2-mb3 left")
print(f"R4 ({len(r4_ids)} pts): mb1-mb3 right")
print(f"R5 ({len(r5_ids)} pts): mb3-base")

# ─── Build lines from region edges ──────────────────────────────────────────
all_lines = set()
all_regions = [r1_ids, r2_ids, r3_ids, r4_ids, r5_ids]
for region in all_regions:
    for i in range(len(region)):
        p1 = region[i]
        p2 = region[(i+1) % len(region)]
        edge = (min(p1, p2), max(p1, p2))
        all_lines.add(edge)

all_lines = sorted(all_lines)
print(f"Lines: {len(all_lines)}")

# ─── Generate XML ────────────────────────────────────────────────────────────
now = datetime.datetime.now()
date_str = now.strftime("%m-%d-%Y")
time_str = now.strftime("%H:%M:%S")

# Points XML
points_xml = ""
for i, (x, y) in enumerate(all_points):
    points_xml += f'        <Point ID="{i+1}" X="{x}" Y="{y}" />\n'

# Lines XML
lines_xml = ""
for i, (p1, p2) in enumerate(all_lines):
    lines_xml += f"""        <Line>
          <ID>{i+1}</ID>
          <PointID1>{p1}</PointID1>
          <PointID2>{p2}</PointID2>
        </Line>\n"""

# Regions XML
regions_xml = ""
region_mat_map = {1: 1, 2: 1, 3: 2, 4: 1, 5: 3}  # region -> material
for i, region in enumerate(all_regions):
    pt_str = ",".join(str(p) for p in region)
    regions_xml += f"""        <Region>
          <ID>{i+1}</ID>
          <PointIDs>{pt_str}</PointIDs>
        </Region>\n"""

# Context material assignments
context_mats = ""
for rid, mid in region_mat_map.items():
    context_mats += f'        <GeometryUsesMaterial ID="Regions-{rid}" Entry="{mid}" />\n'

# Materials XML
materials_xml = ""
for mat in materials:
    materials_xml += f"""    <Material>
      <ID>{mat['id']}</ID>
      <Color>{mat['color']}</Color>
      <Name>{mat['name']}</Name>
      <SlopeModel>MohrCoulomb</SlopeModel>
      <StressStrain>
        <UnitWeight>{mat['uw']}</UnitWeight>
        <CohesionPrime>{mat['cohesion']}</CohesionPrime>
        <PhiPrime>{mat['friction']}</PhiPrime>
      </StressStrain>
    </Material>\n"""

# Slip surface: entry along the upper surface, exit along lower slope
# Entry on the crest area (left side, high elevation)
# Exit on the lower right portion
xml_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<GSIData Version="11.05" AppVersion="23.1.0.1001">
  <FileInfo FileVersion="11.05" AppVersion="23.01" FileBuildNumber="1001" RevNumber="1" Date="{date_str}" Time="{time_str}" />
  <Analyses Len="1">
    <Analysis>
      <ID>1</ID>
      <Name>Slope Stability - Bishop</Name>
      <Kind>SLOPE/W</Kind>
      <Method>Bishop</Method>
      <GeometryId>1</GeometryId>
      <ExcludeInitDeformation>true</ExcludeInitDeformation>
      <TimeIncrements>
        <Duration Missing="true" />
        <TimeSteps Len="1">
          <TimeStep Save="true" />
        </TimeSteps>
      </TimeIncrements>
      <IterationControls Len="1">
        <IterationControl>
          <Key>SlopeStability</Key>
          <Entry MaxIterations="100" MaxReviewIterations="10" />
        </IterationControl>
      </IterationControls>
      <ComputedPhysics SlopeStability="true" />
    </Analysis>
  </Analyses>
  <BCs Len="5">
    <BC ID="1" Name="Fixed X" Color="RGB=(192,0,0)" XDisp="DispDisplacementX(Variability=Constant,Value=0)" YDisp="ForceDispUndefined()" />
    <BC ID="2" Name="Fixed Y" Color="RGB=(192,0,0)" XDisp="ForceDispUndefined()" YDisp="DispDisplacementY(Variability=Constant,Value=0)" />
    <BC ID="3" Name="Fixed X/Y" Color="RGB=(192,0,0)" XDisp="DispDisplacementX(Variability=Constant,Value=0)" YDisp="DispDisplacementY(Variability=Constant,Value=0)" />
    <BC ID="4" Name="Zero Pressure" Color="RGB=(192,0,0)" Hydraulic="HydPressureHead(Variability=Constant,Value=0)" />
    <BC ID="5" Name="Drainage" Color="RGB=(128,0,128)" Hydraulic="HydTotalFlux(Variability=Constant,Value=0,Review=true)" />
  </BCs>
  <Contexts Len="1">
    <Context>
      <AnalysisID>1</AnalysisID>
      <GeometryUsesMaterials Len="{len(region_mat_map)}">
{context_mats}      </GeometryUsesMaterials>
      <IsDefined>true</IsDefined>
    </Context>
  </Contexts>
  <Coordinates>
    <EngCoords HorzScale="600" XPageLeft="-20" YPageBottom="460" XPageRight="550" YPageTop="520" XPageOrg="20" YPageOrg="10" MaxSnapDist="20" UnitSystem="Metric" LockScales="false" VertScale="600" />
    <PageCoords Units="in" PageWidth="11" PageHeight="8.5" PageXOrg="1.3" PageYOrg="0.8" />
  </Coordinates>
  <Geometries Len="1">
    <Geometry>
      <Name>Custom Slope</Name>
      <Points Len="{len(all_points)}">
{points_xml}      </Points>
      <Lines Len="{len(all_lines)}">
{lines_xml}      </Lines>
      <Regions Len="{len(all_regions)}">
{regions_xml}      </Regions>
      <ResultGraphs Len="1">
        <ResultGraph>
          <GraphOptions>
            <Font Height="-12" OutPrecision="1" ClipPrecision="2" Quality="1" PitchAndFamily="26" FaceName="Arial" />
            <Symbols>true</Symbols>
          </GraphOptions>
          <Name>Factor of Safety vs. Lambda</Name>
          <SourceType>SlopeConvergence</SourceType>
          <Y>ViewSlipFOS</Y>
          <X>Lambda</X>
          <IndepUnit Missing="true" />
        </ResultGraph>
      </ResultGraphs>
      <SketchItems>
        <Images Len="1">
          <Image>
            <FileName>OBJECT</FileName>
          </Image>
        </Images>
        <AxisOptions BottomAxisTitle="Distance (m)" LeftAxisTitle="Elevation (m)" TopAxisTitle="Distance" RightAxisTitle="Elevation" />
      </SketchItems>
      <Precision>6,6,7</Precision>
    </Geometry>
  </Geometries>
  <Materials Len="{len(materials)}">
{materials_xml}  </Materials>
  <StabilityItems Len="1">
    <StabilityItem>
      <AnalysisID>1</AnalysisID>
      <Entry>
        <InitialInputInfo>
          <Option>Parent</Option>
        </InitialInputInfo>
        <SlipSurface>
          <Radius NumInc="15" />
          <EntryExit>
            <LeftSideLeftPt X="0" Y="516" />
            <LeftSideRightPt X="130" Y="499.9" />
            <LeftInc>15</LeftInc>
            <RightSideLeftPt X="350" Y="496" />
            <RightSideRightPt X="529" Y="480" />
            <RightInc>15</RightInc>
          </EntryExit>
          <Limit YLeft="516" XRight="529" YRight="465" />
        </SlipSurface>
        <LambdaSettings>
          <LambdaValues Len="11">
            <LambdaValues_>-1</LambdaValues_>
            <LambdaValues_>-0.8</LambdaValues_>
            <LambdaValues_>-0.6</LambdaValues_>
            <LambdaValues_>-0.4</LambdaValues_>
            <LambdaValues_>-0.2</LambdaValues_>
            <LambdaValues_ />
            <LambdaValues_>0.2</LambdaValues_>
            <LambdaValues_>0.4</LambdaValues_>
            <LambdaValues_>0.6</LambdaValues_>
            <LambdaValues_>0.8</LambdaValues_>
            <LambdaValues_>1</LambdaValues_>
          </LambdaValues>
        </LambdaSettings>
      </Entry>
    </StabilityItem>
  </StabilityItems>
  <WaterItems Len="1">
    <WaterItem>
      <AnalysisID>1</AnalysisID>
      <Entry>
        <UnitWaterWeight>9.807</UnitWaterWeight>
        <WaterBulkMod>2083333.33</WaterBulkMod>
      </Entry>
    </WaterItem>
  </WaterItems>
  <View>
    <PreferencesTable Len="1">
      <Preferences>
        <XGridSpacing>10</XGridSpacing>
        <YGridSpacing>5</YGridSpacing>
        <ShowGrid>false</ShowGrid>
        <SnapToGrid>false</SnapToGrid>
        <RightRuler>true</RightRuler>
        <TopRuler>true</TopRuler>
        <Layers>3</Layers>
        <Points>true</Points>
        <Regions>true</Regions>
        <PointNumbers>false</PointNumbers>
        <RegionNumbers>false</RegionNumbers>
        <RegionLabelOption>Material</RegionLabelOption>
        <GroundSurfaceLine>true</GroundSurfaceLine>
        <Mesh>false</Mesh>
        <MaterialColor>true</MaterialColor>
        <MaterialBoundary>true</MaterialBoundary>
        <MeshLabels>false</MeshLabels>
        <SketchItems>true</SketchItems>
        <Pictures>true</Pictures>
        <Axis>true</Axis>
        <SeepBC>Hydraulic</SeepBC>
        <SigmaBC>Displacement</SigmaBC>
        <TempBC>Thermal</TempBC>
        <PWP>true</PWP>
        <SlipSurfaces>true</SlipSurfaces>
        <LineLoads>true</LineLoads>
        <Reinforcement>true</Reinforcement>
        <SlipSurfaceShading>true</SlipSurfaceShading>
        <SlipSurfaceSlices>true</SlipSurfaceSlices>
        <SlipSurfaceColor>RGB=(0,0,0)</SlipSurfaceColor>
        <SlipSurfaceLineThickness>1</SlipSurfaceLineThickness>
        <SigFiguresFofS>4</SigFiguresFofS>
        <FOSContours>true</FOSContours>
        <FOSContourShading>true</FOSContourShading>
        <BoundaryConditions>true</BoundaryConditions>
        <Contours>true</Contours>
        <ISOLineMode>false</ISOLineMode>
      </Preferences>
    </PreferencesTable>
    <ViewMode>Define</ViewMode>
  </View>
</GSIData>
"""

# Create the .gsz file
with zipfile.ZipFile(OUTPUT_FILE, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=5) as zf:
    zf.writestr(f"{PROJECT_NAME}.xml", xml_content.encode("utf-8"))

print(f"\nCreated {OUTPUT_FILE}")
