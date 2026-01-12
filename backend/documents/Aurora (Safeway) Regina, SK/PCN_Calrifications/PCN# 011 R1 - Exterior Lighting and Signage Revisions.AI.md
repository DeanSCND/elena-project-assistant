# PCN# 011 R1 - Exterior Lighting and Signage Revisions - Technical Data

**Document**: PCN# 011 R1 - Exterior Lighting and Signage Revisions
**Project**: Aurora Grocery Store, 2000 Anaquod Road, Regina, SK
**Commission No**: 2445
**Date**: May 2, 2025
**Pages**: 7 (including cover)

---

## 1. VISUAL INTERPRETATION

### Color Coding System (Page 2 - Site Plan)
The color-coded site plan (page002_img001.jpeg) shows:

- **RED markers**: Modified locations of six (6) existing exterior light fixtures - repositioned to optimize coverage
- **PINK markers**: Twenty (20) additional exterior light fixtures distributed around building perimeter
- **GREEN markers**: Modified power locations for existing exterior signage - relocated to accommodate design changes
- **BLUE markers**: Four (4) new exterior signs requiring electrical power - added for wayfinding and identification
- **Annotations**: Handwritten note states "QUOREX TO COORDINATE EXACT CONDUIT QUANTITIES AND LOCATIONS FOR SIGNAGE POWER WITH INTERNATIONAL NEON"

### Spatial Layout Observations
The site plan shows:
- Building with parking lot layout and circulation patterns
- Exterior lighting concentrated at:
  - Building entrances (increased density)
  - Parking lot perimeter
  - Pedestrian walkways
  - Service/loading areas
- Signage locations at:
  - Main building facades
  - Corner/gateway positions
  - Parking lot identification points

### Diagrams and Details
- **Page 4**: Electrical panel schedule E0.2 showing circuit breaker configurations
- **Page 5**: Continuation of panel schedules E0.3
- **Page 6**: Floor plan E1.0 showing interior lighting zones (reference for exterior circuit loading)
- **Page 7**: Power plan E2.0 showing electrical distribution and signage power locations

---

## 2. EXTRACTED DIMENSIONS & SPECIFICATIONS

### 2.1 Exterior Lighting Fixtures

#### Type X1 - Exterior Wall Sconce
- **Quantity**: 4 additional units
- **Mounting**: Wall mounted
- **Manufacturer**: Eclipse Lighting
- **Model**: BSC-TI-XL1-UP10-DN10-4K-80CRI-UNV-PNA-CTB-BBX1
- **Voltage**: 347V
- **Wattage**: 16W per fixture
- **Total Load**: 64W (4 fixtures)
- **Color Temperature**: 4000K
- **CRI**: 80
- **Light Distribution**: Bi-directional (UP10-DN10)
- **Finish**: Powder coated (PNA = Pewter Anthracite)

#### Type X2 - Exterior Downlight
- **Quantity**: 16 additional units
- **Mounting**: Wall mounted
- **Manufacturer**: Keene by Signify
- **Model**: LPW3270NW-G3-3-347MGY
- **Voltage**: 347V
- **Wattage**: 70W per fixture
- **Total Load**: 1,120W (16 fixtures)
- **Color**: Medium Gray (MGY)
- **Application**: Downlighting for building perimeter and entries

### 2.2 Total Added Lighting Load
- Type X1: 4 fixtures × 16W = **64W**
- Type X2: 16 fixtures × 70W = **1,120W**
- **Combined Total**: **1,184W** (approximately 10 amps @ 120V)

### 2.3 Electrical Panel Modifications

#### Panel 2A - Four New Circuits Added
- **Panel Rating**: 200A, 120/208V, 3-Phase, 4-Wire
- **Location**: Surface mounted in Compressor Room 300
- **New Circuits**:
  - Circuit 29-30: 15A-1P for Exterior Signage
  - Circuit 31-32: 15A-1P for Exterior Signage
  - Circuit 33-34: 15A-1P for Exterior Signage
  - Circuit 35-36: 15A-1P for Exterior Signage
- **Wire Size**: #12 AWG
- **Load per Circuit**: Approximately 1,800W @ 120V capacity

