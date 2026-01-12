# PCN# 009 R1 - Seating Area Lights - Technical Data

**Document**: PCN# 009 R1 - Seating Area Lights
**Project**: Aurora Food Store, 2000 Anaquod Road, Regina, SK
**Commission No.**: 2445
**Date**: April 30, 2025
**Analysis Generated**: 2026-01-09

---

## 1. VISUAL INTERPRETATION

### Page 1 - Cover Sheet (page001_img002.jpeg)
**Visual Elements**:
- Standard PCN cover page format
- Black text on white background
- No color coding present
- Professional letterhead with architect signature
- Distribution list clearly formatted

### Page 2 - Electrical Detail (page002_img002.jpeg)
**Visual Elements**:
- Seating area floor plan detail showing Room 101 "SEATING"
- **Red markup lines** indicating deleted fixtures (circled M1 symbols with red "X" marks)
- **Black fixtures** marked with (S) in circles indicating new Type S fixtures
- Circuit annotations showing "6L-9", "6L-22", "2L-2" connections
- Table and seating layout visible in grayscale
- Vestibule 100 and area 100B visible adjacent to seating area
- Clear spatial organization showing fixture placement relative to furniture

**Color Coding System**:
- **Red circles with "M" inside and red "X"** = Deleted Type M1 fixtures (6 total)
- **Black circles with "(S)" or "S"** = New Type S fixtures (5 total)
- **Circuit labels** in black text (e.g., "6L-9", "2L-2")

**Spatial Layout**:
- Seating area appears to be adjacent to vestibule entrance
- Fixtures distributed across seating zone
- Mix of deleted M1 fixtures (appears to be recessed/pot lights based on symbol)
- New Type S fixtures appear to be suspended pendant-style fixtures

### Page 3 - Panel Schedules (page003_rendered.png)
**Visual Elements**:
- Comprehensive electrical panel schedules
- Four main panels shown: PANEL '6L', PANEL '2A', PANEL '2L', PANEL 'SD-1'
- Black text on white background
- Tabular format with circuit numbers, breaker sizes, and descriptions
- **Highlighted circuit**: Circuit 7-8 on Panel 6L shows "LIGHTING - SEATING" at 15A

**Panel Layout Details**:
- Panel 6L: 347/600V-3PH-4W, 400A capacity
- Panel 2L: 200A-120/208V-3PH-4W
- Multiple SPACE positions available for future circuits
- Phase balancing indicators (A, B, C columns)

### Page 4 - Floor Plan E1.0 (page004_rendered.png)
**Visual Elements**:
- Full electrical lighting floor plan at 1/8" = 1'-0" scale
- Comprehensive store layout showing all departments
- **Seating Area 101** clearly marked in lower left quadrant
- Circuit annotations throughout
- Legend and drawing notes on left side
- Multiple lighting fixture types designated by symbols
- Room numbers for all spaces
- Lighting zone schedule table included

**Spatial Context**:
- Seating area positioned near main entrance/vestibule (Room 100)
- Adjacent to Service Desk (Room 103)
- Self Checkouts (Room 102) nearby
- Outdoor Seating (Room 103A) adjacent

---

## 2. EXTRACTED DIMENSIONS & SPECIFICATIONS

### Fixture Changes
- **Deleted**: Six (6) Type M1 fixtures
- **Added**: Five (5) Type S fixtures
- **Net change**: -1 fixture overall in seating area

### Electrical Specifications

#### New Circuiting Requirements:
- **Voltage**: 347/600V
- **Panel**: Panel 6L
- **Circuit Breaker**: 15A-1P (single pole)
- **Circuit Number**: 7-8 (based on panel schedule showing "LIGHTING - SEATING")
- **Control**: EMS Timeclock (per Lighting Zone Schedule, Zone 13)

#### Panel 6L Details:
- **Panel Type**: 347/600V-3PH-4W
- **Panel Rating**: 400A
- **Location**: Surface mounted in West Staff Corridor (per schedule notes)
- **Existing Seating Circuit**: Circuit 7-8, 15A breaker

