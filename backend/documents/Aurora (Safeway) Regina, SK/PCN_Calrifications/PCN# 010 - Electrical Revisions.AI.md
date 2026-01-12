# PCN# 010 - Electrical Revisions - Technical Data

**Project**: Aurora Grocery Store
**Location**: 2000 Anaquod Road, Regina, Saskatchewan
**PCN Number**: 2445-10
**Date**: April 24, 2025
**Electrical PCN**: #2 (dated April 23, 2025)
**Engineering Firm**: CGM Engineering Ltd.
**Architect**: Nejmark Architecture
**Project Number**: 24-258
**Contractor**: Quorex Construction Services Ltd.

---

## 1. VISUAL INTERPRETATION

### Page 3 - Site Plan and Single Line Diagram (E0.1)

**Color Coding & Visual Elements:**
- **Black lines**: Primary electrical conductors and conduit routing
- **Dashed lines**: Underground service routing and site boundaries
- **Circles with symbols**: Electrical connection points and equipment locations
- **Small site plan inset**: Shows building footprint relative to Anaquod Road with scope of work boundary indicated
- **Equipment symbols**: Transformers (TX), panels, switchgear shown with standard electrical symbols

**Spatial Layout:**
- Site plan shows building positioned along Anaquod Road
- Service entrance from SaskPower transformer on west side of property
- Main electrical room/compressor room located on second floor mezzanine
- Service conductors run underground, then penetrate building envelope via concrete shaft to second floor

**Single Line Diagram Layout:**
- Hierarchical power distribution from top to bottom
- Main service: 1600A-347/600V-3PH-4W from SaskPower
- Two main distribution paths via transformers X1 and X2 (both 450kVA)
- Multiple branch panels serving different building zones

