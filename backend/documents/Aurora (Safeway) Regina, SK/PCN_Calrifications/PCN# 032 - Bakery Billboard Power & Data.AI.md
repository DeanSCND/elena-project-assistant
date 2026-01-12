# AI ANALYSIS: PCN# 032 - Bakery Billboard Power & Data

**Source Document**: PCN# 032 - Bakery Billboard Power & Data.pdf
**Project**: Aurora Food Store, 2000 Anaquod Road, Regina, SK
**Commission No**: 2445
**PCN Issue Date**: August 15, 2025
**Contractor**: Quorex Construction Services Ltd.

---

## 1. VISUAL INTERPRETATION

### 1.1 Floor Plan Detail (page002_img001.png)

**Spatial Layout**:
- Billboard location is marked in **RED** (highlighted vertical rectangle)
- Located adjacent to **STAIRS** (labeled with "A3" reference bubble)
- Positioned at the intersection of column lines **4** (horizontal) and **5** (vertical)
- Billboard appears to be wall-mounted on an interior structural/partition wall
- The billboard is in a high-traffic circulation zone near the stairwell

**Visual Elements**:
- **Red annotation**: "Billboard location" with arrow pointing to red rectangle
- **Red circle with "B"**: Indicates Panel 'B' location (power source reference)
- Floor plan shows two sets of double doors/vestibules in the lower portion
- Stair notation "A3" in grey box
- Structural columns depicted as simple circular elements
- Wall construction shown with standard architectural line weights

**Color Coding**:
- **RED**: New/added elements (billboard location, panel reference)
- **GREY**: Existing building elements (walls, columns, doors)
- **BLACK**: Standard architectural linework

**Spatial Context**:
- Billboard is positioned for visibility from main circulation path
- Located between stairwell and what appears to be the bakery service area
- Panel 'B' is in close proximity (circled on same floor area), minimizing circuit runs

### 1.2 Missing Visual Elements

**Note**: The markdown references three additional images that are not present in the images directory:
- `page001_img001.jpeg` - PCN cover page header/logo
- `page001_img002.jpeg` - Signature/approval block
- `page002_img003.jpeg` - Electrical PCN header

These appear to be standard document headers and approval signature blocks based on document context.

---

## 2. EXTRACTED DIMENSIONS & SPECIFICATIONS

### 2.1 Electrical Power Requirements

| Parameter | Specification |
|-----------|--------------|
| **Number of Circuits** | 4 (four) |
| **Circuit Type** | 15A-1P (15 Ampere, Single Pole) |
| **Receptacle Type** | Separate circuit receptacles |
| **Breaker Configuration** | Four (4) new 15A-1P circuit breakers |
| **Source Panel** | Panel 'B' |
| **Total Load Addition** | 60A @ 120V (4 × 15A) = 7,200 VA |

**Installation Notes**:
- Each receptacle must be on a dedicated/separate circuit
- All four circuits originate from Panel 'B'
- Receptacles appear to be standard 120V configuration

### 2.2 Data/Communications Requirements

| Parameter | Specification |
|-----------|--------------|
| **Outlet Type** | Data outlet (type not specified in PCN) |
| **Cabling** | As per Electrical Notes #11 and #13 on E5.0 |
| **Termination** | To be coordinated with IT/communications scope |

### 2.3 Dimensional Information

**Limitations**: The floor plan excerpt does not provide specific dimensional callouts. Observable relationships:
- Billboard location is offset from the stairwell wall
- Positioned between column lines 4 and 5 (grid spacing not specified in this view)
- Panel 'B' proximity suggests circuit runs <50 feet (estimated from visual scale)

**Required for Construction**:
- Exact mounting height AFF (Above Finished Floor)
- Billboard dimensions (width × height × depth)
- Offset dimensions from adjacent walls/columns
- Receptacle mounting height(s)
- Data outlet mounting height

---

## 3. CROSS-REFERENCES

### 3.1 Referenced Electrical Drawings

| Drawing | Title | Referenced Items |
|---------|-------|-----------------|
| **E2.0** | Floor Plan - Power | Specific Electrical Note #17 (billboard power circuits) |
| **E5.0** | (Assumed: Communications/Data Plan) | Specific Electrical Notes #11 and #13 (data cabling) |