#### Fixture Type Details (from context):
- **Type M1**: Appears to be recessed/pot light fixtures (based on circular symbol with "M")
- **Type S**: Suspended pendant-style fixtures (based on "(S)" designation and note D.1 reference)
  - Note F.3 states: "LIGHT FIXTURE TYPE 'S' TO BE SUSPENDED WITH AIRCRAFT CABLE FROM UNISTRUT SUPPORT BETWEEN JOISTS. TYPICAL."

### Room Identification:
- **Seating Area**: Room 101
- **Service Desk**: Room 103
- **Outdoor Seating**: Room 103A
- **Vestibule**: Room 100

### Drawing Scale:
- **Floor Plan E1.0**: 1/8" = 1'-0"
- **Detail views**: Various scales noted on specific details

---

## 3. CROSS-REFERENCES

### Referenced Drawings:
1. **Electrical Drawing E0.2 - Schedules**
   - Shows revised circuiting on electrical panels 6L and 2L
   - Panel schedule details and circuit assignments

2. **Electrical Drawing E1.0 - Lighting**
   - Shows revised lighting layout in 'Seating 103' (Note: Appears to reference Room 101 based on plan)
   - Full floor plan context for fixture locations

### Related Documents:
- **Electrical PCN #3** dated April 30, 2025 (3 pages) - This is the electrical engineering portion
- **PCN-02** dated 2025.04.23 (revision history)
- **PCN-03** dated 2025.04.24 (this current revision)
- **CLAR-01** dated 2025.04.23
- **PCN-01** dated 2025.04.04

### Lighting Zone Schedule Reference:
- **Zone 13**: SEATING
- **Lighting Circuit**: 2L-2
- **Control Scheme**: EMS TIMECLOCK
- Note: Discrepancy - panel schedule shows 6L-7/8 for seating, but zone schedule shows 2L-2

### General Notes Referenced:
- **Note D.1**: Track lighting suspension requirements
- **Note F.3**: Type S fixture suspension with aircraft cable and unistrut
- **Note E.1, E.2, E.3**: Various occupancy sensor and control requirements
- **Note G.1, G.2**: Additional lighting control notes
- **Note H, H.1**: Further installation requirements

---

## 4. IDENTIFIED CONFLICTS & COORDINATION ISSUES

### CONFLICT #1: Circuit Panel Discrepancy
**Issue**: Inconsistency between panel schedules and lighting zone schedule
- **Panel Schedule E0.2**: Shows circuits 6L-7 and 6L-8 for "LIGHTING - SEATING" on 347/600V Panel 6L
- **Lighting Zone Schedule (E1.0)**: Shows Zone 13 "SEATING" controlled by circuit "2L-2"
- **PCN Instruction**: States "Wire and connect new Type S fixtures for seating area to 347/600V panel 6L on a 15A-1P circuit breaker"

**Severity**: HIGH - Critical for proper installation
**Required Action**: Clarify which panel and circuit number is correct for seating area lighting

### CONFLICT #2: Room Number Reference
**Issue**: PCN text refers to "Seating 103" but floor plan shows seating as Room 101
- **PCN Page 2**: States "revised lighting layout in 'Seating 103'"
- **Floor Plan E1.0**: Clearly labels seating area as Room 101
- **Room 103**: Actually labeled as "SERVICE DESK" on floor plan

**Severity**: MEDIUM - Documentation error, not installation error
**Required Action**: Correct room number reference in PCN text

### CONFLICT #3: Multiple Circuit Annotations
**Issue**: Floor plan shows multiple circuit labels in seating area
- Visible circuits: 6L-9, 2L-2, 6L-22
- Unclear which circuit(s) the new Type S fixtures connect to
- May indicate different lighting types or zones within seating area

**Severity**: MEDIUM
**Required Action**: Verify exact circuit assignment for new Type S fixtures

### COORDINATION REQUIRED:

1. **Millwork/Furniture Coordination**
   - General Note 2: "ELECTRICAL CONTRACTOR TO COORDINATE, INSTALL AND WIRE ALL MILLWORK/FURNITURE LIGHTING FIXTURES SUPPLIED BY OTHERS"
   - Verify if Type S fixtures are part of furniture package

