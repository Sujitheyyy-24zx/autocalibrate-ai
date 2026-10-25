from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak,
                                KeepTogether, CondPageBreak)
from PIL import Image as PILImage

OUT = "/home/claude/cad_r1b/out"
R0 = "/home/claude/cad/out"
PDF = f"{OUT}/AutoCalibrate_PT100_Node_R1_Mechanical_Design.pdf"
INK = colors.HexColor("#111111")
ACC = colors.HexColor("#1f3a5f")
GRID = colors.HexColor("#9aa3ad")
HEAD = colors.HexColor("#e8ecf1")

body = ParagraphStyle("b", fontName="Helvetica", fontSize=9.4, leading=12.6, textColor=INK, spaceAfter=4)
small = ParagraphStyle("s", parent=body, fontSize=8.0, leading=10.2, spaceAfter=2)
cell = ParagraphStyle("c", parent=body, fontSize=7.9, leading=9.8, spaceAfter=0)
cellb = ParagraphStyle("cb", parent=cell, fontName="Helvetica-Bold")
h1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=ACC, spaceBefore=8, spaceAfter=6)
h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=ACC, spaceBefore=8, spaceAfter=4)
cap = ParagraphStyle("cap", parent=small, textColor=colors.HexColor("#444444"), spaceAfter=8)
title = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=20, leading=25, textColor=ACC, spaceAfter=4)
flag = ParagraphStyle("f", parent=body, backColor=colors.HexColor("#fff4e5"), borderColor=colors.HexColor("#c2410c"),
                      borderWidth=0.8, borderPadding=6, spaceBefore=6, spaceAfter=10)

S = []
W_TXT = 174 * mm


def H1(t): S.append(Paragraph(t, h1))
def H2(t): S.append(Paragraph(t, h2))
def P(t, st=body): S.append(Paragraph(t, st))
def B(items, st=body):
    for i in items:
        S.append(Paragraph("&bull;&nbsp;" + i, ParagraphStyle("li", parent=st, leftIndent=10, firstLineIndent=-7)))


def IMG(path, w=W_TXT, caption=None, maxh=200 * mm):
    im = PILImage.open(path)
    h = w * im.height / im.width
    if h > maxh:
        w, h = maxh * im.width / im.height, maxh
    flow = [Image(path, width=w, height=h)]
    if caption:
        flow.append(Paragraph(caption, cap))
    S.append(KeepTogether(flow))