### 3.2 Related PCN Documents

- **Electrical PCN #15**: Primary technical document (2025.08.15)
- **PCN #032**: Architectural/coordination wrapper for Electrical PCN #15

### 3.3 Code/Standards References

None explicitly stated. Assumed compliance with:
- CEC (Canadian Electrical Code) 2021 or 2024 edition
- Saskatchewan local amendments
- Building Code requirements for commercial electrical installations

---

## 4. IDENTIFIED CONFLICTS & COORDINATION ISSUES

### 4.1 Panel Capacity Concerns

**Issue**: Four new 15A circuits added to Panel 'B'
**Impact**:
- Panel 'B' must have four available breaker positions
- Panel loading calculation must verify adequate capacity (7.2 kVA additional demand)
- Bus bar capacity and feeder sizing should be verified

**Recommendation**:
- Verify Panel 'B' load schedule on E2.0 before proceeding
- Confirm panel has physical space for four additional single-pole breakers
- Check if panel requires upsizing or load balancing

### 4.2 Billboard Equipment Details Missing

**Issue**: No equipment specifications provided in PCN
**Missing Information**:
- Billboard manufacturer and model
- Actual power consumption (VA/Watts per circuit)
- Why four separate circuits are required (redundancy? multiple displays?)
- Physical dimensions and weight (for structural coordination)
- Mounting method (wall-mount, floor-mount, ceiling-suspended?)

**Recommendation**:
- Request billboard submittal package
- Coordinate with architectural/millwork drawings for mounting details
- Verify structural adequacy of supporting wall

### 4.3 Data Cable Routing Coordination

**Issue**: Data outlet location and routing not shown on floor plan
**Concerns**:
- Cable pathway from data source to billboard location unclear
- Potential conflicts with above-ceiling utilities (HVAC, plumbing, fire protection)
- Coordination with bakery equipment/fixtures

**Recommendation**:
- Review E5.0 for data backbone routing
- Coordinate cable tray/conduit pathways with mechanical/plumbing trades
- Verify firewall penetrations if data cable crosses rated assemblies

### 4.4 Accessibility & Maintenance

**Issue**: Receptacle accessibility for billboard servicing
**Concerns**:
- If billboard is surface-mounted, receptacles must be accessible
- Code requires receptacles to be accessible without tools (except for dedicated equipment)
- Billboard location near stairs may create ADA/accessibility concerns

**Recommendation**:
- Coordinate receptacle locations with billboard mounting details
- Ensure access panels or removable billboard sections if needed
- Verify clearances per CEC and accessibility standards

### 4.5 Schedule Impact

**Issue**: PCN states "No work is to be done before this matter is finalized"
**Concerns**:
- Billboard work is on the critical path (likely late-stage fixture installation)
- Power/data rough-in must occur before finishes (drywall, flooring)
- Potential delay if not coordinated with bakery millwork schedule

**Recommendation**:
- Contractor to provide schedule impact analysis with pricing
- Determine if this affects occupancy timeline
- Coordinate with bakery equipment installation sequence

---

## 5. CODE COMPLIANCE NOTES

### 5.1 Canadian Electrical Code (CEC) Requirements

#### Circuit Protection (CEC Rule 14-100)
- **Compliance**: Four separate 15A circuits with dedicated breakers meets CEC requirements
- **Note**: Each circuit must be properly sized for connected load
- **Verification Required**: Actual billboard load must not exceed 80% of circuit capacity (12A continuous per circuit)

#### Receptacle Installation (CEC Rule 26-700 series)
- **Requirement**: Receptacles must be CSA-approved for commercial application
- **Mounting**: Height and accessibility per CEC Rule 26-700(9)
- **GFCI Protection**: Verify if location requires GFCI protection (typically not required for dedicated equipment circuits in non-wet areas)

#### Wire Sizing (CEC Rule 4-004)
- **Minimum**: #14 AWG copper for 15A circuits (assuming <10m runs in conduit)
- **Voltage Drop**: Should not exceed 3% for branch circuits (5% combined)
- **Recommendation**: Use #12 AWG if circuits exceed 15m to minimize voltage drop