2. **Mounting Height Coordination**
   - General Note 4: "REFER TO ARCHITECTURAL DECOR LIGHTING AND REFLECTED CEILING PLAN FOR EXACT MOUNTING HEIGHTS"
   - Must coordinate with architect for Type S suspension heights

3. **Structural Coordination**
   - Note F.3 requires unistrut support between joists
   - Coordinate with structural drawings for joist locations and loading

4. **EMS Controls Coordination**
   - General Note 6: "COORDINATE THE PURCHASE AND INSTALLATION OF ALL LIGHTING CONTROL EQUIPMENT THROUGH MICRO THERMO WEST"
   - Zone 13 controlled by EMS timeclock
   - Must integrate new fixtures into existing control system

5. **Architectural Coordination**
   - Verify ceiling type and finish in seating area
   - Confirm Type S fixture aesthetic matches design intent
   - Coordinate with architectural reflected ceiling plan

---

## 5. CODE COMPLIANCE NOTES

### Electrical Code Requirements:

1. **Voltage Classification**
   - 347/600V system requires specific wire and device ratings
   - Must comply with CEC (Canadian Electrical Code) for high voltage lighting circuits
   - Proper insulation and spacing required

2. **Circuit Protection**
   - 15A breaker sizing appears appropriate for lighting circuit
   - Verify total fixture load does not exceed 80% of breaker rating (12A continuous load max)

3. **Grounding/Bonding**
   - All fixtures must be properly grounded
   - Aircraft cable suspension must maintain proper ground path
   - Panel 6L shows TVSS (Transient Voltage Surge Suppression) protection

4. **Control Requirements**
   - Lighting controls must comply with energy code requirements
   - EMS timeclock control satisfies automatic shutoff requirements
   - Consider occupancy sensor requirements for this space type

5. **Accessibility**
   - Suspended fixtures must maintain proper clearance heights
   - Controls must be accessible (mounting height, location)

6. **Fixture Ratings**
   - Type S fixtures must be rated for 347V operation
   - Verify aircraft cable and unistrut support rated for fixture weight

### Building Code Considerations:

1. **Illumination Levels**
   - Seating area must meet minimum illumination requirements
   - Verify 5 fixtures provide adequate light levels vs. previous 6 fixtures
   - May require photometric analysis

2. **Emergency Lighting**
   - Verify if emergency lighting required in seating area
   - Check if any deleted M1 fixtures were emergency units
   - Confirm Type S fixtures can accommodate emergency battery packs if required

3. **Fire Rating**
   - If ceiling is fire-rated, penetrations must maintain rating
   - Unistrut support through ceiling requires proper firestopping

---

## 6. FINANCIAL IMPLICATIONS

### Credit Items:
- **Six (6) Type M1 fixtures** - Credit to owner required
- PCN specifically states: "Provide credit for the deletion of six (6) Type M1 fixtures"
- Credit should include:
  - Fixture cost
  - Installation labor
  - Associated materials (conduit, wire, supports)

### Additional Costs:
- **Five (5) Type S fixtures** - New procurement
- Aircraft cable suspension hardware
- Unistrut support system between joists
- Modified circuiting/wiring as required
- Potential re-programming of EMS control system

### Net Change Estimate:
- One fewer fixture overall (6 deleted, 5 added)
- Type S fixtures likely different cost than Type M1
- Installation method more complex (suspended vs. recessed)
- **Contractor must submit**: Signed letter with price including cost breakdown and schedule impact

---

## 7. SCHEDULE IMPACT

Per PCN instructions:
- "No work is to be done before this matter is finalized and a 'Change Order' is issued"
- Contractor to submit change to construction schedule if any
- Coordination required with multiple trades (electrical, structural support, controls)
- EMS programming may require system downtime

---

## 8. DISTRIBUTION LIST