def TBL(rows, widths, head=True, fs=None):
    data = [[Paragraph(str(c), cellb if (head and i == 0) else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1 if head else 0, hAlign="LEFT")
    st = [("GRID", (0, 0), (-1, -1), 0.4, GRID), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
          ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]
    if head:
        st.append(("BACKGROUND", (0, 0), (-1, 0), HEAD))
    t.setStyle(TableStyle(st))
    S.append(t); S.append(Spacer(1, 6))


# ===================================================================== cover
P("AutoCalibrate AI", ParagraphStyle("k", parent=body, textColor=colors.HexColor("#c2410c"), fontName="Helvetica-Bold"))
P("PT100 Sensor Health Monitoring and Predictive Calibration Node", title)
P("Mechanical design package, revision R1 (developed from our R0 design <i>IP65_PT100_Enclosure.step</i>) - "
  "Vishwakarma Awards 2026-27, Stage 2. Preliminary, 25 October 2026.", body)
IMG(f"{OUT}/v_cutaway.png", w=150 * mm, caption="Figure 1. R1 half-section: ESP32 chamber (top), MAX31865 + terminal chamber "
    "(bottom), bulkhead and two O-rings between them, SS304 finned neck, 1/2\" NPT process thread and Class A PT100 probe.")
P("<b>Legend used throughout:</b> [Brief] = requirement stated in the project brief; [Template] = requirement stated in the "
  "Stage 2 template PDF; [Rec] = our engineering recommendation; [Assump] = assumption to be replaced by a measurement; "
  "[Illustrative] = simplified calculation, not a validated result.", small)
P("<b>Template status:</b> the Stage 2 Submission Template PDF was not attached and was not found in the shared Downloads "
  "folder, so no [Template] requirement has been extracted and the page references (CAD ~p.7, BOM ~p.9, safety ~p.13) are "
  "unverified. Section 1.1 lists exactly what must be checked against it; nothing in this package claims template compliance.", flag)

S.append(PageBreak())
# ===================================================================== 1 requirements
H1("1. Requirements basis")
H2("1.1 Template requirements (to be extracted)")
TBL([["Template area (as referenced in the brief)", "Status", "Where this package addresses it once verified"],
     ["CAD and design requirements (stated as ~page 7)", "Not extracted - PDF not provided", "Sections 2, 3, 7, 8 and drawings sheets 1-4"],
     ["Electronics and bill of materials (stated as ~page 9)", "Not extracted - PDF not provided", "Section 6 (BOM) and 4 (fit table)"],
     ["Safety requirements (stated as ~page 13)", "Not extracted - PDF not provided", "Section 13 (safety) and 12 (validation)"],
     ["Any other mechanical requirements", "Unknown", "Add rows here after reading the full template"]],
    [70, 45, 59])
H2("1.2 Brief requirements and where they are met")
TBL([["[Brief] requirement", "How R1 meets it"],
     ["House ESP32, MAX31865 and wiring", "ESP32-DevKitC on a D70 carrier in the upper chamber; MAX31865 breakout on a 30 x 30 sub-carrier in the lower chamber (Section 2)."],
     ["Convenient assembly and maintenance", "4 x M4 open the whole node; ESP32 stage unplugs via one JST-XH harness; boards are socketed or on M3 inserts."],
     ["Cable entry and strain relief", "2 x PG7 glands (one blanked spare) + printed cable-tie anchor on each gland axis + service loop."],
     ["No loose wires touching conductive surfaces", "All-insulating ASA housing; bulkhead separates field wiring from the ESP32; ferrules on all field cores; harness tied to anchors."],
     ["Mount on bench, test rig or machine", "Mode A: 1/2\" NPT into a process port. Mode B: Al bracket clamped by an NPT locknut, 4 x M5 slots (bench, rig, bath lid, machine plate)."],
     ["Separate heat-sensitive electronics from the measurement point", "60 mm SS304 finned neck: 65 mm from the process fitting to the housing base; electronics 70-120 mm above it (Section 10)."],
     ["College-level manufacturing", "FDM ASA (or PETG) printed housing; neck from standard 1/2\" SS304 pipe parts; laser- or hand-cut bracket."],
     ["Do not over-complicate", "R1 keeps R0's proven layout but drops the custom PCB and moulded PA66-GF30 in favour of dev boards and FDM."],
     ["No unsupported IP65 claim", "IP65 features are design intent only; Section 12 lists the IEC 60529 tests needed before any claim."],
     ["No fabricated FEA", "Section 9 gives the ANSYS set-up. Preliminary numbers shown are labelled hand calculations or our earlier open-source R0 neck check, to be repeated in ANSYS."]],
    [52, 122])
H2("1.3 What changed from R0 to R1")
TBL([["Item", "R0 (IP65_PT100_Enclosure.step)", "R1 (this package)", "Reason"],
     ["Electronics", "Custom 55 x 45 PCB with ESP32 module", "ESP32-DevKitC + MAX31865 breakout on carriers", "[Brief] off-the-shelf hardware"],
     ["Front-end location", "On the single PCB", "MAX31865 in lower chamber beside the RTD entry", "Short RTD leads; ESP32 heat and RF kept above the bulkhead"],
     ["Housing material", "PA66-GF30 (injection moulded)", "ASA by FDM (PETG option)", "[Brief] college manufacturing"],
     ["Gland position", "+/-20 deg", "+/-35 deg, inner spot-face, 5 mm local wall", "Clear of the anchors and terminal block; PG7 thread length is 8 mm"],
     ["Bolt / neck-screw clocking", "45 deg / 90 deg start", "0 deg / 30 deg start", "Keeps flange bosses clear of glands and screw heads clear of the terminal pedestal"],
     ["Neck screw holes", "D4.5 in neck flange", "M4 tapped (D3.3 drill)", "Screws thread into the SS304 flange from inside"],
     ["Strain relief", "Gland only", "Gland + anchor posts + service loop", "[Brief] strain relief"],
     ["Mounting", "1/2\" NPT only", "NPT + optional rig bracket", "[Brief] bench / test rig mounting"]],
    [26, 45, 52, 51])

S.append(PageBreak())
# ===================================================================== 2 summary
H1("2. Proposed design summary")
P("R1 keeps the R0 architecture: a cylindrical two-chamber housing (D88 body, D108 flanges) stacked on a 60 mm SS304 finned "
  "neck with a 1/2\"-14 NPT process thread, and a Class A PT100 in a 6 mm sheath passing up the neck bore. "
  "A 4 mm bulkhead, clamped between the two housings by 4 x M4 screws with an FKM O-ring in a 2.0 mm groove on each face, "
  "separates the chambers.")
B(["<b>Lower chamber (field side):</b> PT100 3-wire leads arrive through the D8 floor hole and land on the MAX31865 terminal "
   "less than 40 mm away. The 5 V supply enters through a PG7 gland, is tied to an anchor post and lands on a 3-way "
   "terminal block. The second PG7 is blanked (spare for a remote probe or comms cable).",
   "<b>Upper chamber (electronics side):</b> the ESP32-DevKitC plugs into 2 x 19-way female headers on a D70 FR4 carrier "
   "screwed to four bulkhead standoffs. An 8-way JST-XH harness (SPI, 5 V, GND) passes through a potted grommet in the "
   "bulkhead. The plastic roof carries an M12 ePTFE vent and a light pipe over the board LED. Wi-Fi works because the "
   "housing is non-metallic.",
   "<b>Thermal separation:</b> the finned SS304 neck (low conductivity, 16 W/mK) keeps the housing interface near 60 C "
   "with a 150 C process (Section 10).",
   "<b>Mounting:</b> Mode A screws straight into a process port; Mode B clamps a 4 mm Al bracket under the hex for a "
   "bench, test rig, calibration-bath lid or machine plate."])
IMG(f"{OUT}/v_isometric.png", w=80 * mm, caption="Figure 2. R1 isometric assembly.")
IMG(f"{OUT}/v_exploded.png", w=150 * mm, caption="Figure 3. Exploded assembly: lid stack, boards, O-rings, bulkhead, housing, neck, probe.")
IMG(f"{OUT}/v_lower_chamber.png", caption="Figure 4. Lower chamber (bulkhead removed): MAX31865 sub-carrier, RTD leads, terminal block, anchors and glands.")
IMG(f"{OUT}/v_upper_chamber.png", caption="Figure 5. Upper chamber (upper housing removed): ESP32-DevKitC on the D70 carrier over the bulkhead.")
IMG(f"{OUT}/v_mounting.png", caption="Figure 6. Mounting arrangement. Mode A: process port. Mode B: bracket for bench, rig or bath.")

S.append(PageBreak())
# ===================================================================== 3 spec table
H1("3. Mechanical specification")
TBL([["#", "Specification", "R1 value", "Basis"],
     ["1", "Overall size", "Housing D88 body / D108 flanges x 99 mm high (+6 vent). Neck + thread 94.5 mm below housing; probe tip 194 mm below housing base. Over gland caps: 108 mm.", "Model; R0 envelope kept"],
     ["2", "Wall thickness", "7 mm body walls (5 mm local at glands after spot-face), 6 mm floor, 5 mm roof, 8 mm flanges", "R0; [Rec] FDM solid walls"],
     ["3", "Lid / attachment", "Upper housing is the lid: 50 mm cup, 5 mm roof; 4 x M4 x 16 A2-70 SHCS on PCD 98 through upper flange + bulkhead into M4 heat-set inserts in the lower flange; counterbore D8 x 4.5", "R0 + [Rec] compression-limiter sleeves"],
     ["4", "Internal clearance", "ESP32 corners 6.6 mm to bore; 22 mm above ESP32 module to roof; MAX31865 17 mm below bulkhead (see Section 4)", "Model"],
     ["5", "PCB mounting", "D70 carrier: 4 x D3.2 on R30 at 45/135/225/315 deg, M3 x 6 into inserts in 8 mm bulkhead standoffs. Sub-carrier 30 x 30: 4 x D3.2 at X -29.5/-6.5, Y +/-11.5, M3 x 6 into 8 mm floor standoffs", "Model; boards have no holes - carriers used"],
     ["6", "Cable entries", "2 x PG7 (thread 12.5, hole D12.7) at +/-35 deg, Z 22, 22 x 22 pads; clamping 3-6.5 mm, IP68 rated nylon gland", "[Rec]"],
     ["7", "PT100 routing / strain relief", "Integral probe: sheath sealed in the neck by a 6 mm compression ferrule; leads up the neck bore to MAX31865. Remote probe option: through the spare PG7 + anchor post", "R0 + [Rec]"],
     ["8", "Mounting holes", "Mode A: 1/2\"-14 NPT, 27 AF hex. Mode B: bracket 120 x 64 x 4 Al, D21.8 centre hole, 4 x slots 11 x 5.5 at X +/-48, Y +/-22 (M5)", "Model"],
     ["9", "Material", "Housing + bulkhead: ASA (FDM); PETG for processes <= 100 C. Neck: SS304. Seals: FKM. Bracket: Al 6061-T6", "Section 5"],
     ["10", "Tolerances / clearances", "FDM +/-0.3 mm general; holes printed undersize then drilled/reamed; 0.3 mm/side on printed fits; board edges >= 2 mm to walls; groove depth 2.0 +0.1/-0", "[Rec]"],
     ["11", "Fasteners", "4 x M4x16 SHCS A2-70 + 4 x M4x8.1 brass inserts; 3 x M4x10 A2 (floor to neck flange); 10 x M3x6 + 10 x M3x5.7 inserts (carriers, terminal); PG7 x 2 + plug; M12 vent", "Section 6"],
     ["12", "Gasket groove", "Face groove ID 78 / OD 85.2, 3.6 wide, 2.0 deep, both bulkhead faces. O-ring 80 x 2.65 FKM 75 ShA: squeeze 24.5 %, gland fill 76.6 %, O-ring OD 85.3 seats on groove OD (no stretch). Flanges close face-to-face (hard stop)", "R0; [Illustrative] Section 9.3"],
     ["13", "Thermal separation", "60 mm SS304 finned neck, 65 mm fitting-to-housing; target housing interface <= 60 C, interior <= 50 C at 150 C process, 40 C ambient", "Section 10"],
     ["14", "Assembly / maintenance", "Open top: 4 x M4. ESP32 stage out: unplug JST, 4 x M3. Lower chamber: lift bulkhead. Terminal screws reachable from above with a 2.5 mm driver", "Section 11"],
     ["15", "Loads / environment", "[Assump] Indoor lab / test rig / machine; ambient 0-40 C; RH <= 90 % non-condensing; process <= 150 C (ASA). Loads: 100 N side push on housing, 20 N.m twist when installing, 10 g shock, 2 g 10-150 Hz vibration, 40 N cable pull", "[Assump] - confirm"]],
    [7, 30, 100, 37])

# ===================================================================== 4 fit table
H1("4. Component fit and clearance")
P("Clearances are measured on the R1 CAD model. Board sizes are datasheet or vendor values [Assump]; Section 14 explains how to replace them.")
TBL([["Component", "Size used in CAD", "Location", "Critical clearance", "Result"],
     ["ESP32-DevKitC V4", "54 x 28 x 1.6 PCB; module 25.5 x 18 x 3.2", "Upper chamber, on headers, top of PCB at Z 68.7", "Corners to D74 bore 6.6 mm; module to roof 22.1 mm", "OK"],
     ["ESP32 antenna", "End 6 mm of module", "+X end of board", ">= 15 mm to metal (inserts 17 mm, M4 screw 26 mm); no copper under antenna on carrier", "OK - keep carrier copper-free there"],
     ["D70 carrier", "D70 x 1.6 FR4", "Z 57-58.6 on 8 mm standoffs", "2 mm to bore; JST-XH underneath clears bulkhead by 2 mm", "OK"],
     ["USB connector", "Micro-USB, -X end", "Upper chamber", "25 mm free above board for right-angle plug (cup removed)", "OK"],
     ["MAX31865 breakout", "28.0 x 25.5 x 1.6 (Adafruit 3328)", "Lower chamber on sub-carrier, PCB Z 18.1", "17.3 mm under bulkhead; RTD terminal 1.5 mm from floor-hole edge in plan", "OK"],
     ["Sub-carrier 30 x 30 R4", "FR4", "Centre X -18", "1.9 mm to bore at corners", "Tight - check with real board"],
     ["Terminal block (3-way)", "10 x 15 x 12", "Pedestal at X 26", "4.6 mm to bore; 7 mm to M4 neck screw heads", "OK"],
     ["PG7 gland + locknut", "Hex 15 AF, locknut 3 mm", "+/-35 deg, Z 22", "Locknut in D21 spot-face; 7.5 mm to anchor post", "OK"],
     ["Cable in gland", "Power cable D5 (2 x 0.5 mm2)", "-35 deg", "Within 3-6.5 mm clamping range", "OK"],
     ["Bulkhead grommet", "D10 hole, harness D3.2", "X -20", "Harness passes above MAX31865 header", "OK"],
     ["Interference check", "All solids", "Full assembly", "Boolean intersection of every part pair: 0 mm3 (only wire ends inside terminal entries)", "OK"]],
    [27, 33, 33, 55, 26])

S.append(PageBreak())
# ===================================================================== 5 materials
H1("5. Material selection")
TBL([["Material", "Glass transition / HDT (C)", "Strength / stiffness", "Moisture & UV", "Electrical", "Printing", "Cost", "Verdict"],
     ["PLA", "Tg ~60 / HDT ~55", "Good but creeps", "Fair / poor UV", "Insulator", "Very easy", "Low", "Reject: creeps above ~45 C, softens near the hot flange"],
     ["PETG", "Tg ~80 / HDT ~70", "Good, tough", "Good / fair", "Insulator", "Easy", "Low", "OK for bench use, processes <= 100 C"],
     ["ABS", "Tg ~105 / HDT ~95", "Good", "Fair / poor UV", "Insulator", "Needs enclosure", "Low", "OK, but ASA is better"],
     ["ASA", "Tg ~100 / HDT ~95", "Good, ~40 MPa XY", "Good / good UV", "Insulator", "Needs enclosure", "Low-medium", "Selected: heat margin at 60 C flange, outdoor/UV safe"],
     ["Polycarbonate", "Tg ~147 / HDT ~130", "Very good", "Absorbs water / fair", "Insulator", "Hard (warp, 300 C)", "Medium", "Upgrade if process > 150 C"],
     ["PA66-GF30 (R0)", "HDT ~250 (moulded)", "Excellent", "Absorbs water", "Insulator", "Injection mould only", "High tooling", "Production option only"],
     ["Al / SS sheet box", "> 300", "Excellent", "Excellent", "Conductive, blocks Wi-Fi", "Fabrication + earthing", "Medium", "Reject for prototype: needs external antenna and earthing"]],
    [20, 24, 21, 21, 17, 20, 15, 36])
P("Values are typical datasheet ranges [Illustrative]; check the filament supplier's datasheet for your spool. FDM parts are "
  "weaker between layers (use about 0.6 x the XY strength for loads across layers), so print the housings upright: the "
  "bolt-load and side-load paths then run along the layers. Other materials: SS304 neck (k = 16.2 W/mK, Sy >= 205-215 MPa "
  "annealed), FKM seals (-20 to 200 C, oil resistant), Al 6061-T6 bracket (Sy 276 MPa).")

# ===================================================================== 6 BOM
H1("6. Enclosure bill of materials")
TBL([["#", "Part", "Specification", "Qty", "Make / source", "Indicative cost (INR)"],
     ["1", "Lower housing", "ASA, FDM, ~140 g, R1_lower_housing.step", "1", "Printed in-house", "250-350"],
     ["2", "Upper housing", "ASA, FDM, ~140 g, R1_upper_housing.step", "1", "Printed in-house", "250-350"],
     ["3", "Bulkhead", "ASA, FDM, ~40 g, R1_bulkhead.step", "1", "Printed in-house", "80-120"],
     ["4", "O-ring", "80 x 2.65 FKM 75 ShA (ISO 3601)", "2 (+2 spare)", "Seal supplier", "60-120 each"],
     ["5", "Neck", "SS304: 1/2\" NPT hex nipple + 1/2\" Sch 10S tube 60 mm + D50 x 4 flange (TIG) + 4 fins D40 x 1.5", "1", "Workshop / fabricator", "800-1500"],
     ["6", "Neck flange gasket", "FKM sheet 1 mm, D44 / D10", "1", "Cut from sheet", "50"],
     ["7", "PT100 probe", "Class A, 3-wire, 6 mm SS sheath, 100 mm insertion + leads; 6 mm compression ferrule", "1", "Sensor supplier", "800-2000"],
     ["8", "ESP32 board", "ESP32-DevKitC V4 (WROOM-32E) or equivalent", "1", "Electronics distributor", "450-900"],
     ["9", "RTD converter", "MAX31865 breakout (Adafruit 3328 or equivalent, 430 ohm Rref)", "1", "Electronics distributor", "350-1500"],
     ["10", "ESP32 carrier", "FR4 perfboard cut to D70, 2 x 19-way female header", "1", "Cut in lab", "60-100"],
     ["11", "MAX sub-carrier", "FR4 perfboard 30 x 30", "1", "Cut in lab", "20"],
     ["12", "Harness", "JST-XH 8-way pair + 8-core 26 AWG, 120 mm", "1", "Distributor", "40-80"],
     ["13", "Terminal block", "3-way 5 mm pitch screw terminal, panel-mount", "1", "Distributor", "30-60"],
     ["14", "Cable glands", "PG7 nylon, IP68, 3-6.5 mm, with locknut + sealing ring", "2", "Distributor", "20-40 each"],
     ["15", "Blanking plug", "PG7 or M12 nylon blanking plug", "1", "Distributor", "15-30"],
     ["16", "Vent", "M12x1.5 ePTFE pressure-equalising vent", "1", "Distributor", "150-400"],
     ["17", "Light pipe", "D5 PC rod, 14 mm, glued", "1", "Distributor", "20"],
     ["18", "Grommet", "Silicone D10 grommet + RTV potting", "1", "Hardware", "20"],
     ["19", "Lid screws", "M4 x 16 SHCS A2-70", "4", "Hardware", "5-10 each"],
     ["20", "Heat-set inserts", "M4 x 8.1 brass (4), M3 x 5.7 brass (10)", "14", "Hardware", "3-8 each"],
     ["21", "Compression limiters [Rec]", "Brass sleeve OD 7.5 / ID 4.3 x 12", "4", "Turned in workshop", "20 each"],
     ["22", "Neck screws", "M4 x 10 A2 pan head + washer", "3", "Hardware", "5 each"],
     ["23", "Carrier screws", "M3 x 6 A2 pan head", "10", "Hardware", "3 each"],
     ["24", "Power cable", "2 x 0.5 mm2 PVC/PUR D5, ferrules", "1 m", "Hardware", "40"],
     ["25", "Rig bracket (Mode B)", "Al 6061-T6 4 mm, 120 x 64, + 1/2\" NPT locknut", "1", "Laser / hand cut", "150-300"]],
    [6, 28, 66, 14, 32, 28])
P("Costs are indicative Indian retail ranges for budgeting only [Illustrative] - replace them with actual quotes for the "
  "submission. Electronics BOM items beyond the enclosure (passives, supply) belong in the electronics BOM.", small)

S.append(PageBreak())
# ===================================================================== 7 modelling sequence
H1("7. CAD modelling sequence and files")
H2("7.1 Workflow")
B(["<b>Source of truth:</b> parametric CadQuery script <i>r1c.py</i> (all dimensions are named parameters; edit and rebuild).",
   "<b>Exchange:</b> STEP AP214 for every part and the assembly - opens in Fusion 360, SolidWorks, FreeCAD and ANSYS SpaceClaim / DesignModeler.",
   "<b>Native editable file:</b> no Fusion .f3d or SolidWorks .sldprt has been generated. To get one, import the STEP into Fusion "
   "(or FreeCAD) and rebuild it with the feature sequence below, so the features become editable.",
   "<b>Printing:</b> STL per part (0.04 mm tolerance) from the same model."])
H2("7.2 Feature sequence to rebuild in Fusion 360 / FreeCAD")
TBL([["Part", "Feature sequence (sketch plane, feature, dimension)"],
     ["Lower housing", "1. XY: circle D88, extrude 45. 2. Offset plane Z 37: circle D108, extrude 8 (flange). 3. Shell / cut D74 from Z 6. "
      "4. Fillet bottom edge R3. 5. Pads: 22 x 22 x 6 at +/-35 deg, centre Z 22; hole D12.7; inner spot-face D21 to leave 5 mm wall. "
      "6. Bosses D11 under flange at PCD 98 (0/90/180/270), holes D5.6 x 14. 7. Top face: groove ID 78 / OD 85.2, depth 2.0. "
      "8. Floor: 3 x D4.5 on PCD 38 (30/150/270), D8 centre. 9. Pedestal 12 x 19 x 5 at X 26, 2 x D4.0. 10. Anchor posts 5 x 10 on gland axes at R29, tie slot 2.2 x 12, saddle R2.6. 11. Sub-carrier standoffs D7 x 8, D4.0 bores."],
     ["Bulkhead", "XY: circle D108, extrude 4. 4 x D4.6 on PCD 98. D10 at (-20, 0). 4 standoffs D7 x 8 on R30 at 45 deg, D4.0 bores."],
     ["Upper housing", "Circle D88, extrude 50 from Z 49; flange D108 x 8; fillet top R6; cavity D74 to 5 mm roof; 4 x D4.6 + C'bore D8 x 4.5; groove on mating face; D12 at X+22 (vent), D5 at X-22 (light pipe)."],
     ["Neck", "Revolve profile: flange D50 x 4, tube D21.3 / 15.8 x 60, 4 fins D40 x 1.5 at 12 pitch, hex 27 AF x 10, NPT 1/2\"-14 (Fusion: Thread tool, NPT, 1/2, modelled) 19 long; 3 x M4 tapped PCD 38."],
     ["Carriers", "D70 x 1.6 disc, 4 x D3.2 on R30 at 45 deg; 30 x 30 x 1.6 R4 square, 4 x D3.2 on 23 x 23."],
     ["Assembly", "Ground the lower housing; joints: bulkhead and upper housing coaxial and planar on the flange faces; neck coaxial under the floor (1 mm gasket); boards on standoffs; glands on pads. Run Interference check."]],
    [26, 148])
H2("7.3 Files delivered")
TBL([["File", "Content"],
     ["AutoCalibrate_PT100_Node_R1_assembly.step", "Full coloured assembly (housings, seals, boards, glands, neck, probe, cables)"],
     ["R1_lower_housing / upper_housing / bulkhead.step", "Printable parts (also as STL)"],
     ["R1_neck.step, R1_rig_bracket.step", "Fabricated metal parts"],
     ["R1_carrier.step, R1_sub_carrier.step", "Board carriers"],
     ["R1_drawings.pdf", "4 A3 sheets: GA, lower housing, upper housing + bulkhead, carriers / neck / bracket"],
     ["r1c.py, build.py, render.py, drawings.py", "Parametric source and scripts that regenerate everything"]],
    [70, 104])

# ===================================================================== 8 drawings
H1("8. Drawing requirements")
B(["<b>Sheet 1 - General arrangement:</b> front, top and side views; overall dimensions, chamber heights, neck length, probe depth, gland angles. [Included]",
   "<b>Sheet 2 - Lower housing:</b> top view with all holes and features, section A-A with wall, floor, flange and groove, section B-B through the gland. [Included]",
   "<b>Sheet 3 - Upper housing and bulkhead:</b> section C-C, vent and light-pipe holes, counterbores, bulkhead hole pattern. [Included]",
   "<b>Sheet 4 - Carriers, neck, bracket:</b> board layout with mounting-hole coordinates, neck section, bracket. [Included]",
   "<b>To add once parts are measured:</b> groove detail at 5:1 with surface finish (Ra <= 3.2 on seal lands), GD&amp;T flatness 0.1 on both flange faces, "
   "thread callout per ASME B1.20.1 for the NPT, weld symbols on the neck, and a harness drawing (pin-out, lengths).",
   "<b>Title block:</b> part number, material, finish, tolerance class, scale, revision and approval."])

S.append(PageBreak())
# ===================================================================== 9 FEA
H1("9. FEA plan and preliminary checks")
H2("9.1 What to analyse (ANSYS Mechanical)")
TBL([["Study", "Part / model", "Material data", "Boundary conditions", "Loads"],
     ["S1 Process mount (Mode A)", "Neck + hex + NPT (solid), housing as point mass or bonded body", "SS304: E 193 GPa, nu 0.29, Sy 205-215 MPa, Su 515 MPa", "Fixed support on first 5 engaged thread flanks (or on the root cylinder of the engaged length)", "L1 100 N horizontal at housing top (lever 106 mm above flange); L2 20 N.m torque on housing; L3 10 g lateral + 1 g down on 0.4 kg"],
     ["S2 Housing clamp", "Upper housing + bulkhead + lower flange, bolt pretension, O-ring as pressure on groove floor", "ASA: E 2.0-2.3 GPa (use 0.7 x across layers), nu 0.35, sigma_t 40 MPa XY / 25 MPa Z", "Frictional contacts between flanges (mu 0.3); fixed at floor screws", "4 x bolt pretension 625 N; O-ring reaction ~1 kN total; 60 C material data if available"],
     ["S3 Floor joint", "Lower housing floor + 3 x M4 to neck flange", "ASA as above", "Neck flange fixed", "Moment from L1 (9.9 N.m at floor), screw preload"],
     ["S4 Rig bracket (Mode B)", "Bracket + locknut contact", "Al 6061-T6: E 68.9 GPa, Sy 276 MPa", "Fixed at the 4 slot washers", "Node weight 0.67 kg x 10 g shock, 100 N side push"],
     ["S5 Modal", "Full node on Mode A / Mode B", "As above", "As S1 / S4", "First natural frequency - target > 150 Hz (above the vibration test band)"]],
    [24, 34, 36, 40, 40])
H2("9.2 Mesh, outputs and acceptance")
B(["<b>Mesh:</b> quadratic tetrahedra (SOLID187); 2 mm global, 0.3-0.5 mm on thread roots, the tube-to-hex fillet, insert bosses and groove corners; at least 3 elements through every wall.",
   "<b>Convergence:</b> refine three times until the peak stress changes by less than 5 %; report the converged value.",
   "<b>Outputs:</b> equivalent (von Mises) stress for SS304 and Al; maximum principal stress for printed ASA; total deformation; contact pressure on the flange faces (gap = 0 at the O-ring); bolt reaction forces.",
   "<b>Factor of safety:</b> FoS = Sy / sigma_vM for metals (target >= 2 on L1-L3); FoS = sigma_t(Z) / sigma_1 for ASA (target >= 3 because of layer adhesion and creep).",
   "<b>Validation:</b> compare with the beam hand-calculation below; check reaction forces balance the applied loads; then do a physical check by hanging 10 kg from the housing top and measuring the deflection with a dial gauge."])
H2("9.3 Preliminary checks (to be repeated in ANSYS)")
TBL([["Check", "Method", "Result", "Status"],
     ["Neck tube root bending, L1", "Hand calc: sigma = M c / I, M = 100 N x 170 mm, I = pi/64 (21.3^4 - 15.8^4) = 7045 mm4", "25.7 MPa, FoS 8.4", "[Illustrative]"],
     ["Neck, L1 and L2 (R0 geometry, unchanged in R1)", "Our earlier open-source linear FEA (scikit-fem, quadratic tets, 9.4k nodes) of the R0 neck", "Peak 48.2 MPa (L1) / 47.7 MPa (L2) at first engaged thread root, FoS 4.5; tube root 25.0 MPa vs 25.7 hand calc", "Preliminary - not ANSYS, not converged study"],
     ["Thread-root notch", "Kt ~2.5 applied to the root-diameter model", "FoS ~1.8 under misuse loads", "[Illustrative]"],
     ["O-ring seal force", "FKM 75 ShA, 2.65 CS, 25 % squeeze: ~2-4 N/mm x 256 mm", "0.5-1.0 kN per ring", "[Illustrative] chart estimate"],
     ["Bolt preload", "T = K F d, K 0.2, d 4 mm, T 0.5 N.m", "625 N per bolt, 2.5 kN total vs <= 1.0 kN seal force -> faces close", "[Illustrative]"],
     ["Insert pull-out", "M4 brass insert in ASA, typical 1.2-1.5 kN", "FoS ~2 at 625 N - verify by test", "[Assump]"],
     ["Floor screws, L1", "3 bolts on R19: F = 2M / (3r), M = 9.9 N.m", "347 N per screw; ASA pull-through ~3 kN (pi x 7 x 6 x 25 MPa), FoS ~9", "[Illustrative]"],
     ["Internal temperature rise", "0.5 W ESP32 + 1.1 W through neck, R = 1/(hA) ~2 K/W", "~3 K above ambient (43 C at 40 C ambient)", "[Illustrative]"]],
    [34, 62, 50, 28])
IMG(f"{R0}/analysis_fea_stress.png", caption="Figure 7. Preliminary open-source FEA of the R0 neck (geometry unchanged in R1). Shown only to "
    "size the ANSYS study; repeat it in ANSYS with a convergence study before quoting it as a result.")

S.append(PageBreak())
# ===================================================================== 10 thermal
H1("10. Thermal separation and isolation")
P("The brief suggests a 50 mm separation as a starting target, not a rule. R1 uses <b>65 mm</b> from the process fitting to "
  "the housing base (60 mm neck + flange + gasket). This spacing was chosen so that the interface under the plastic housing "
  "stays at or below about 60 C with a 150 C process and 40 C ambient. That keeps ASA well below its ~95 C HDT, keeps the "
  "interior air below 50 C (ESP32 module rated -40 to 85 C), and keeps the MAX31865 reference resistor close to room temperature.")
TBL([["Neck option, 150 C process, 40 C ambient", "Housing interface (C)", "Heat into housing (W)", "Interior (C)"],
     ["No neck (housing on the fitting)", "143.9", "5.87", "53.7"],
     ["60 mm Al 6061 neck, finned", "123.0", "4.68", "51.1"],
     ["60 mm SS304 neck, plain", "69.9", "1.65", "44.6"],
     ["60 mm SS304 neck, finned (R1)", "59.9", "1.08", "43.3"]],
    [80, 32, 32, 30])
P("[Illustrative] 1-D finned-conduction model (from the R0 study; neck unchanged): h = 10 W/m2K, k(SS304) = 16.2 W/mK, "
  "hex held at process temperature, FKM gasket and 6 mm floor in series. Real values depend on mounting, airflow and "
  "radiation, so measure them (Section 12, T1-T3).")
B(["<b>Measurement side:</b> only the sheath tip is in the process. The ferrule seal sits inside the thread, so conduction "
   "along the sheath is small for 100 mm immersion (rule of thumb: immersion >= 10-15 x sheath diameter).",
   "<b>Electronics side:</b> the ESP32 (main heat source, ~0.5 W) sits above the bulkhead, away from the MAX31865. A 25 ppm/K "
   "Rref at +18 K gives ~0.05 % gain error (about 0.07 Ohm at 100 C, ~0.18 C). Choose a <= 10 ppm/K Rref, or calibrate at "
   "the operating temperature, to keep within Class A (+/-0.35 C at 100 C).",
   "<b>PETG limit:</b> if PETG is used instead of ASA, limit the process to about 100 C (interface ~50 C)."])
IMG(f"{R0}/analysis_thermal.png", caption="Figure 8. [Illustrative] Neck temperature profile and neck-option comparison (R0 model, neck unchanged in R1).")

S.append(PageBreak())
# ===================================================================== 11 manufacturing
H1("11. Manufacturing and assembly plan")
H2("11.1 Manufacturing")
TBL([["Part", "Process", "Settings / steps"],
     ["Housings + bulkhead", "FDM, ASA (enclosed printer) or PETG", "0.4 mm nozzle, 0.2 mm layers (0.1 mm for the last 2 mm under groove faces), 6+ perimeters so walls are solid, 40 % gyroid infill elsewhere. Lower housing open side up; upper housing roof-down with tree supports; bulkhead flat. Dry filament. Anneal ASA 1 h at 80 C if dimensionally stable."],
     ["Post-processing", "Drill / ream / insert", "Ream D12.7 gland holes and D4.6 bolt holes; press heat-set inserts at 230 C; check groove depth (2.0 +0.1/-0) and lightly sand the seal lands flat on 400 grit on glass."],
     ["Neck", "Weld fabrication", "1/2\" NPT SS304 hex nipple, 60 mm 1/2\" Sch 10S tube, laser-cut D50 x 4 flange, TIG weld; drill 3 x D3.3 and tap M4; fins laser-cut and brazed or press-fit (optional); pickle and passivate."],
     ["Carriers", "Cut perfboard", "Cut D70 and 30 x 30; drill D3.2; remove copper under the ESP32 antenna area; solder headers, terminal and JST."],
     ["Bracket", "Laser / bandsaw + drill", "4 mm Al 6061-T6, D21.8 hole, 4 slots, deburr."]],
    [30, 34, 110])
H2("11.2 Assembly (about 30 min)")
B(["1. Fit PG7 glands and the blanking plug with sealing rings; tighten locknuts to 2.5 N.m.",
   "2. Bolt the neck to the lower housing floor: FKM gasket, 3 x M4 x 10 with washers, 1.5 N.m; seal the screw heads with a dab of RTV.",
   "3. Insert the PT100 up the neck; set the compression ferrule; route the leads through the D8 hole.",
   "4. Screw the MAX31865 sub-carrier to its standoffs; land the RTD leads (3-wire jumper set on the board); ferrules on all cores.",
   "5. Pass the power cable through the gland; tie it to the anchor post leaving a 30 mm service loop; land it on the terminal block; tighten the gland cap.",
   "6. Fit the O-ring into the lower groove; pass the JST harness through the bulkhead grommet; place the bulkhead; pot the grommet with RTV.",
   "7. Screw the ESP32 carrier to the bulkhead standoffs (M3 x 6, 0.4 N.m); plug in the ESP32 and the JST harness.",
   "8. Fit the second O-ring; place the upper housing; fit the 4 x M4 x 16 with compression limiters; tighten crosswise to 0.5 N.m.",
   "9. Fit the vent and light pipe; do the functional test, then leak test L1 (Section 12)."])
H2("11.3 Maintenance")
P("Remove 4 x M4 and lift the upper housing to reach the ESP32 (USB for re-flashing; OTA is preferred). Unplug the JST and "
  "remove 4 x M3 to lift the ESP32 stage out. Lift the bulkhead to reach the terminals and the MAX31865. Replace the O-rings "
  "whenever the housing is opened after thermal cycling, or annually.")

# ===================================================================== 12 validation
H1("12. Validation checklist")
TBL([["ID", "Check", "Method", "Pass criterion"],
     ["F1", "Component fit", "Dry-assemble with real boards; feeler gauges at bore and roof", "No contact; >= 1.5 mm to bore; lid closes face-to-face"],
     ["F2", "Assembly / maintenance", "Time a full open-close cycle", "<= 10 min, no tools beyond 2.5/3 mm hex and a screwdriver"],
     ["M1", "Mounting stability (A and B)", "Hang 10 kg (~100 N) from the housing top; dial gauge", "No yield; deflection matches FEA within 20 %"],
     ["M2", "Install torque", "20 N.m on the hex with the housing restrained", "No thread or neck damage; housing does not rotate"],
     ["C1", "Cable pull / strain relief", "40 N axial pull for 1 min, then 25 x 90 deg flex", "< 2 mm slip; terminals undisturbed; continuity OK"],
     ["V1", "Vibration (machine mounting)", "IEC 60068-2-6: 10-150 Hz, 2 g, 1 oct/min, 10 sweeps per axis", "No loosening; readings stable within 0.1 C; no resonance below 150 Hz"],
     ["T1", "Thermal separation", "Thermocouples on flange, floor and interior air; probe in a 150 C bath, 2 h", "Interface <= 60 C, interior <= 50 C"],
     ["T2", "Measurement effect", "Compare against a reference thermometer in the bath at 0, 50, 100, 150 C", "Within Class A tolerance after calibration"],
     ["T3", "Self-heating of the electronics", "Interior rise with Wi-Fi on, ambient 25 C", "<= 5 K"],
     ["S1", "Enclosure strength", "Drop 1 m onto concrete (probe removed), 2 drops", "No cracks; seals intact"],
     ["S2", "Fastener retention", "Re-torque check after 50 thermal cycles 20-60 C", "Torque loss < 30 %; inserts not pulled"],
     ["L1", "Seal pre-check (in-house)", "Pressure-decay test: 0.2 bar for 5 min with the vent plugged; and hose spray with tissue indicators inside", "Decay < 5 %; tissue dry"],
     ["IP", "Ingress protection claim", "IEC 60529 at a test lab: IP6X dust chamber (8 h, talc, under vacuum) and IPX5 jets (6.3 mm nozzle, 12.5 L/min, 3 m, >= 3 min)", "Only then may 'IP65' be claimed"],
     ["P1", "Manufacturing feasibility", "Print time, material, failure rate; neck fabrication time", "Record for the submission"]],
    [10, 34, 78, 52])

S.append(PageBreak())
# ===================================================================== 13 safety
H1("13. Safety considerations (verify against the template's safety page)")
B(["<b>Electrical:</b> SELV only - 5 V DC from an external, certified adapter. No mains voltage inside the housing. Polarity marked at the terminal block; polyfuse on the carrier [Rec].",
   "<b>Insulation:</b> the all-plastic housing needs no protective earth. The SS304 neck and probe are isolated from the electronics; the RTD element is isolated inside its sheath (check the probe's insulation rating, typically >= 100 MOhm at 100 V DC).",
   "<b>Hot surfaces:</b> the neck can exceed 60 C at high process temperature - add a 'hot surface' label and keep the fins accessible only to trained users.",
   "<b>Pressure:</b> Mode A is for low-pressure or open vessels unless the probe, ferrule and neck are rated for the line pressure. The NPT joint needs PTFE tape or sealant.",
   "<b>Fire:</b> ASA and PETG are not UL94 V-0. That is acceptable for SELV low-power electronics; use V-0 PC-ABS for a production design.",
   "<b>Mechanical:</b> deburr metal edges; tie the cable to the anchors so a pull cannot load the terminals; secure the bracket with 4 x M5 bolts.",
   "<b>ESD and handling:</b> handle the boards with ESD precautions; the ESP32 stage is socketed so it can be replaced without soldering."])

# ===================================================================== 14 assumptions
H1("14. Assumptions and how to replace them")
TBL([["Assumption", "Value used", "How to replace with measured data"],
     ["ESP32 board size", "54 x 28 mm, header rows 25.4 mm apart", "Measure with calipers; edit ESP_L, ESP_W, ESP_ROW in r1c.py; rebuild; re-run the interference check"],
     ["MAX31865 board size", "28.0 x 25.5 mm (Adafruit 3328)", "Measure your module (generic red boards differ); edit MAX_LX, MAX_WY"],
     ["Probe", "6 mm sheath, 100 mm immersion, 3-wire", "Use the supplier drawing; edit SHEATH_D, SHEATH_L"],
     ["Process / ambient", "<= 150 C / <= 40 C", "Use the real test-rig values; re-run the thermal model; measure T1"],
     ["Loads", "100 N, 20 N.m, 10 g, 2 g vibration", "Replace with the rig or machine data (accelerometer survey)"],
     ["Material properties", "Typical datasheet ranges", "Use the filament datasheet; ideally test printed coupons (ISO 527) in Z and XY"],
     ["Insert pull-out", "1.2-1.5 kN M4 in ASA", "Pull-test 3 printed coupons"],
     ["Costs", "Indicative ranges", "Vendor quotes"]],
    [32, 48, 94])

# ===================================================================== 15 evidence
H1("15. Evidence for the Stage 2 submission")
B(["Isometric, exploded, half-section, internal (both chambers) and mounting renders (Figures 1-6).",
   "4 dimensioned A3 drawings (R1_drawings.pdf) and the STEP assembly + part files.",
   "Mechanical specification, fit and material tables and the BOM (Sections 3-6).",
   "ANSYS FEA report for S1-S5 with mesh convergence, FoS table and the hand-calculation comparison (to be produced from Section 9).",
   "Photos of printed parts, the fabricated neck and the assembled node; the print log (time, material, settings).",
   "Test records: fit (F1), pull (C1), vibration (V1), thermal (T1-T3), leak pre-check (L1); the IP test report only if done at a lab.",
   "Calibration data: probe vs reference at 4 points, with the uncertainty budget (links to the calibration algorithm).",
   "R0 to R1 change log (Section 1.3) showing the design iteration."])

# ===================================================================== appendix drawings
for i, f in enumerate(["dwg_1_GA.png", "dwg_2_lower.png", "dwg_3_upper.png", "dwg_4_parts.png"], 1):
    im = PILImage.open(f"{OUT}/{f}").rotate(90, expand=True)
    rp = f"{OUT}/_rot_{f}"
    im.save(rp)
    S.append(PageBreak())
    H2(f"Appendix A{i}. Drawing sheet {i} (A3, rotated)")
    IMG(rp, w=172 * mm, maxh=245 * mm)


def deco(c, d):
    c.saveState()
    c.setFont("Helvetica", 7.5); c.setFillColor(colors.HexColor("#555555"))
    c.drawString(18 * mm, 10 * mm, "AutoCalibrate AI | PT100 node | Mechanical design R1 (from R0) | PRELIMINARY | 25 Oct 2026")
    c.drawRightString(192 * mm, 10 * mm, str(d.page))
    c.restoreState()


doc = SimpleDocTemplate(PDF, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=15 * mm, bottomMargin=16 * mm,
                        title="AutoCalibrate AI PT100 Node - Mechanical Design R1", author="AutoCalibrate AI team")
doc.build(S, onFirstPage=deco, onLaterPages=deco)
print("report ok")
