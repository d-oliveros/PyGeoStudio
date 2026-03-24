"""
Create a minimal empty GeoStudio .gsz project file and open it with GeoStudio.

A .gsz file is a ZIP archive containing an XML configuration file.
This script creates the bare minimum XML structure that GeoStudio accepts.
"""

import zipfile
import subprocess
import os
import datetime

OUTPUT_FILE = "empty_project.gsz"
PROJECT_NAME = "empty_project"
GEOCMD_PATH = r"C:\Program Files\Seequent\GeoStudio 2025.2\Bin"

now = datetime.datetime.now()
date_str = now.strftime("%m-%d-%Y")
time_str = now.strftime("%H:%M:%S")

# Minimal XML that GeoStudio should accept
xml_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<GSIData Version="11.01" AppVersion="11.1.3.22700">
  <FileInfo FileVersion="11.01" AppVersion="11.01" FileBuildNumber="22700" RevNumber="1" Date="{date_str}" Time="{time_str}" />
  <Analyses Len="0">
  </Analyses>
  <Contexts Len="0">
  </Contexts>
  <Coordinates>
    <EngCoords HorzScale="200" XPageLeft="-16.667" YPageBottom="-16.667" XPageRight="158.333" YPageTop="116.6663333333333" XPageOrg="16.667" YPageOrg="16.667" MaxSnapDist="20" UnitSystem="Metric" LockScales="false" VertScale="200" />
    <PageCoords Units="in" PageWidth="10.5" PageHeight="8" PageXOrg="3.280905511811024" PageYOrg="3.280905511811024" />
  </Coordinates>
  <Geometries Len="0">
  </Geometries>
  <View>
    <PreferencesTable Len="1">
      <Preferences>
        <XGridSpacing>1</XGridSpacing>
        <YGridSpacing>1</YGridSpacing>
        <ShowGrid>true</ShowGrid>
        <SnapToGrid>true</SnapToGrid>
        <RightRuler>true</RightRuler>
        <TopRuler>true</TopRuler>
        <Layers>3</Layers>
        <Points>true</Points>
        <Regions>true</Regions>
        <PointNumbers>true</PointNumbers>
        <RegionNumbers>true</RegionNumbers>
        <RegionLabelOption>Number</RegionLabelOption>
        <GroundSurfaceLine>true</GroundSurfaceLine>
        <Mesh>false</Mesh>
        <MaterialColor>true</MaterialColor>
        <MaterialBoundary>false</MaterialBoundary>
        <MeshLabels>false</MeshLabels>
        <NodeConvergence>false</NodeConvergence>
        <ReviewNodesFlipped>false</ReviewNodesFlipped>
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
        <PressureLines>true</PressureLines>
        <PressureLineShading>true</PressureLineShading>
        <TensionCrackLine>true</TensionCrackLine>
        <TensionCrackShading>true</TensionCrackShading>
        <SlipSurfaceShading>true</SlipSurfaceShading>
        <SlipSurfaceSlices>true</SlipSurfaceSlices>
        <SlipSurfaceColor>RGB=(0,0,0)</SlipSurfaceColor>
        <SlipSurfaceLineThickness>1</SlipSurfaceLineThickness>
        <MultipleSlipSurfaces>false</MultipleSlipSurfaces>
        <SigFiguresFofS>4</SigFiguresFofS>
        <AllFofSValues>false</AllFofSValues>
        <SafetyMap>false</SafetyMap>
        <FOSContours>true</FOSContours>
        <FOSContourShading>true</FOSContourShading>
        <ViewPondingArrows>true</ViewPondingArrows>
        <PWPLineThickness>Thin</PWPLineThickness>
        <Particles>true</Particles>
        <InitialConditions>true</InitialConditions>
        <BoundaryConditions>true</BoundaryConditions>
        <InitialWaterTable>true</InitialWaterTable>
        <CoverDetail>true</CoverDetail>
        <ViewImperviousBarriers>true</ViewImperviousBarriers>
        <BodyLoad>true</BodyLoad>
        <StructuralElements>true</StructuralElements>
        <TrussElements>true</TrussElements>
        <HistoryPoints>true</HistoryPoints>
        <Vectors>true</Vectors>
        <Contours>true</Contours>
        <ContourShading>false</ContourShading>
        <TransientContours>true</TransientContours>
        <TransientContourType>PoreWaterPressure</TransientContourType>
        <FlowPath>true</FlowPath>
        <Deformation>true</Deformation>
        <DeformationShading>false</DeformationShading>
        <LiquefactionConditions>false</LiquefactionConditions>
        <LiquefiedElementColor>RGB=(255,255,0)</LiquefiedElementColor>
        <ISOLineMode>false</ISOLineMode>
      </Preferences>
    </PreferencesTable>
    <ViewMode>Define</ViewMode>
  </View>
</GSIData>
"""

# Create the .gsz (ZIP) file
with zipfile.ZipFile(OUTPUT_FILE, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=5) as zf:
    zf.writestr(f"{PROJECT_NAME}.xml", xml_content.encode("utf-8"))

print(f"Created {OUTPUT_FILE}")

# Open with GeoStudio
geostudio_exe = os.path.join(GEOCMD_PATH, "GeoStudio.exe")
if not os.path.exists(geostudio_exe):
    # Try finding the main GUI executable
    bin_dir = GEOCMD_PATH
    candidates = [f for f in os.listdir(bin_dir) if "GeoStudio" in f and f.endswith(".exe")]
    print(f"Available executables with 'GeoStudio': {candidates}")
    # Fallback: just use os.startfile which opens with default association
    abs_path = os.path.abspath(OUTPUT_FILE)
    print(f"Opening {abs_path} with default association...")
    os.startfile(abs_path)
else:
    abs_path = os.path.abspath(OUTPUT_FILE)
    print(f"Opening {abs_path} with GeoStudio...")
    subprocess.Popen([geostudio_exe, abs_path])