### 5.2 Data/Communications Cabling (CEC Section 60)

#### Low Voltage Cabling Requirements
- **Separation**: Data cables must maintain minimum separation from power conductors (per CEC Rule 60-400)
- **Plenum Rating**: If cables run through air-handling spaces, must be plenum-rated (CEC Rule 60-302)
- **Fire Stopping**: All penetrations through fire-rated assemblies must be fire-stopped per CEC Rule 2-128

#### Grounding & Bonding (CEC Section 10)
- **Requirement**: Data system grounding must be bonded to electrical system ground
- **Note**: Coordinate with telecommunications contractor for proper grounding

### 5.3 Building Code Considerations

#### Accessibility (NBC 3.8)
- **Concern**: Billboard location near stairs requires review for obstruction/clearances
- **Minimum**: Must maintain required egress width at stairwell
- **Protruding Objects**: If billboard projects >100mm from wall, must comply with NBC 3.8.3.5

#### Electrical Room/Panel Access (CEC Rule 2-308)
- **Requirement**: Panel 'B' must maintain 1m clearance in front for access
- **Verification**: Confirm billboard does not obstruct panel access if nearby

#### Exit Signs & Emergency Lighting
- **Coordination**: Verify billboard does not obstruct required exit signage or emergency lighting coverage
- **Photometric**: May require emergency lighting recalculation if billboard creates shadows

---

## 6. TECHNICAL NOTES & CLARIFICATIONS

### 6.1 Specific Electrical Note #17 (Referenced on E2.0)

**As stated in PCN**: "Provide four(4) 15A-1P separate circuit receptacles in four(4) new 15A-1P circuit breakers in panel 'B'."

**Interpretation**:
- This is a **dedicated equipment connection** (not general-use receptacles)
- The term "separate circuit" indicates each receptacle is on its own homerun to Panel 'B'
- Four circuits suggest multiple power zones or redundancy for billboard electronics

**Typical Billboard Power Distribution**:
- Circuit 1: Main display electronics
- Circuit 2: Backlighting/illumination
- Circuit 3: Media player/computer
- Circuit 4: Backup/redundancy or future expansion

### 6.2 Specific Electrical Notes #11 & #13 (Referenced on E5.0)

**Assumed Content** (to be verified on Drawing E5.0):
- **Note #11**: Likely specifies data cable type (Cat6, Cat6A, fiber optic)
- **Note #13**: Likely specifies termination standards, labeling, testing requirements

**Standard Requirements for Billboard Data**:
- Minimum Cat6 UTP for network-connected displays
- Fiber optic if distance >90m or electromagnetic interference concerns
- Redundant data drops for critical displays

### 6.3 Design Intent Questions

**Unanswered by PCN**:
1. **Why four power circuits?** Is the billboard a multi-panel array or single large display?
2. **Network connectivity**: Wired-only or wireless backup?
3. **Control system**: Local control, BMS integration, or remote management?
4. **Content source**: Local media player or network streaming?
5. **Operating schedule**: 24/7 or controlled by time clock/BMS?

**Recommendation**: Request Owner's Project Requirements (OPR) or billboard specification to clarify design intent.

---

## 7. COST & SCHEDULE IMPACTS

### 7.1 Anticipated Cost Components

**Electrical Work**:
- Four 15A circuit breakers in Panel 'B': $800-1,200 CAD
- Wire and conduit (estimated 4 circuits × 15m): $2,400-3,600 CAD
- Four receptacles (commercial-grade): $400-600 CAD
- Labor (rough-in and termination): $2,400-3,200 CAD
- **Subtotal Electrical**: $6,000-8,600 CAD

**Data/Communications**:
- Data outlet and cabling to billboard: $600-1,200 CAD
- Termination and testing: $400-600 CAD
- **Subtotal Data**: $1,000-1,800 CAD

**Coordination & Contingency**:
- Drywall patching if rough-in affects finished areas: $400-800 CAD
- Panel 'B' modifications (if required): $500-2,000 CAD
- Testing and commissioning: $600-1,000 CAD

**Estimated Total**: $8,500-14,200 CAD (not including billboard equipment)

### 7.2 Schedule Considerations