**Project Stakeholders**:
- Sobeys Inc. - Jeff Craig (jeff.craig@sobeys.com)
- Sobeys Inc. - Shanwen Hsu (shanwen.hsu@sobeys.com)
- Quorex Construction Services Ltd. - Chris Walbaum (c.walbaum@quorex.ca)
- Lavergne Draward & Associates Inc. - Charles Koop (ckoop@ldaeng.ca)
- CGM Engineering - Justin Albo (justin_albo@cgmeng.ca)
- CGM Engineering - Tony Mitousis (tony_mitousis@cgmeng.ca)
- CGM Engineering - Brendan Simpson (brendan_simpson@cgmeng.ca)

**Design Team**:
- Architect: Nejmark (Kevin Fawley, SAA MRAIC - Principal)
- Electrical Engineer: CGM Engineering Ltd. (Brendan Simpson, E.I.T.)
- Project No: 24258

---

## 9. TECHNICAL SPECIFICATIONS SUMMARY

### Type S Fixture Installation Requirements:

**Mounting System**:
- Suspended with aircraft cable
- Supported from unistrut between joists
- Coordinate joist locations with structural drawings

**Electrical Connection**:
- Panel: 6L (347/600V-3PH-4W)
- Breaker: 15A-1P
- Wire to suit 347V application
- Connection method per manufacturer requirements

**Control Integration**:
- Connect to EMS system
- Timeclock control (Zone 13)
- Coordinate programming with Micro Thermo West

**Installation Notes**:
- All suspended fixture accessories to match ceiling finish (General Note 1)
- Mounting hardware includes steel cables, EMT conduit, supported unistruts (General Note 3)
- Coordinate mounting heights with architectural RCP (General Note 4)

---

## 10. RECOMMENDED ACTIONS

### Immediate Actions Required:

1. **Clarification Request**:
   - Resolve circuit number discrepancy (6L-7/8 vs 2L-2)
   - Confirm correct room number (101 vs 103)
   - Request fixture cut sheets for Type S to verify specifications

2. **Coordination Meetings**:
   - Schedule meeting with architect to review mounting heights
   - Coordinate with Micro Thermo West for controls integration
   - Review structural support requirements with engineer

3. **Submittal Preparation**:
   - Prepare cost breakdown for deleted Type M1 fixtures (credit)
   - Prepare cost breakdown for new Type S fixtures
   - Assess schedule impact
   - Submit signed letter per PCN requirements

4. **Shop Drawings**:
   - Prepare detailed shop drawings showing:
     - Exact fixture locations
     - Suspension details
     - Circuit routing
     - Structural support details

### Pre-Installation Requirements:

1. Verify Type S fixtures are 347V rated
2. Confirm aircraft cable load capacity
3. Verify unistrut spacing and support
4. Coordinate with ceiling contractor for penetrations
5. Program EMS system for new fixture configuration
6. Conduct mockup if required by architect

---

## 11. NOTES & OBSERVATIONS

### General Observations:

1. **Design Intent**: Change from recessed M1 to suspended S fixtures suggests aesthetic upgrade or functional improvement in seating area

2. **Fixture Count Reduction**: Going from 6 to 5 fixtures may indicate:
   - Type S provides more light output
   - Better light distribution pattern
   - Cost savings on fixture count
   - Different spacing requirements

3. **High Voltage System**: Use of 347/600V system is common in commercial facilities for lighting, reduces conductor sizes

4. **Control Strategy**: EMS timeclock control appropriate for public seating area, allows automated scheduling

5. **Drawing Revisions**: This is PCN-03, indicating third major revision to lighting plan, suggests ongoing design refinement

### Document Quality:
- Clear markups on visual plans
- Comprehensive panel schedules provided
- Good cross-referencing between documents
- Some minor inconsistencies noted (room numbers, circuit labels)

---

## CONCLUSION

PCN# 009 R1 documents a straightforward lighting fixture substitution in the seating area with some coordination requirements. The primary technical concern is resolving the circuit panel discrepancy. Installation complexity is moderate due to suspended fixture mounting requirements. Financial impact includes credit for deleted fixtures offset by cost of new Type S fixtures and installation.

**Risk Level**: MEDIUM
**Complexity**: MODERATE
**Coordination Required**: HIGH

---

**Analysis Prepared By**: AI Assistant
**Date**: January 9, 2026
**Source Documents**: PCN# 009 R1 - Seating Area Lights.pdf (4 pages)