#### Panel C1 - One Circuit Modified
- **Panel Rating**: 100A, 120/208V, 3-Phase, 4-Wire
- **Circuit Modification**: One 15A-1P circuit noted as **SPARE**
- **Financial Impact**: Provide **credit** for associated wiring and conduit (cost reduction)

#### Panel C2 - One New Circuit Added
- **Panel Rating**: 200A, 120/208V, 3-Phase, 4-Wire
- **New Circuit**: One 15A-1P circuit breaker
- **Purpose**: Exterior signage power
- **Wire Size**: #12 AWG (typical for 15A circuits)

#### Panel 2L - Exterior Lighting Circuit
- **Circuit 23-24**: 15A-1P for Lighting - Exterior (existing)
- **Note**: Additional Type X1 and X2 fixtures to be "wired and connected to exterior lighting circuit as required"
- **Load Verification Required**: Confirm circuit capacity adequate for additional 1,184W load

### 2.4 Signage Power Requirements
- **Total New Signage**: 4 exterior signs requiring electrical power
- **Power Specs**: Not explicitly detailed (coordinate with International Neon)
- **Circuit Protection**: Four 15A-1P circuits in Panel 2A (one per sign assumed)
- **Voltage**: Likely 120V (standard for signage)

---

## 3. CROSS-REFERENCES

### Referenced Drawings
1. **Electrical Drawing E1.0** - Floor Plan - Lighting
   - Shows additional Type X1 and X2 fixture locations
   - Dated May 1, 2025

2. **Electrical Drawing E0.2** - Schedules (Page 4)
   - Panel schedules showing circuit breaker additions to Panel 2A
   - Updated circuitry for revised signage

3. **Electrical Drawing E0.3** - Schedules (Page 5)
   - Continuation of panel schedules
   - Shows Panel C1 spare circuit and Panel C2 additions

4. **Electrical Drawing E2.0** - Floor Plan - Power (Pages 6-7)
   - Revised locations of exterior signage power
   - Shows four new exterior signs requiring power
   - Power distribution routing

### Related Documents
- **Electrical PCN #4R1** - Dated May 1, 2025 (5 pages)
  - Parent document providing technical details
  - Prepared by CGM Engineering

### Coordination Requirements
- **Contractor**: Quorex Construction Services Ltd.
- **Signage Contractor**: International Neon
- **Coordination Item**: Exact conduit quantities and locations for exterior signage power (PCN Section 1.0.2)

### Distribution List
- Sobeys Inc. (Jeff Craig, Shanwen Hsu)
- Quorex Construction Services Ltd. (Chris Walbaum)
- Lavergne Draward & Associates Inc. (Charles Koop)
- CGM Engineering (Justin Albo, Tony Mitousis, Brendan Simpson)

---

## 4. IDENTIFIED CONFLICTS & COORDINATION ISSUES

### 4.1 Potential Circuit Overload - Panel 2L
**Concern**: The additional 1,184W of exterior lighting (Type X1 and X2 fixtures) is to be "wired and connected to exterior lighting circuit as required."

**Existing Circuit**: Panel 2L, Circuit 23-24, 15A-1P
**Circuit Capacity**: 15A × 120V = 1,800W maximum
**Issue**: Document does not specify current load on exterior lighting circuit. If existing load approaches capacity, adding 1,184W could exceed 80% continuous load threshold (1,440W).

**Resolution Required**:
- Verify existing load on Panel 2L Circuit 23-24
- If capacity insufficient, add dedicated circuit(s) for new fixtures
- Consider load balancing across phases

### 4.2 Signage Power Conduit Coordination
**Concern**: PCN states "Quorex to coordinate exact conduit quantities and locations for exterior signage power with signage contractor (International Neon)" but provides limited specifics.

**Missing Information**:
- Signage electrical load per unit
- Exact conduit routing and sizes
- Pull box locations
- Disconnect switch requirements
- Signage controller/transformer specifications

**Resolution Required**:
- Obtain signage shop drawings from International Neon before rough-in
- Confirm four 15A circuits in Panel 2A are adequate
- Verify voltage requirements (120V assumed)
- Coordinate with Authority Having Jurisdiction (AHJ) for signage code compliance

### 4.3 Modified Fixture Locations - Field Verification
**Concern**: Six exterior fixtures are being relocated (red markers on plan).