**Key Visual Notes:**
- Revision cloud visible around service entrance area indicating PCN change
- **CRITICAL CHANGE**: Service entrance splitter has been removed (as per PCN item #1)
- Diagram shows both 600V and 208V distribution systems
- TVSS (Transient Voltage Surge Suppressor) devices indicated at multiple points

### Page 5 - Electrical Schedules (E0.2)

**Visual Layout:**
- Multiple panel schedules arranged in grid format
- Tables showing circuit breaker assignments, wire sizes, and loads
- Color differentiation between panel types (600V vs 208V systems)
- Notes sections with equipment specifications

**Luminaire Schedule Additions:**
- **Type F dock light fixture** added to schedule (per PCN item #2)
- Schedule organized by fixture type with specifications for each

### Page 7 - Floor Plan and Life Safety (E1.0/E3.0)

**Spatial Layout:**
- Complete floor plan showing all retail areas, back-of-house, and service areas
- Grid system (A-H horizontally, 1-7+ vertically) for spatial reference
- Lighting fixtures distributed throughout with type designations
- Emergency lighting and exit signs clearly marked

**Color Coding:**
- Black lines: Walls and architectural elements
- Lighter gray: Fixture locations and symbols
- Equipment symbols: Standard electrical notation for lights, exits, panels

**Key Visual Elements:**
- Receiving area (190) in northwest corner with dock doors
- Staff areas including Staff Lounge (201) in upper floor/mezzanine area
- Main sales floor with systematic lighting layout
- **New dock lights** marked in Receiving 190 area
- **Additional weatherproof emergency remote head** shown covering exterior passageway from doors 190A and 119A

---

## 2. EXTRACTED DIMENSIONS & SPECIFICATIONS

### Electrical Service

**Main Service:**
- **Service Voltage**: 347/600V-3PH-4W
- **Main Switchgear**: 1600A MD-1 (Main Distribution)
- **Main Breaker**: 1600A LSIG (Instantaneous Ground Fault)
- **Service Conductors**: 5x(4# 600 MCM ACWU90 Al.) BURIED
- **Conduit Detail**: Per Detail 5, Diagram D10, Table 10B

**Transformers:**
- **TX-X1**: 450kVA Dry-Type, 600V to 120/208V
  - Primary Protection: 400A-3P fused disconnect (equivalent to 332 kVA per CEC 26-256(3))
  - **Note**: Transformer is choked - requires lamacoid label stating "CHOKED TO 400A ON PRIMARY SIDE"
- **TX-X2**: 450kVA Dry-Type, 600V to 120/208V
  - Same specifications as TX-X1

### Distribution Panels

**600V Distribution:**
- **Panel 6L**: 100A-600V-3PH-4W, Lighting Loads, West Staff Corridor (surface mounted)
- **CDP 100A**: 400A-347/600V-3PH-4W, Compressor Room 300 (surface mounted)
- **CDP 100B**: 400A-347/600V-3PH-4W, Compressor Room 300 (surface mounted)

**208V Sub-Distribution:**
- **SD-1**: 1200A-120/208V-3PH-4W, Compressor Room 300 (surface mounted)
- **SD-2**: 1200A-120/208V-3PH-4W, Compressor Room 300 (surface mounted)

**208V Branch Panels:**
- **Panel 2A**: 200A-208V, Basic Loads, Compressor Room 300
- **Panel 2L**: 200A-208V, Lighting Loads, West Staff Corridor
- **Panel 2B**: 200A-208V, Mechanical Loads
- **Panel C1**: 100A, IT/BMS/Controls
- **Panel C2**: 200A, Checkouts/Basic Loads
- **Panel O**: 100A, Office Basic Loads
- **Panel D**: 100A, Deli
- **Panel P**: 100A, Pharmacy
- **Panel B**: 200A, Bakery
- **Panel H**: 400A, HMR (Hot Meals Ready), includes 2x(60A-3P) spaces, 2x(100A-3P) spaces
- **Panel SM**: 200A, Seafood/Meats
- **Panel R1L**: 200A, Refrigeration Panel #1
- **Panel R2L**: 400A, Refrigeration Panel #2
- **Panel R3L**: 400A, Refrigeration Panel #3
- **Panel R4L**: 400A, Refrigeration Panel #4
- **Panel R1M**: 200A, Refrigeration Panel #5
- **Panel Z**: 100A-120/208V-1PH-3W, Non-Essential Loads via ATS-Z

### Major Equipment Circuits

**HVAC Equipment:**
- **RTU-1**: 125A-3P, 4# 1 AWG RW90 Al. in 1.5" C
- **RTU-2**: 70A-3P, 4# 4 AWG RW90 Cu. in 1.0" C
- **RTU-3**: 30A-3P, 4# 10 AWG RW90 Cu. in 0.5" C
- **RTU-4**: 15A-3P, 4# 12 AWG RW90 Cu. in 0.5" C
- **RTU-5**: 15A-3P, 4# 12 AWG RW90 Cu. in 0.5" C
- **RTU-6**: 15A-3P, 4# 12 AWG RW90 Cu. in 0.5" C
- **AC-1** (Air Curtain): 30A-3P, 4# 10 AWG RW90 Cu. in 0.5" C
- **EF-1** (Exhaust Fan): 15A-3P, 4# 12 AWG RW90 Cu. in 0.5" C

**Refrigeration:**
- **Compressor Rack A**: 244 kW, 4# 500 MCM RW90 Cu. in 3.0" C
- **Gas Cooler**: 20A-3P, 4# 12 AWG RW90 Cu. in 0.5" C

**Waste Management:**
- **Compactor**: 30A-3P, 4# 1 AWG RW90 Al. in 1.5" C
- **Baler**: 30A-3P, 4# 1 AWG RW90 Al. in 1.5" C

**Emergency Power:**
- **Generator**: 22 kW, 3# 1 AWG RW90 Al. in 1.25" C
- **ATS-Z**: 100A-120/208V-1PH-3W, Standard Transition Automatic Transfer Switch

### Conductor Specifications by Circuit

**Main Feeders:**
- **To SD-1/SD-2**: 4x(4# 500 MCM RW90 Al. in 3.0" C.) each
- **Between MD-1 and Transformers**: 2x(4# 250 MCM RW90 Al. in 2.5" C.)
- **Various 200A Panels**: 4# 250 MCM RW90 Al. in 2.5" C
- **Various 400A Panels**: 2x(4# 250 MCM RW90 Al. in 2.5" C.)
- **100A Panels**: 4# 1 AWG RW90 Al. in 1.5" C

### Lighting Specifications

**New Dock Lighting (PCN Item #2):**
- **Location**: Receiving 190
- **Quantity**: Two (2) dock lights
- **Fixture Type**: Type F (added to luminaire schedule E0.3)
- **Circuit**: 15A-1P circuit breaker on Panel 2L

**Staff Lounge Revision (PCN Item #3):**
- **Location**: Staff Lounge 201
- **Change**: One (1) Type LA fixture **REPLACED** with one (1) Type N fixture
- **Drawing Reference**: 3/E1.0

**Exterior Emergency Lighting (PCN Item #4):**
- **Location**: Exterior passageway from doors 190A and 119A
- **Equipment**: Additional weatherproof emergency remote head
- **Drawing Reference**: E3.0

---

## 3. CROSS-REFERENCES

### Drawing References

**Primary Drawings in This PCN:**
- **E0.1** - Single Line Diagram (Revision 2)
- **E0.2** - Schedules
- **E0.3** - Schedules (includes new Type F dock light)
- **E1.0** - Lighting Plan (shows dock lights and Staff Lounge change)
- **E3.0** - Life Safety Plan (shows new exterior emergency head)

**Referenced Standards & Details:**
- **Detail 5, Diagram D10, Table 10B** - For buried service conductors
- **CEC 26-256(3)** - Transformer primary protection sizing (choked transformers)

### External Coordination Requirements

**Utility Coordination:**
- **SaskPower**: Pad-mount utility transformer location (approximate location shown, exact location to be coordinated on site)
- **SaskTel**: Communication utility pedestal coordination required on site
  - 3" Rigid PVC conduit from SaskTel pedestal to service telecom backboard in mezzanine
  - Owner's Internet Service Provider coordination required

**Other Disciplines:**
- **Refrigeration Contractor**: Provides roof-top generator; electrical contractor provides all conduits, conductors, and supports
- **Architectural**: Concrete shaft penetrations for service entrance
- **Mechanical**: HVAC equipment coordination (RTU units 1-6, exhaust fans)

### Related Project Documents

**Distribution List:**
- Sobeys Inc. - Jeff Craig (jeff.craig@sobeys.com)
- Sobeys Inc. - Shanwen Hsu (shanwen.hsu@sobeys.com)
- Quorex Construction Services Ltd. - Chris Walbaum (c.walbaum@quorex.ca)
- Lavergne Draward & Associates Inc. - Charles Koop (ckoop@ldaeng.ca)
- CGM Engineering - Justin Albo (justin_albo@cgmeng.ca)
- CGM Engineering - Tony Mitousis (tony_mitousis@cgmeng.ca)
- CGM Engineering - Brendan Simpson (brendan_simpson@cgmeng.ca)

**Prepared By:**
- Brendan Simpson, E.I.T. - CGM Engineering Ltd.
- Principal: Kevin Fawley, SAA MRAIC - Nejmark Architecture

---

## 4. IDENTIFIED CONFLICTS & COORDINATION ISSUES

### Design Changes (PCN #2)

**Item #1 - Service Entrance Splitter Removal:**
- **CRITICAL**: Service entrance splitter has been **REMOVED** from design
- **Action Required**: Provide credit to owner for electrical items no longer required
- **Impact**: Simplified service entrance configuration
- **Coordination**: May affect service entrance coordination with SaskPower
- **Potential Issues**:
  - Verify existing procurement status before credit processing
  - Confirm no impact to service capacity calculations
  - Review construction schedule impact

**Item #2 - Dock Lighting Addition:**
- **New Work**: Two (2) dock lights added in Receiving 190
- **Panel Impact**: Requires new 15A-1P circuit breaker on Panel 2L
- **Schedule Impact**: Type F fixture added to luminaire schedule E0.3
- **Coordination Issues**:
  - Verify Panel 2L has available circuit capacity
  - Confirm dock light specifications (Type F) meet receiving area requirements
  - Coordinate with architectural for mounting locations at dock doors
  - Ensure adequate illumination for loading/unloading operations

**Item #3 - Staff Lounge Lighting Change:**
- **Change**: One Type LA fixture → One Type N fixture in Staff Lounge 201
- **Potential Issues**:
  - Verify photometric impact of fixture type change
  - Confirm Type N fixture meets staff lounge lighting level requirements
  - May indicate cost reduction or specification alignment
  - Check if mounting/rough-in requirements differ between fixtures

**Item #4 - Exterior Emergency Lighting:**
- **New Work**: Additional weatherproof emergency remote head
- **Location**: Exterior passageway coverage for doors 190A and 119A
- **Code Compliance**: Addresses life safety requirements for exterior egress
- **Coordination Issues**:
  - Verify emergency power source connection
  - Confirm weatherproof rating suitable for Saskatchewan climate
  - Coordinate with architectural for mounting surface
  - Ensure adequate coverage overlap with existing emergency lighting

### Potential Coordination Conflicts

**Electrical Room Access:**
- Multiple panels surface-mounted in Compressor Room 300 (second floor mezzanine)
- **Risk**: Congestion in electrical/mechanical room
- **Action**: Verify adequate working clearances per CEC requirements (minimum 1m)

**Service Entrance Routing:**
- Service conductors penetrate concrete shaft within building envelope
- **Risk**: Structural coordination required for shaft dimensions
- **Action**: Verify shaft sizing accommodates 5x conduits plus telecom conduit

**Roof Equipment Coordination:**
- Six (6) RTU units plus generator on roof
- **Risk**: Conduit routing conflicts, structural loading
- **Action**: Coordinate with structural for roof penetrations and supports

**Generator Location:**
- Approximate location shown for 22 kW rooftop generator
- **Risk**: Final location may affect feeder routing
- **Action**: Coordinate with refrigeration contractor for exact placement

**Transformer Choke Labeling:**
- Transformers X1 and X2 choked to 400A primary
- **Risk**: Field installation may miss required lamacoid label
- **Action**: Ensure specification includes rivet-fastened label requirement

---

## 5. CODE COMPLIANCE NOTES

### Canadian Electrical Code (CEC) References

**CEC 26-256(3) - Transformer Primary Protection:**
- Transformers X1 and X2 utilize 400A-3P fused disconnect for 450 kVA units
- Equivalent to 332 kVA protection per code calculation
- **Compliance Method**: Choke transformers with labeled primary protection
- **Labeling Requirement**: Rivet-fastened lamacoid label stating "TRANSFORMER CHOKED TO 400A ON PRIMARY SIDE"

**Working Clearances:**
- Multiple panels in Compressor Room 300 require CEC minimum working clearances
- **Requirement**: Minimum 1.0m clear workspace in front of electrical equipment
- **Voltage Level**: 600V equipment requires enhanced clearances

**Ground Fault Protection:**
- Main breaker specified as 1600A LSIG (Low-Setting Instantaneous Ground fault)
- Provides ground fault protection for main service

**Transient Voltage Surge Suppression (TVSS):**
- TVSS devices specified at multiple panel locations
- **Purpose**: Surge protection per CEC requirements for sensitive electronic equipment
- **Locations**: Panels H, SD-1, SD-2, and main switchgear

**Emergency Power (CEC Rule 46):**
- Automatic Transfer Switch ATS-Z with standard transition
- 22 kW generator for non-essential loads
- Generator provided by refrigeration contractor (specialized application)

**Conductor Ampacity:**
- All conductor sizing appears to follow CEC Table 2 ampacity ratings
- Aluminum conductors (RW90 Al.) used for most feeders
- Copper conductors (RW90 Cu.) used for smaller branch circuits and specific equipment

### Life Safety Code Compliance

**Emergency Lighting:**
- Emergency remote heads throughout building per E3.0
- **PCN Addition**: Weatherproof emergency head for exterior egress path (doors 190A and 119A)
- **Purpose**: Ensures illumination of exterior exit routes per National Building Code of Canada (NBCC)

**Exit Signage:**
- Exit signs throughout per life safety plan
- Coordination with emergency power system

**Fire Alarm Integration:**
- Not explicitly shown in electrical PCN
- Likely separate system with coordination required

### Saskatchewan Electrical Code & Local Authority

**Inspection Authority:**
- Technical Safety Authority of Saskatchewan (TSASK) or local AHJ
- **Note**: PCN states "Authority having Jurisdiction shall advise of any objections"

**Utility Coordination:**
- **SaskPower**: Service voltage 347/600V standard for Saskatchewan commercial
- **SaskTel**: Communication service coordination

### Occupancy & Load Classification

**Building Use**: Retail Grocery Store (Group E occupancy per NBCC)
- Multiple cooking equipment circuits (HMR, Bakery, Deli)
- Extensive refrigeration loads
- Public assembly considerations for sales floor

**Load Calculations:**
- Main service 1600A appears adequately sized for grocery store with:
  - 244 kW refrigeration compressor rack
  - Multiple department panels
  - Extensive lighting loads
  - HVAC equipment (6 RTU units)

### Special Equipment Requirements

**Refrigeration Equipment:**
- Multiple refrigeration panels (R1L through R4L, R1M)
- Compressor Rack A: 244 kW major load
- Gas cooler circuit
- **Code**: CSA C22.2 standards for refrigeration equipment

**Commercial Cooking:**
- Multiple cooking equipment circuits in HMR, Deli, Bakery
- **Code**: Special consideration for commercial cooking per CEC Section 26

**Data/Telecom:**
- Separate telecom service and backboard
- IT rack circuits with dedicated panels
- **Code**: CSA T529 Design of Electrical and Fibre Optic Communication Systems

---

## 6. TECHNICAL NOTES & OBSERVATIONS

### PCN Financial Impact

**Credit Items:**
- Service entrance splitter removal should provide owner credit
- **Components Potentially Eliminated**:
  - Splitter enclosure and hardware
  - Associated mounting/support
  - Possible simplification of metering/CT configuration

**Additional Costs:**
- Two (2) Type F dock light fixtures
- One (1) 15A-1P circuit breaker for Panel 2L
- Fixture Type N vs Type LA (may be cost neutral or credit)
- One (1) weatherproof emergency remote head
- Associated wiring and installation labor

**Net Impact**: Likely credit to owner, pending detailed pricing

### Construction Schedule Impact

**PCN Notes**:
- "No work is to be done before this matter is finalized and a Change Order is issued"
- Contractor to submit signed letter with price and schedule impact

**Potential Delays**:
- Service entrance revision may affect underground rough-in if already started
- Dock lighting addition appears straightforward
- Emergency lighting addition minor impact

### Design Revisions History

**Drawing E0.1 Revision History:**
- **Rev 1**: Original issue 2025.03.25
- **Rev 2**: PCN-01, 2025.04.04
- **Rev 3**: PCN-02, 2025.04.23 (Current revision)

**Indicates**: Active design development with multiple revisions during construction phase

### Equipment Procurement Considerations

**Long-Lead Items:**
- Main switchgear MD-1 (1600A)
- Transformers X1 and X2 (450 kVA each)
- Sub-distribution panels SD-1 and SD-2 (1200A each)
- Generator (22 kW, by refrigeration contractor)

**Impact of Changes:**
- Verify splitter removal doesn't affect switchgear procurement/delivery
- Dock lights and emergency head likely short-lead stock items

### Quality Control Items

**Field Verification Required:**
- Lamacoid labels on choked transformers (critical for inspection approval)
- Working clearances in Compressor Room 300
- Underground service routing and depth
- Roof penetration waterproofing for all conduits
- Panel circuit directory accuracy (extensive panel schedules)

**Testing Requirements:**
- Switchgear acceptance testing
- Ground fault protection functionality
- Emergency generator and ATS operation
- TVSS device verification
- Lighting levels (photometric testing recommended for type changes)

### Sustainability/Energy Considerations

**Energy Efficiency:**
- LED lighting assumed (Type designations suggest modern fixtures)
- VFD capability on HVAC equipment (typical for modern RTUs)
- High-efficiency transformers (dry-type specified)

**Future Expansion:**
- Multiple SPACE designations in panel schedules indicate growth capacity
- Panel H has specific spaces reserved: 2x(60A-3P), 2x(100A-3P)
- Panels SD-1 and SD-2 have spare capacity

---

## 7. SUMMARY OF KEY FINDINGS

### Critical Items Requiring Immediate Attention

1. **Service Entrance Splitter Removal** - Verify no impact to installed work; process owner credit
2. **Panel 2L Circuit Capacity** - Confirm availability for new 15A-1P dock light circuit
3. **Transformer Labeling** - Ensure choke labels specified and installed on TX-X1 and TX-X2
4. **Emergency Lighting Code Compliance** - New exterior head addresses egress code requirement
5. **Working Clearances** - Verify Compressor Room 300 layout with multiple panels

### Documentation Completeness

**Provided in PCN:**
- ✓ Single line diagram (E0.1)
- ✓ Panel schedules (E0.2, E0.3)
- ✓ Floor plan/lighting (E1.0)
- ✓ Life safety plan (E3.0)
- ✓ Luminaire schedule with new Type F fixture

**Not Included (may be in separate documents):**
- Lighting fixture specifications/cut sheets
- Generator specifications
- Emergency power riser diagram
- Fire alarm coordination
- Photometric calculations

### Coordination Requirements

**Immediate:**
- Contractor pricing and schedule impact submission
- SaskPower utility transformer location confirmation
- SaskTel communication requirements finalization

**Prior to Rough-In:**
- Roof equipment final locations (RTUs, generator)
- Structural shaft sizing confirmation
- Electrical room equipment layout approval

**Prior to Trim-Out:**
- Fixture type substitutions approved
- Panel circuit directories finalized
- Emergency lighting final locations verified

---

## 8. RECOMMENDED ACTIONS

### For Electrical Contractor

1. Verify service entrance work status before crediting splitter
2. Confirm Panel 2L has physical space and ampacity for additional circuit
3. Order Type F dock light fixtures (quantity 2)
4. Order weatherproof emergency remote head (quantity 1)
5. Review Staff Lounge fixture change for installation impact
6. Coordinate transformer choke labels with equipment supplier
7. Submit formal pricing and schedule impact per PCN requirements

### For Design Team

1. Issue formal Change Order upon pricing approval
2. Verify photometric impact of fixture type changes
3. Confirm emergency lighting coverage calculations with new exterior head
4. Review panel loading with added dock light circuit
5. Update project specifications to reflect PCN changes

### For Project Management

1. Process contractor pricing submission
2. Obtain owner approval for net cost impact
3. Update construction schedule per contractor input
4. Distribute approved Change Order to all stakeholders
5. Track PCN incorporation in as-built documentation

---

**Analysis Completed**: 2026-01-09
**Analyzed By**: AI Analysis System
**Source Documents**: PCN# 010 - Electrical Revisions.pdf (7 pages) and associated rendered images
