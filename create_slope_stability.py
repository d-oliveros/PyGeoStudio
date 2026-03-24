"""
Create a simple slope stability (SLOPE/W) analysis project.

Geometry: A simple slope with a 2:1 gradient
  - Flat top at Y=10 from X=0 to X=10
  - Slope face from (10,10) to (20,5)
  - Flat bottom at Y=0 from X=0 to X=30
  - Toe at (20,5) down to (30,0)

Material: Mohr-Coulomb with:
  - Unit weight = 127.3 pcf
  - Phi' = 25 degrees
  - c' = 104.4 psf

Slip surface: Entry-exit method searching the slope face
Analysis: Bishop method, Imperial units (ft, pcf, psf)
"""

import zipfile
import os
import datetime

OUTPUT_FILE = "slope_stability_bishop.gsz"
PROJECT_NAME = "slope_stability_bishop"

now = datetime.datetime.now()
date_str = now.strftime("%m-%d-%Y")
time_str = now.strftime("%H:%M:%S")

xml_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<GSIData Version="11.05" AppVersion="23.1.0.1001">
  <FileInfo FileVersion="11.05" AppVersion="23.01" FileBuildNumber="1001" RevNumber="1" Date="{date_str}" Time="{time_str}" />
  <Analyses Len="1">
    <Analysis>
      <ID>1</ID>
      <Name>Slope Stability</Name>
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
      <GeometryUsesMaterials Len="1">
        <GeometryUsesMaterial ID="Regions-1" Entry="1" />
      </GeometryUsesMaterials>
      <IsDefined>true</IsDefined>
    </Context>
  </Contexts>
  <Coordinates>
    <EngCoords HorzScale="200" XPageLeft="-5" YPageBottom="-3" XPageRight="40" YPageTop="20" XPageOrg="5" YPageOrg="3" MaxSnapDist="20" UnitSystem="Imperial" LockScales="false" VertScale="200" />
    <PageCoords Units="in" PageWidth="11" PageHeight="8.5" PageXOrg="1.312335958005249" PageYOrg="0.7874015748031497" />
  </Coordinates>
  <Geometries Len="1">
    <Geometry>
      <Name>Slope Geometry</Name>
      <Points Len="6">
        <Point ID="1" X="0" Y="33" />
        <Point ID="2" X="33" Y="33" />
        <Point ID="3" X="66" Y="16" />
        <Point ID="4" X="100" Y="16" />
        <Point ID="5" X="100" Y="0" />
        <Point ID="6" X="0" Y="0" />
      </Points>
      <Lines Len="6">
        <Line>
          <ID>1</ID>
          <PointID1>1</PointID1>
          <PointID2>2</PointID2>
        </Line>
        <Line>
          <ID>2</ID>
          <PointID1>2</PointID1>
          <PointID2>3</PointID2>
        </Line>
        <Line>
          <ID>3</ID>
          <PointID1>3</PointID1>
          <PointID2>4</PointID2>
        </Line>
        <Line>
          <ID>4</ID>
          <PointID1>4</PointID1>
          <PointID2>5</PointID2>
        </Line>
        <Line>
          <ID>5</ID>
          <PointID1>5</PointID1>
          <PointID2>6</PointID2>
        </Line>
        <Line>
          <ID>6</ID>
          <PointID1>6</PointID1>
          <PointID2>1</PointID2>
        </Line>
      </Lines>
      <Regions Len="1">
        <Region>
          <ID>1</ID>
          <PointIDs>1,2,3,4,5,6</PointIDs>
        </Region>
      </Regions>
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
        <AxisOptions BottomAxisTitle="Distance (ft)" LeftAxisTitle="Elevation (ft)" TopAxisTitle="Distance" RightAxisTitle="Elevation" />
      </SketchItems>
      <Precision>6,6,7</Precision>
    </Geometry>
  </Geometries>
  <Materials Len="1">
    <Material>
      <ID>1</ID>
      <Color>RGB=(177,200,237)</Color>
      <Name>Clay</Name>
      <SlopeModel>MohrCoulomb</SlopeModel>
      <StressStrain>
        <UnitWeight>127.3</UnitWeight>
        <CohesionPrime>104.4</CohesionPrime>
        <PhiPrime>25</PhiPrime>
      </StressStrain>
    </Material>
  </Materials>
  <StabilityItems Len="1">
    <StabilityItem>
      <AnalysisID>1</AnalysisID>
      <Entry>
        <InitialInputInfo>
          <Option>Parent</Option>
        </InitialInputInfo>
        <SlipSurface>
          <Radius NumInc="10" />
          <EntryExit>
            <LeftSideLeftPt X="7" Y="33" />
            <LeftSideRightPt X="33" Y="33" />
            <LeftInc>10</LeftInc>
            <RightSideLeftPt X="66" Y="16" />
            <RightSideRightPt X="92" Y="16" />
            <RightInc>10</RightInc>
          </EntryExit>
          <Limit YLeft="33" XRight="100" YRight="0" />
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
        <UnitWaterWeight>62.4</UnitWaterWeight>
        <WaterBulkMod>2083333.33</WaterBulkMod>
      </Entry>
    </WaterItem>
  </WaterItems>
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

# Create the .gsz (ZIP) file
with zipfile.ZipFile(OUTPUT_FILE, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=5) as zf:
    zf.writestr(f"{PROJECT_NAME}.xml", xml_content.encode("utf-8"))

print(f"Created {OUTPUT_FILE}")
abs_path = os.path.abspath(OUTPUT_FILE)
print(f"Opening {abs_path} with GeoStudio...")
os.startfile(abs_path)