**Coordination Items**:
- Verify existing conduit can be reused or requires modification
- Confirm structural support adequate at new mounting locations
- Check for conflicts with architectural finishes, glazing, or building systems
- Ensure relocated fixtures maintain required illumination levels

**Resolution Required**:
- Field verify existing conduit locations before demolition
- Coordinate with architect for fixture mounting details
- Update photometric analysis if required by code

### 4.4 Panel 2A Space Availability
**Concern**: Four new 15A-1P circuit breakers added to Panel 2A.

**Verification Required**:
- Confirm Panel 2A has four available breaker spaces (circuits 29-36 shown as added)
- Verify panel does not exceed nameplate rating with additional loads
- Check if panel requires feeder upgrade

**Panel 2A Existing Data**:
- Rating: 200A, 120/208V, 3-Phase
- Location: Compressor Room 300
- Many circuits already allocated (schedule shows extensive use)

### 4.5 Credit for Panel C1 Spare Circuit
**Financial Item**: One 15A-1P circuit on Panel C1 noted as spare - credit for wiring and conduit.

**Coordination Required**:
- Verify which circuit is designated spare (not specified in PCN)
- Confirm wiring/conduit not yet installed (eligible for credit)
- Document credit amount in Change Order pricing
- Ensure circuit breaker space remains available for future use

### 4.6 Mounting Height and Code Compliance
**Concern**: Exterior lighting fixture mounting heights not specified.

**Code Considerations**:
- Minimum illumination levels per local code
- Uniformity ratios for parking lot and walkways
- Dark sky compliance (if applicable)
- Energy code compliance (lighting power density)

**Resolution Required**:
- Specify mounting heights for Type X1 and X2 fixtures
- Confirm photometric compliance
- Verify no light trespass onto adjacent properties

---

## 5. CODE COMPLIANCE NOTES

### 5.1 Canadian Electrical Code (CEC) Requirements

#### Circuit Protection
- **Section 8-104**: Circuit breaker sizing adequate - 15A-1P for #12 AWG wire complies
- **Section 8-108**: Continuous loads (outdoor lighting) must not exceed 80% of circuit rating
  - 15A circuit × 80% = **12A maximum continuous**
  - 120V × 12A = **1,440W maximum per circuit**
  - Verify exterior lighting load calculation includes diversity factor

#### Wire Sizing
- **#12 AWG copper**: Rated 15A maximum per CEC Table 2
- Appropriate for 15A-1P circuit breakers
- Verify ambient temperature correction factors (outdoor conduit)
- Consider voltage drop over long runs to exterior fixtures

#### Grounding and Bonding
- **Section 10**: All exterior fixtures and signage must be properly grounded
- Metal conduit must provide continuous ground path
- Disconnect switches for signage must include ground

### 5.2 Building Code Compliance

#### Exterior Lighting Levels
- **NBC 2020**: Minimum illumination for:
  - Building exits: 50 lux
  - Parking areas: 10-20 lux
  - Pedestrian walkways: 20 lux
- **Verify**: Photometric analysis confirms compliance with added/relocated fixtures

#### Emergency Lighting
- Confirm if any exterior fixtures serve as emergency egress lighting
- If so, must be on emergency circuit or battery backup

### 5.3 Energy Code Compliance

#### Lighting Power Density (LPD)
- **NECB 2020 / ASHRAE 90.1**: Exterior lighting power allowances
  - Parking areas: 0.15 W/ft² (facade lighting separate)
  - Building entrances: 20W per linear foot of door width
  - Added load: 1,184W - verify does not exceed allowable LPD

#### Automatic Controls Required
- **Photocell control**: Exterior lighting must automatically shut off during daylight
- **Time clock**: Additional control for operating hours
- **Verify**: Control system accommodates additional fixtures

### 5.4 Signage Code Requirements

#### Electrical Signage Standards
- **CSA C22.2 No. 236**: Outdoor electrical signs
- Disconnect switch required within sight of each sign
- GFCI protection may be required depending on signage type
- Grounding per CEC Section 10

#### Sign Permits
- **Municipal Requirements**: Verify signage permits obtained
- Electrical inspection required before energizing
- Authority Having Jurisdiction (AHJ) approval noted on cover page

### 5.5 Installation Standards

#### Weatherproofing
- All exterior fixtures and connections must be rated for outdoor use
- IP rating: Minimum IP65 recommended for Saskatchewan climate
- Conduit seals required where entering building
- Expansion fittings for long conduit runs (temperature extremes)