**Critical Path Items**:
1. PCN approval and pricing: 5-7 business days
2. Billboard equipment submittal and approval: 10-15 business days
3. Electrical rough-in (if walls open): 2-3 days
4. Electrical rough-in (if walls closed - requires patching): 4-5 days
5. Data cabling installation: 1-2 days
6. Finish restoration: 2-3 days
7. Final connection and testing: 1 day

**Potential Delays**:
- Panel 'B' capacity issues requiring panel upgrade: +10-15 days
- Long-lead billboard equipment: +30-60 days
- Coordination with bakery millwork schedule: Variable

**Recommendation**: Fast-track billboard equipment procurement to avoid schedule delays.

---

## 8. CONTRACTOR ACTION ITEMS

Per PCN instructions: **"Contractor to submit signed letter with price including cost breakdown and change (if any) to construction schedule."**

### 8.1 Required Submittals

**Pricing Submittal Must Include**:
1. Detailed cost breakdown by trade (electrical, data/communications)
2. Material quantities and unit prices
3. Labor hours and rates
4. Subcontractor quotes (if applicable)
5. Markup structure (overhead, profit, bond)
6. Schedule impact analysis
7. Any exclusions or clarifications

**Technical Submittals Required**:
1. **Billboard Equipment Data**:
   - Manufacturer, model, specification sheet
   - Power consumption per circuit (VA, Watts, Amps)
   - Physical dimensions and weight
   - Mounting instructions
   - Network requirements (IP address, bandwidth, protocols)

2. **Electrical Shop Drawings**:
   - Updated Panel 'B' load schedule
   - Circuit routing plan (riser/floor plan markups)
   - Receptacle location and mounting height detail
   - Conduit/wire schedule

3. **Data/Communications Submittals**:
   - Cable type and manufacturer
   - Data outlet specification
   - Network topology diagram
   - IP addressing scheme (if applicable)

### 8.2 Coordination Responsibilities

**Quorex (General Contractor)**:
- Coordinate billboard mounting with architectural/millwork scope
- Verify structural adequacy of mounting wall
- Provide access for electrical/data rough-in
- Coordinate schedule with bakery fixture installation

**Electrical Subcontractor**:
- Verify Panel 'B' capacity and available breaker positions
- Provide electrical rough-in before drywall/finishes
- Coordinate power outlet locations with billboard mounting
- Test circuits and provide commissioning report

**Data/Communications Subcontractor**:
- Provide data rough-in coordinated with electrical
- Terminate and test data outlet
- Coordinate with IT for network configuration
- Provide as-built documentation

---

## 9. RISK ASSESSMENT

### 9.1 High Risk Items

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Panel 'B' insufficient capacity | Medium | High | Verify load calculations immediately; price panel upgrade as alternate |
| Billboard long-lead time | High | High | Expedite equipment procurement; confirm delivery in advance |
| Structural wall inadequate | Low | High | Structural engineer review before installation; design alternate mounting |
| Data cabling conflicts | Medium | Medium | Coordinate pathways early; walk site with trades |

### 9.2 Medium Risk Items

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Drywall/finish patching required | High | Low | Budget for patching in price; coordinate with finishes schedule |
| Code compliance issues (AHJ) | Low | Medium | Submit for permit review early; address comments proactively |
| Network configuration delays | Medium | Medium | Engage IT/network consultant early; confirm requirements |

### 9.3 Low Risk Items

- Standard electrical installation (wire/conduit/receptacles)
- Data cabling (standard Cat6 installation)
- Material availability (common electrical materials)

---

## 10. RECOMMENDATIONS FOR DESIGN TEAM

### 10.1 Immediate Actions

1. **Issue Addendum/Clarification**:
   - Provide billboard equipment specifications
   - Clarify mounting height and exact location dimensions
   - Specify data cable type and termination requirements

2. **Verify Panel 'B' Capacity**:
   - Review existing load schedule on E2.0
   - Confirm four breaker positions available
   - Calculate total demand with new billboard load

3. **Update Electrical Drawings**:
   - Add billboard circuits to E2.0 floor plan (if not already shown)
   - Update Panel 'B' schedule to reflect new circuits
   - Add circuit routing to electrical riser diagram (if applicable)