#### Mounting
- Type X1 (wall sconce): Verify backing/blocking for secure mounting
- Type X2 (downlight): Confirm wall construction adequate for fastening
- Vibration isolation if near mechanical equipment

---

## 6. TECHNICAL SPECIFICATIONS SUMMARY

### Fixture Performance Data

| Fixture Type | Qty | Voltage | Wattage | Lumens | CCT | CRI | Application |
|--------------|-----|---------|---------|---------|-----|-----|-------------|
| Type X1 (Eclipse) | 4 | 347V | 16W | TBD | 4000K | 80 | Wall sconce, bi-directional |
| Type X2 (Keene) | 16 | 347V | 70W | TBD | TBD | TBD | Wall downlight |

**Note**: Lumen output not specified in PCN - reference manufacturer cut sheets.

### Electrical Panel Load Summary

| Panel | Rating | Circuits Added | Circuits Modified | Load Impact |
|-------|--------|----------------|-------------------|-------------|
| 2A | 200A, 120/208V, 3φ | 4 × 15A-1P | None | +4 circuits (signage) |
| C1 | 100A, 120/208V, 3φ | None | 1 × 15A-1P spare | Credit (reduction) |
| C2 | 200A, 120/208V, 3φ | 1 × 15A-1P | None | +1 circuit (signage) |
| 2L | 200A, 120/208V, 3φ | None | Existing exterior lighting | +1,184W load |

### Wire and Conduit Requirements

**New Circuits**:
- **5 new circuits** total (4 in 2A, 1 in C2)
- **Wire**: #12 AWG copper
- **Conduit**: Size TBD based on conductor count and routing
- **Length**: TBD - field measure from panels to fixture/signage locations

**Coordination with Signage Contractor**:
- Conduit quantities and exact locations to be determined by Quorex in coordination with International Neon
- Provide conduit stubouts at signage locations before exterior finishes

---

## 7. COST IMPACT CONSIDERATIONS

### Additions (Cost Increase)
1. **Type X1 fixtures**: 4 units @ $[TBD] + installation
2. **Type X2 fixtures**: 16 units @ $[TBD] + installation
3. **Circuit breakers**: 5 × 15A-1P @ $[TBD]
4. **Wire and conduit**: #12 AWG + conduit for 5 new circuits + fixture feeds
5. **Signage power conduit**: 4 conduit runs to exterior signage locations
6. **Labor**:
   - Fixture installation and wiring
   - Conduit installation and terminations
   - Panel modifications
   - Testing and commissioning

### Deductions (Cost Decrease)
1. **Panel C1 spare circuit**: Credit for eliminated wiring and conduit (quantity TBD)

### Schedule Impact
- **Coordination delay risk**: Signage contractor (International Neon) must provide specifications before electrical rough-in
- **Recommendation**: Prioritize signage shop drawing submittal and approval
- **Critical path item**: Exterior lighting on schedule critical path for building occupancy

---

## 8. SUBMITTAL REQUIREMENTS

### Shop Drawings Required
1. **Exterior Lighting Fixtures**:
   - Type X1 and X2 fixture cut sheets
   - Photometric data (IES files)
   - Mounting details and templates
   - Finish samples

2. **Signage**:
   - International Neon signage drawings
   - Electrical load calculations per sign
   - Transformer/controller specifications
   - Conduit connection details

3. **Panel Modifications**:
   - Updated panel schedules (E0.2, E0.3)
   - Load calculations
   - Short circuit coordination study (if applicable)

### Coordination Drawings
- Site plan showing final exterior lighting locations (Type X1, X2, relocated fixtures)
- Power plan (E2.0) showing signage power routing and conduit paths
- Details showing fixture mounting at various wall conditions

### Documentation for Approval
- Authority Having Jurisdiction (AHJ) review and approval
- Contractor pricing proposal with cost breakdown
- Schedule impact analysis (if any)

---

## 9. CONSTRUCTION NOTES

### Sequencing
1. Coordinate signage conduit locations with International Neon **before** wall finishes
2. Install conduit stubouts and pull boxes for signage
3. Install exterior lighting conduit and junction boxes
4. Install circuit breakers in Panels 2A, C1, C2
5. Pull wire and terminate at panels
6. Install fixtures (after finishes complete)
7. Install signage (by others)
8. Connect signage to electrical power
9. Test and commission all exterior lighting and signage
10. Final inspection by AHJ

### Field Verification Required
- Existing exterior lighting circuit load (Panel 2L, Circuit 23-24)
- Available breaker spaces in Panel 2A
- Conduit routing paths clear of obstructions
- Structural backing at fixture mounting locations
- Voltage at panel bus (confirm 347V/120V as applicable)

### Testing and Commissioning
- Megger test all new circuits before energizing
- Verify proper operation of all fixtures
- Confirm photocell and time clock control functionality
- Test signage operation
- Record "as-built" fixture and signage locations
- Provide operation and maintenance manuals to owner

---

## 10. POTENTIAL RISKS AND MITIGATION

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|---------------------|
| Circuit overload on Panel 2L | High | Medium | Verify existing load, add circuit if needed |
| Signage conduit coordination delay | High | Medium | Expedite International Neon shop drawings |
| Panel 2A space unavailable | Medium | Low | Verify panel schedule, add subpanel if required |
| Fixture mounting conflicts | Medium | Medium | Field verify locations before ordering fixtures |
| Schedule delay - long lead items | Medium | Medium | Order fixtures immediately upon approval |
| Cost overrun - hidden conditions | Medium | Low | Include contingency in pricing |
| Code compliance issues | High | Low | Pre-review with AHJ, confirm photometric compliance |

---

## 11. RECOMMENDATIONS

### Immediate Actions
1. **Expedite Approvals**: Obtain signed Change Order to minimize schedule impact
2. **Signage Coordination Meeting**: Schedule meeting between Quorex, International Neon, and CGM Engineering to finalize conduit routing
3. **Load Calculation**: Electrical engineer to verify Panel 2L exterior lighting circuit has adequate capacity for 1,184W additional load
4. **Procurement**: Order Type X1 and X2 fixtures immediately (potential long lead time)

### Design Clarifications Needed
1. Confirm lumen output for Type X1 and X2 fixtures meets site lighting requirements
2. Specify mounting heights for all exterior fixtures
3. Provide signage electrical load per unit (coordinate with International Neon)
4. Identify specific Panel C1 circuit designated as spare for credit calculation
5. Confirm conduit sizes for signage power feeds

### Quality Control
1. Pre-installation meeting with electrical contractor to review PCN requirements
2. Field inspection of conduit rough-in before concrete/finishes
3. Witness testing of all new circuits
4. Photographic documentation of all modifications

---

## 12. APPENDIX - FIXTURE CATALOG DATA

### Type X1 - Eclipse Lighting Wall Sconce
- **Model**: BSC-TI-XL1-UP10-DN10-4K-80CRI-UNV-PNA-CTB-BBX1
- **Type**: LED wall sconce with bi-directional distribution
- **Optics**: 10° up-light, 10° down-light
- **Finish**: Pewter Anthracite (PNA) powder coat
- **Housing**: Cast bronze (CTB)
- **Electrical**: Universal voltage (UNV) - suitable for 347V
- **Application**: Architectural accent lighting, building entry features

### Type X2 - Keene by Signify Exterior Downlight
- **Model**: LPW3270NW-G3-3-347MGY
- **Type**: LED wall-mounted downlight
- **Series**: Keene (commercial/industrial grade)
- **Generation**: G3 (third generation)
- **Color**: Medium Gray (MGY)
- **Voltage**: 347V
- **Wattage**: 70W
- **Application**: General area lighting, building perimeter illumination

---

## DOCUMENT REVISION HISTORY

| Revision | Date | Description | By |
|----------|------|-------------|-----|
| R1 | 2025-05-02 | Initial PCN issue | CGM Engineering |
| - | 2025-05-01 | Electrical PCN #4R1 prepared | Brendan Simpson, E.I.T. |

**Original PDF Source**: PCN# 011 R1 - Exterior Lighting and Signage Revisions.pdf
**Extraction Date**: 2026-01-09 18:31:13
**AI Analysis Date**: 2026-01-09

---

*This AI-generated analysis is based on the information contained in the source PCN document and associated drawings. All specifications, dimensions, and recommendations should be verified against original construction documents and applicable codes. This analysis does not constitute engineering design or approval.*