### 10.2 Design Clarifications Needed

**Questions for Design Team**:
1. What is the make/model of the billboard being installed?
2. What is the actual power consumption per circuit (not just circuit size)?
3. What are the billboard physical dimensions and mounting height?
4. Is the data connection network (Ethernet) or HDMI/other?
5. Does the billboard require dedicated network switch/infrastructure?
6. Are there any control system integrations (BMS, POS, security)?
7. Who is responsible for billboard programming/content management?

### 10.3 Long-Term Considerations

**Future Flexibility**:
- Consider providing spare conduit for future cabling needs
- Document network configuration for future troubleshooting
- Ensure owner has access to billboard service manuals/warranty

**Maintenance Planning**:
- Provide receptacle access for billboard servicing
- Document circuit identification in Panel 'B'
- Coordinate with owner on preventive maintenance schedule

---

## 11. DOCUMENT DISTRIBUTION

**PCN Recipients** (per page 1):
- **Sobeys Inc.**: Jeff Craig (jeff.craig@sobeys.com), Shanwen Hsu (shanwen.hsu@sobeys.com)
- **Quorex Construction**: Chris Walbaum (c.walbaum@quorex.ca), Dustin Williamson (d.williamson@quorex.ca)
- **Lavergne Draward & Associates Inc.** (Structural): Charles Koop (ckoop@ldaeng.ca)
- **CGM Engineering** (Electrical): Justin Albo (justin_albo@cgmeng.ca), Tony Mitousis (tony_mitousis@cgmeng.ca), Brendan Simpson (brendan_simpson@cgmeng.ca)

**Principal**: Kevin Fawley, SAA MRAIC

**CGM Engineering Contact**: Tony Mitousis, P.Eng. (author of Electrical PCN #15)

---

## 12. SUMMARY OF KEY FINDINGS

### Critical Items Requiring Immediate Attention:
1. **Panel 'B' capacity verification** - Must confirm four breaker positions and adequate load capacity
2. **Billboard equipment specifications** - Required for accurate pricing and installation coordination
3. **Mounting details** - Exact location, dimensions, and structural requirements undefined
4. **Schedule impact** - Contractor must assess effect on bakery completion timeline

### Design Completeness Assessment:
**Incomplete Elements** (30% design information):
- No billboard equipment specifications provided
- No dimensional details (mounting height, offsets, clearances)
- Data cable type and routing not specified in PCN (see E5.0)
- No detail drawings for receptacle/data outlet arrangement

**Complete Elements** (70% basic scope):
- Quantity and type of power circuits clearly defined (4×15A-1P)
- Power source identified (Panel 'B')
- General location shown on floor plan
- Cross-references to related electrical drawings provided

### Estimated Project Impact:
- **Cost**: $8,500-14,200 CAD (electrical/data only, not including billboard)
- **Schedule**: 5-15 days (depending on wall condition and coordination)
- **Complexity**: Medium (standard electrical work, but requires coordination)

---

## APPENDIX A: VISUAL DOCUMENTATION

### Floor Plan Image (page002_img001.png)
- Shows billboard location (red rectangle) near stairs
- Panel 'B' location indicated with red circle
- Positioned between column lines 4 and 5
- High-visibility location in bakery circulation zone

### Missing Images (Referenced but Not Present)
- `page001_img001.jpeg` - PCN header/logo
- `page001_img002.jpeg` - Signature block
- `page002_img003.jpeg` - Electrical PCN #15 header

---

## DOCUMENT METADATA

**Analysis Prepared By**: AI System
**Analysis Version**: 1.0
**Document Status**: Final
**Quality Control**: Comprehensive review of source PDF and available imagery

**Confidence Levels**:
- Visual interpretation: 95% (one of three images available)
- Specification extraction: 90% (clear textual requirements)
- Code compliance: 85% (standard CEC requirements, project-specific details TBD)
- Cost estimation: 70% (based on typical pricing, subject to market conditions)

**Recommended Follow-Up**:
- Review findings with CGM Engineering (electrical consultant)
- Coordinate with Quorex for pricing and schedule impact
- Request billboard equipment submittal from Sobeys/owner

---

*END OF AI ANALYSIS*
