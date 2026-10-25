"""
AutoCalibrate AI PT100 node - R1 (evolution of R0 IP65_PT100_Enclosure.step).
R0 form kept: cylindrical two-chamber housing, bulkhead, 2 mm O-ring grooves, PG7 glands,
M12 vent, SS304 finned neck + 1/2" NPT, PT100 in 6 mm sheath.
R1 changes: off-the-shelf ESP32-DevKitC (upper chamber, round carrier) and MAX31865 breakout
(lower chamber, sub-carrier next to the RTD leads), FDM ASA housing, gland angles/bolt pattern
re-clocked, cable anchors, terminal pedestal, optional rig/bath bracket.
All dimensions in mm. Z is up; z = 0 is the underside of the lower housing floor.
"""
import math
import cadquery as cq

# ---------------- parameters ----------------
BODY_OD = 88.0          # chamber outer diameter
BODY_ID = 74.0          # chamber inner diameter (wall 7 mm)
FLANGE_OD = 108.0
FLANGE_T = 8.0
BOLT_PCD = 98.0
BOLT_HOLE = 5.6         # for M4 brass heat-set insert (lower) / clearance 4.5 (upper)
N_BOLTS = 4

LOWER_H = 45.0          # terminal chamber height (incl. floor)
FLOOR_T = 6.0
UPPER_H = 50.0          # PCB chamber height (incl. roof)
ROOF_T = 5.0
BULKHEAD_T = 4.0

# O-ring face-seal groove (spec: 2 mm deep)
GROOVE_DEPTH = 2.0
GROOVE_ID = 78.0
GROOVE_W = 3.6
GROOVE_OD = GROOVE_ID + 2 * GROOVE_W
ORING_CS = 2.65         # ISO 3601 80 x 2.65 mm FKM
ORING_MEAN_D = (GROOVE_ID + GROOVE_OD) / 2

# PG7 cable gland (thread 12.5 mm)
PG7_HOLE = 12.7          # PG7 thread 12.5 + 0.2 clearance (R0: 12.5)
GLAND_WALL = 5.0         # local wall at the gland after inner spot-face
GLAND_POCKET_D = 21.0
GLAND_Z = 22.0
GLAND_ANGLES = (-35.0, 35.0)   # -35: power cable, +35: spare / remote-probe (blanked)

# Process connection
NECK_OD = 21.3          # 1/2" pipe OD, SS304
NECK_ID = 15.8
NECK_L = 60.0           # thermal-decoupling neck length
NECK_FLANGE_D = 50.0
NECK_FLANGE_T = 4.0
FIN_D = 40.0
FIN_T = 1.5
N_FINS = 4
HEX_AF = 27.0
HEX_H = 10.0
NPT_OD = 21.336         # 1/2"-14 NPT major diameter at gauge plane
NPT_PITCH = 25.4 / 14
NPT_LEN = 19.0
SHEATH_D = 6.0          # PT100 sheath, SS304
SHEATH_L = 100.0
GASKET_T = 1.0
NECK_SCREW_START = 30.0   # 3 x M4 at r 19: 30, 150, 270 deg

# PCB
PCB_W, PCB_D, PCB_T = 55.0, 45.0, 1.6
STANDOFF_H = 8.0


def bolt_points(pcd=BOLT_PCD, n=N_BOLTS, start=0.0):
    r = pcd / 2
    return [(r * math.cos(math.radians(start + i * 360 / n)),
             r * math.sin(math.radians(start + i * 360 / n))) for i in range(n)]


def groove_cut(z_face, downward=True):
    """Annular 2 mm groove cut into a face at height z_face."""
    ring = (cq.Workplane("XY").circle(GROOVE_OD / 2).circle(GROOVE_ID / 2)
            .extrude(GROOVE_DEPTH))
    z0 = z_face - GROOVE_DEPTH if downward else z_face
    return ring.translate((0, 0, z0))


# ---------------- lower housing (terminal chamber) ----------------
def lower_housing():
    body = cq.Workplane("XY").circle(BODY_OD / 2).extrude(LOWER_H)
    flange = (cq.Workplane("XY").workplane(offset=LOWER_H - FLANGE_T)
              .circle(FLANGE_OD / 2).extrude(FLANGE_T))
    h = body.union(flange)
    # cavity
    cav = (cq.Workplane("XY").workplane(offset=FLOOR_T)
           .circle(BODY_ID / 2).extrude(LOWER_H))
    h = h.cut(cav)
    # bottom fillet
    h = h.faces("<Z").edges().fillet(3.0)
    # gland bosses (flat pads) + holes
    for a in GLAND_ANGLES:
        pad = (cq.Workplane("YZ").rect(22, 22).extrude(6)
               .translate((BODY_OD / 2 - 3, 0, GLAND_Z))
               .rotate((0, 0, 0), (0, 0, 1), a))
        h = h.union(pad)
        hole = (cq.Workplane("YZ").circle(PG7_HOLE / 2).extrude(30)
                .translate((BODY_OD / 2 - 15, 0, GLAND_Z))
                .rotate((0, 0, 0), (0, 0, 1), a))
        h = h.cut(hole)
    # re-cut cavity so pads don't intrude inside
    h = h.cut(cav)
    # inner spot-face so the gland sees a flat 5 mm wall (PG7 thread length 8 mm, locknut inside)
    for a in GLAND_ANGLES:
        pocket = (cq.Workplane("YZ").workplane(offset=BODY_OD / 2 + 3 - GLAND_WALL - 12)
                  .center(0, GLAND_Z).circle(GLAND_POCKET_D / 2).extrude(12)
                  .rotate((0, 0, 0), (0, 0, 1), a))
        h = h.cut(pocket)
    # bolt bosses under the flange (depth for M4 heat-set inserts)
    for x, y in bolt_points():
        h = h.union(cq.Workplane("XY").workplane(offset=LOWER_H - 18)
                    .center(x, y).circle(5.5).extrude(18 - FLANGE_T + 0.01))
    h = h.cut(cav)
    # bolt holes (heat-set inserts)
    for x, y in bolt_points():
        h = h.cut(cq.Workplane("XY").workplane(offset=LOWER_H - 14)
                  .center(x, y).circle(BOLT_HOLE / 2).extrude(14.1))
    # O-ring groove in top mating face
    h = h.cut(groove_cut(LOWER_H, downward=True))
    # floor: neck-flange screw holes + PT100 lead hole
    for i in range(3):
        a = math.radians(NECK_SCREW_START + i * 120)
        h = h.cut(cq.Workplane("XY").center(19 * math.cos(a), 19 * math.sin(a))
                  .circle(2.25).extrude(FLOOR_T + 1))
    h = h.cut(cq.Workplane("XY").circle(4.0).extrude(FLOOR_T + 1))
    # terminal-block pedestal (power entry) with 2 x M3 insert holes
    h = h.union(cq.Workplane("XY").workplane(offset=FLOOR_T - 0.5).center(TB_X, 0)
                .rect(12.0, 19.0).extrude(PED_H + 0.5).edges("|Z").fillet(1.0))
    for dy in (-7.5, 7.5):
        h = h.cut(cq.Workplane("XY").workplane(offset=FLOOR_T + PED_H - 6).center(TB_X, dy)
                  .circle(2.0).extrude(6.1))
    # cable-tie anchor posts on the gland axes (secondary strain relief)
    for a in GLAND_ANGLES:
        post = (cq.Workplane("XY").workplane(offset=FLOOR_T - 0.5).rect(5.0, 10.0)
                .extrude(GLAND_Z - 2.5 - FLOOR_T + 0.5).edges("|Z").fillet(0.8))
        post = post.cut(cq.Workplane("XY").workplane(offset=GLAND_Z - 8.0).rect(2.2, 12.0).extrude(2.4))
        post = post.cut(cq.Workplane("YZ").workplane(offset=-3).center(0, GLAND_Z).circle(2.6).extrude(6))
        h = h.union(post.translate((ANCHOR_R, 0, 0)).rotate((0, 0, 0), (0, 0, 1), a))
    # MAX31865 sub-carrier standoffs
    for x, y in sub_holes():
        h = h.union(cq.Workplane("XY").workplane(offset=FLOOR_T - 0.5).center(x, y)
                    .circle(3.5).extrude(SUB_STANDOFF + 0.5))
        h = h.cut(cq.Workplane("XY").workplane(offset=FLOOR_T + SUB_STANDOFF - 6).center(x, y)
                  .circle(2.0).extrude(6.1))
    return h


# ---------------- bulkhead (chamber partition) ----------------
def bulkhead():
    z0 = LOWER_H
    b = (cq.Workplane("XY").workplane(offset=z0)
         .circle(FLANGE_OD / 2).extrude(BULKHEAD_T))
    for x, y in bolt_points():
        b = b.cut(cq.Workplane("XY").workplane(offset=z0).center(x, y)
                  .circle(2.3).extrude(BULKHEAD_T))
    # sealed wire feedthrough (potted grommet)
    b = b.cut(cq.Workplane("XY").workplane(offset=z0).center(-20, 0)
              .circle(5.0).extrude(BULKHEAD_T))
    # ESP32 carrier standoffs (M3 heat-set inserts)
    for x, y in car_holes():
        b = b.union(cq.Workplane("XY").workplane(offset=z0 + BULKHEAD_T)
                    .center(x, y).circle(3.5).circle(2.0).extrude(STANDOFF_H))
    return b


def grommet():
    z0 = LOWER_H
    g = (cq.Workplane("XY").workplane(offset=z0 - 1.5).center(-20, 0)
         .circle(6.5).circle(2.5).extrude(1.5))
    g = g.union(cq.Workplane("XY").workplane(offset=z0).center(-20, 0)
                .circle(5.0).circle(2.5).extrude(BULKHEAD_T))
    g = g.union(cq.Workplane("XY").workplane(offset=z0 + BULKHEAD_T).center(-20, 0)
                .circle(6.5).circle(2.5).extrude(1.5))
    return g


# ---------------- upper housing (PCB chamber) ----------------
def upper_housing():
    z0 = LOWER_H + BULKHEAD_T
    body = (cq.Workplane("XY").workplane(offset=z0)
            .circle(BODY_OD / 2).extrude(UPPER_H))
    flange = (cq.Workplane("XY").workplane(offset=z0)
              .circle(FLANGE_OD / 2).extrude(FLANGE_T))
    u = body.union(flange)
    u = u.faces(">Z").edges().fillet(6.0)
    cav = (cq.Workplane("XY").workplane(offset=z0)
           .circle(BODY_ID / 2).extrude(UPPER_H - ROOF_T))
    u = u.cut(cav)
    # bolt counterbores
    for x, y in bolt_points():
        u = u.cut(cq.Workplane("XY").workplane(offset=z0).center(x, y)
                  .circle(2.3).extrude(FLANGE_T))
        u = u.cut(cq.Workplane("XY").workplane(offset=z0 + FLANGE_T - 4.5)
                  .center(x, y).circle(4.0).extrude(5))
    # O-ring groove in bottom mating face
    u = u.cut(groove_cut(z0, downward=False))
    # pressure-equalisation vent (M12 membrane vent) on roof
    top = z0 + UPPER_H
    u = u.cut(cq.Workplane("XY").workplane(offset=top - ROOF_T - 1)
              .center(22, 0).circle(6.0).extrude(ROOF_T + 2))
    # status-LED light pipe hole
    u = u.cut(cq.Workplane("XY").workplane(offset=top - ROOF_T - 1)
              .center(-22, 0).circle(2.5).extrude(ROOF_T + 2))
    return u


def vent():
    top = LOWER_H + BULKHEAD_T + UPPER_H
    v = (cq.Workplane("XY").workplane(offset=top - ROOF_T)
         .center(22, 0).circle(6.0).extrude(ROOF_T))
    v = v.union(cq.Workplane("XY").workplane(offset=top)
                .center(22, 0).polygon(6, 16.0).extrude(3.0))
    v = v.union(cq.Workplane("XY").workplane(offset=top + 3)
                .center(22, 0).circle(7.0).extrude(3.0)
                .faces(">Z").edges().fillet(2.0))
    return v


def light_pipe():
    top = LOWER_H + BULKHEAD_T + UPPER_H
    return (cq.Workplane("XY").workplane(offset=top - ROOF_T - 8)
            .center(-22, 0).circle(2.5).extrude(ROOF_T + 9)
            .faces(">Z").edges().fillet(1.2))


# ---------------- electronics (R1: off-the-shelf boards) ----------------
PG7_HOLE = PG7_HOLE
CAR_D, CAR_T = 70.0, 1.6                 # round FR4 carrier for the ESP32 (upper chamber)
CAR_HOLE_R = 30.0
ESP_L, ESP_W, ESP_T = 54.0, 28.0, 1.6    # ESP32-DevKitC V4 ~54 x 28 (measure)
ESP_ROW = 25.4                           # header row spacing - ASSUMED, measure
HDR_H = 8.5
Z_CAR = LOWER_H + BULKHEAD_T + STANDOFF_H
Z_ESP = Z_CAR + CAR_T + HDR_H
SUB_L, SUB_W, SUB_X = 30.0, 30.0, -18.0  # MAX31865 sub-carrier (lower chamber)
SUB_STANDOFF = 8.0
Z_SUB = FLOOR_T + SUB_STANDOFF
MAX_LX, MAX_WY, MAX_T = 25.5, 28.0, 1.6  # Adafruit #3328: 28.0 x 25.5 x 3 mm
MAX_X0 = SUB_X + SUB_L / 2 - 2.5 - MAX_LX
Z_MAX = Z_SUB + CAR_T + 2.5
TB_X, PED_H = 26.0, 5.0
ANCHOR_R = 29.0


def car_holes():
    return [(CAR_HOLE_R * math.cos(math.radians(a)), CAR_HOLE_R * math.sin(math.radians(a)))
            for a in (45, 135, 225, 315)]


def sub_holes():
    return [(SUB_X + sx * (SUB_L / 2 - 3.5), sy * (SUB_W / 2 - 3.5)) for sx in (-1, 1) for sy in (-1, 1)]


def carrier():
    c = cq.Workplane("XY").workplane(offset=Z_CAR).circle(CAR_D / 2).extrude(CAR_T)
    for x, y in car_holes():
        c = c.cut(cq.Workplane("XY").workplane(offset=Z_CAR - 0.1).center(x, y).circle(1.6).extrude(2))
    return c


def esp_headers():
    out = None
    for sgn in (-1, 1):
        h = cq.Workplane("XY").workplane(offset=Z_CAR + CAR_T).center(0, sgn * ESP_ROW / 2) \
            .rect(19 * 2.54, 2.54).extrude(HDR_H)
        out = h if out is None else out.union(h)
    return out


def esp32():
    return cq.Workplane("XY").workplane(offset=Z_ESP).rect(ESP_L, ESP_W).extrude(ESP_T)


def esp32_parts():
    z = Z_ESP + ESP_T
    xe = ESP_L / 2
    mod = cq.Workplane("XY").workplane(offset=z).center(xe - 25.5 / 2, 0).rect(25.5, 18.0).extrude(0.8)
    can = cq.Workplane("XY").workplane(offset=z + 0.8).center(xe - 25.5 + 17.6 / 2 + 0.5, 0).rect(17.6, 15.8).extrude(2.4)
    usb = cq.Workplane("XY").workplane(offset=z).center(-xe + 2.5, 0).rect(5.5, 7.8).extrude(2.8)
    ldo = cq.Workplane("XY").workplane(offset=z).center(-xe + 14, -6).rect(6.5, 3.5).extrude(1.6)
    p = mod.union(can).union(usb).union(ldo)
    for y in (-9.0, 9.0):
        p = p.union(cq.Workplane("XY").workplane(offset=z).center(-xe + 4.5, y).rect(3.5, 4.5).extrude(1.8))
    return p


def car_connector():
    """JST-XH 8-way on carrier underside: inter-chamber harness (SPI + 5 V + GND), unpluggable."""
    return cq.Workplane("XY").workplane(offset=Z_CAR - 6.0).center(-20.0, -14.0).rect(22.5, 5.8).extrude(6.0)


def sub_carrier():
    c = cq.Workplane("XY").workplane(offset=Z_SUB).center(SUB_X, 0).rect(SUB_L, SUB_W).extrude(CAR_T) \
        .edges("|Z").fillet(4.0)
    for x, y in sub_holes():
        c = c.cut(cq.Workplane("XY").workplane(offset=Z_SUB - 0.1).center(x, y).circle(1.6).extrude(2))
    return c


def max31865():
    return cq.Workplane("XY").workplane(offset=Z_MAX).center(MAX_X0 + MAX_LX / 2, 0) \
        .rect(MAX_LX, MAX_WY).extrude(MAX_T).edges("|Z").fillet(1.0)


def max_parts():
    z = Z_MAX + MAX_T
    ic = cq.Workplane("XY").workplane(offset=z).center(MAX_X0 + 11, 4).rect(5, 5).extrude(1.0)
    rref = cq.Workplane("XY").workplane(offset=z).center(MAX_X0 + 8, -8).rect(3.2, 1.6).extrude(0.6)
    spacer = cq.Workplane("XY").workplane(offset=Z_SUB + CAR_T).center(MAX_X0 + 2.0, 0) \
        .rect(2.54, 8 * 2.54).extrude(2.5)
    return ic.union(rref).union(spacer)


def max_terminal():
    """4-way 3.5 mm terminal for the RTD leads, entries facing +X (towards the neck bore)."""
    z = Z_MAX + MAX_T
    xe = MAX_X0 + MAX_LX
    t = cq.Workplane("XY").workplane(offset=z).center(xe - 3.6, 0).rect(7.2, 14.0).extrude(8.0)
    for i in range(4):
        y = -5.25 + i * 3.5
        t = t.cut(cq.Workplane("YZ").workplane(offset=xe - 2.9).center(y, z + 3.0).rect(2.2, 2.2).extrude(3.0))
        t = t.cut(cq.Workplane("XY").workplane(offset=z + 6.5).center(xe - 4.5, y).circle(1.1).extrude(2))
    return t


def terminal_block():
    z = FLOOR_T + PED_H
    t = cq.Workplane("XY").workplane(offset=z).center(TB_X, 0).rect(10.0, 15.0).extrude(12.0)
    for dy in (-7.5, 7.5):
        t = t.union(cq.Workplane("XY").workplane(offset=z).center(TB_X, dy).rect(8.0, 4.0).extrude(2.0))
    for i in range(3):
        y = -5.0 + i * 5.0
        t = t.cut(cq.Workplane("YZ").workplane(offset=TB_X + 2.1).center(y, z + 4).rect(3.2, 3.2).extrude(3))
        t = t.cut(cq.Workplane("YZ").workplane(offset=TB_X - 5.1).center(y, z + 4).rect(3.2, 3.2).extrude(3))
        t = t.cut(cq.Workplane("XY").workplane(offset=z + 10).center(TB_X, y).circle(1.4).extrude(3))
    return t


def sweep_circle(pts, r):
    path = cq.Workplane("XY").spline([cq.Vector(*p) for p in pts], includeCurrent=False)
    p0, p1 = cq.Vector(*pts[0]), cq.Vector(*pts[1])
    d = (p1 - p0).normalized()
    xd = d.cross(cq.Vector(0, 0, 1)) if abs(d.z) < 0.9 else cq.Vector(1, 0, 0)
    plane = cq.Plane(origin=p0, xDir=xd.normalized(), normal=d)
    return cq.Workplane(plane).circle(r).sweep(path, isFrenet=False)


def polar(r, a_deg, z):
    a = math.radians(a_deg)
    return (r * math.cos(a), r * math.sin(a), z)


def power_cable():
    a = GLAND_ANGLES[0]
    return sweep_circle([polar(BODY_OD / 2 + 70, a, GLAND_Z), polar(BODY_OD / 2 + 30, a, GLAND_Z),
                         polar(BODY_OD / 2 - 2, a, GLAND_Z), polar(ANCHOR_R - 4, a, GLAND_Z + 0.2)], 2.5)


def blank_plug():
    """Spare PG7 entry closed with a blanking plug (use for a remote probe or comms cable)."""
    a = GLAND_ANGLES[1]
    p = cq.Workplane("YZ").workplane(offset=BODY_OD / 2 + 2).center(0, GLAND_Z).circle(2.8).extrude(13)
    return p.rotate((0, 0, 0), (0, 0, 1), a)


def rtd_leads():
    """Class A PT100 3-wire leads: sheath top -> neck bore -> floor hole -> MAX31865 terminal."""
    z_sh = -NECK_FLANGE_T - GASKET_T
    zt = Z_MAX + MAX_T + 3.0
    xe = MAX_X0 + MAX_LX
    w = {}
    for i, (dy, c) in enumerate([(-1.2, "r"), (0.0, "r"), (1.2, "w")]):
        ty = -5.25 + (i + 1) * 3.5
        w[f"rtd_{i}"] = (sweep_circle([(0.0, dy, z_sh + 1), (0.0, dy, FLOOR_T + 2), (2.5, dy * 1.5, FLOOR_T + 9),
                                       (3.0, ty, zt + 2), (xe - 1.0, ty, zt)], 0.7), c)
    return w


def power_wires():
    """5 V pair: cable end -> terminal block -> through bulkhead grommet (to ESP32 carrier)."""
    a = GLAND_ANGLES[0]
    x0, y0, _ = polar(ANCHOR_R - 4.5, a, 0)
    w = {}
    for i, (dy, c) in enumerate([(-1.2, "k"), (1.2, "rd")]):
        ty = -5.0 + i * 10.0
        zt = FLOOR_T + PED_H + 4
        w[f"pwr_in_{i}"] = (sweep_circle([(x0, y0 + dy, GLAND_Z), (TB_X + 4, y0 * 0.55 + dy, zt + 5.0),
                                         (TB_X + 6.5, ty, zt), (TB_X + 3.5, ty, zt)], 0.8), c)
        w[f"pwr_up_{i}"] = (sweep_circle([(TB_X - 3.5, ty, zt), (TB_X - 8, ty, zt + 1), (TB_X - 12, ty, 30.0),
                                         (-8.0, -10.0 + dy, 38.0), (-20.0 + dy, 0.0, LOWER_H - 2.0)], 0.8), c)
    return w


def spi_harness():
    """7-core ribbon from MAX31865 header up through the grommet."""
    return sweep_circle([(MAX_X0 + 2.0, 0.0, Z_MAX + MAX_T + 0.5), (MAX_X0 + 2.0, 0.0, 32.0),
                         (-20.0, 0.0, 40.0), (-20.0, 0.0, LOWER_H + BULKHEAD_T + 4.0)], 1.6)


def rig_bracket():
    """Optional mounting mode B: 4 mm Al 6061 bracket clamped between hex and a 1/2 in NPT locknut."""
    z_top = -GASKET_T - NECK_FLANGE_T - NECK_L - HEX_H
    b = cq.Workplane("XY").workplane(offset=z_top - 4).rect(120, 64).extrude(4).edges("|Z").fillet(6)
    b = b.cut(cq.Workplane("XY").workplane(offset=z_top - 5).circle(21.8 / 2).extrude(6))
    for sx in (-1, 1):
        for sy in (-1, 1):
            b = b.cut(cq.Workplane("XY").workplane(offset=z_top - 5).center(sx * 48, sy * 22)
                      .slot2D(11, 5.5, angle=0).extrude(6))
    nut = cq.Workplane("XY").workplane(offset=z_top - 4 - 5).polygon(8, 31).extrude(5) \
        .cut(cq.Workplane("XY").workplane(offset=z_top - 10).circle(21.4 / 2).extrude(7))
    return b, nut


# ---------------- PG7 cable glands ----------------
def gland(angle):
    g = cq.Workplane("YZ").polygon(6, 17.3).extrude(5.0)               # body hex 15 AF
    g = g.union(cq.Workplane("YZ").workplane(offset=5).circle(7.5).extrude(9.0)
                .faces(">X").edges().fillet(3.0))                       # dome cap
    g = g.cut(cq.Workplane("YZ").circle(2.8).extrude(20))              # cable bore
    inner = (cq.Workplane("YZ").workplane(offset=-8)
             .circle(12.5 / 2 - 0.1).extrude(8))                        # PG7 thread spigot, 8 mm
    inner = inner.cut(cq.Workplane("YZ").workplane(offset=-8).circle(2.8).extrude(8))
    g = g.union(inner)
    locknut = (cq.Workplane("YZ").workplane(offset=-8)
               .polygon(6, 17.3).extrude(3.0)
               .cut(cq.Workplane("YZ").workplane(offset=-8).circle(12.5 / 2).extrude(3)))
    g = g.translate((BODY_OD / 2 + 3, 0, GLAND_Z))
    locknut = locknut.translate((BODY_OD / 2 + 3, 0, GLAND_Z))
    return (g.rotate((0, 0, 0), (0, 0, 1), angle),
            locknut.rotate((0, 0, 0), (0, 0, 1), angle))


# ---------------- O-rings ----------------
def oring(z_center):
    """O-ring shown in its installed state: squeezed to the 2.0 mm groove depth,
    cross-section area preserved (ellipse 2.0 tall x 3.51 wide in a 3.6 wide groove)."""
    b = GROOVE_DEPTH / 2
    a = (ORING_CS / 2) ** 2 / b
    r = ORING_MEAN_D / 2
    prof = cq.Workplane("XZ").center(r, 0).ellipse(a, b * 0.999)
    return prof.revolve(360, (-r, 0, 0), (-r, 1, 0)).translate((0, 0, z_center))


# ---------------- fasteners ----------------
def screws():
    top = LOWER_H + BULKHEAD_T + FLANGE_T - 4.5
    s = None
    for x, y in bolt_points():
        head = (cq.Workplane("XY").workplane(offset=top).center(x, y)
                .circle(3.5).extrude(4.0)
                .cut(cq.Workplane("XY").workplane(offset=top + 2).center(x, y)
                     .polygon(6, 3.5).extrude(2.1)))
        shank = (cq.Workplane("XY").workplane(offset=top - 20).center(x, y)
                 .circle(2.0).extrude(20))
        part = head.union(shank)
        s = part if s is None else s.union(part)
    return s


# ---------------- SS304 neck + process connection ----------------
def neck():
    # top flange (screwed to housing floor)
    n = (cq.Workplane("XY").workplane(offset=-NECK_FLANGE_T)
         .circle(NECK_FLANGE_D / 2).extrude(NECK_FLANGE_T))
    for i in range(3):
        a = math.radians(NECK_SCREW_START + i * 120)
        n = n.cut(cq.Workplane("XY").workplane(offset=-NECK_FLANGE_T)
                  .center(19 * math.cos(a), 19 * math.sin(a)).circle(1.65)
                  .extrude(NECK_FLANGE_T))
    # tube
    z_bot = -NECK_FLANGE_T - NECK_L
    n = n.union(cq.Workplane("XY").workplane(offset=z_bot)
                .circle(NECK_OD / 2).extrude(NECK_L))
    # cooling fins
    for i in range(N_FINS):
        zf = -NECK_FLANGE_T - 12 - i * 12
        n = n.union(cq.Workplane("XY").workplane(offset=zf)
                    .circle(FIN_D / 2).extrude(FIN_T))
    # hex
    n = n.union(cq.Workplane("XY").workplane(offset=z_bot - HEX_H)
                .polygon(6, HEX_AF / math.cos(math.radians(30))).extrude(HEX_H)
                .edges(">Z or <Z").chamfer(1.0))
    # 1/2"-14 NPT male thread (tapered 1:16 on diameter), modelled as crests
    z_t = z_bot - HEX_H - NPT_LEN
    root = (cq.Workplane("XY").workplane(offset=z_t)
            .circle(NPT_OD / 2 - 1.45 - NPT_LEN / 32).workplane(offset=NPT_LEN)
            .circle(NPT_OD / 2 - 1.45).loft())
    n = n.union(root)
    k = 0
    z = z_t + 0.3
    while z + NPT_PITCH * 0.5 < z_t + NPT_LEN:
        r_major = NPT_OD / 2 - (z_t + NPT_LEN - z) / 32
        crest = (cq.Workplane("XZ").center(r_major - 0.75, z)
                 .polyline([(-0.8, -NPT_PITCH * 0.45), (0.75, -0.08),
                            (0.75, 0.08), (-0.8, NPT_PITCH * 0.45)]).close()
                 .revolve(360, (-(r_major - 0.75), 0, 0), (-(r_major - 0.75), 1, 0)))
        n = n.union(crest)
        z += NPT_PITCH
        k += 1
    # bore
    n = n.cut(cq.Workplane("XY").workplane(offset=z_t - 1)
              .circle(NECK_ID / 2 - 2.0).extrude(-z_t + 2))
    n = n.cut(cq.Workplane("XY").workplane(offset=z_bot)
              .circle(NECK_ID / 2).extrude(NECK_L + NECK_FLANGE_T))
    return n.translate((0, 0, -GASKET_T))


def sheath():
    z_t = -NECK_FLANGE_T - NECK_L - HEX_H - NPT_LEN
    s = (cq.Workplane("XY").workplane(offset=z_t - SHEATH_L)
         .circle(SHEATH_D / 2).extrude(SHEATH_L + NPT_LEN + HEX_H + NECK_L))
    s = s.faces("<Z").edges().fillet(SHEATH_D / 2 - 0.05)
    # compression ferrule seat inside thread
    s = s.union(cq.Workplane("XY").workplane(offset=z_t)
                .circle(5.8).circle(SHEATH_D / 2).extrude(6))
    return s.translate((0, 0, -GASKET_T))


def neck_gasket():
    return (cq.Workplane("XY").circle(NECK_FLANGE_D / 2 - 3).circle(5.0)
            .extrude(GASKET_T).translate((0, 0, -GASKET_T)))


# ---------------- assembly ----------------
H_COL = (0.22, 0.24, 0.27)
PARTS = {
    "lower_housing": (lower_housing, H_COL, "Lower housing (terminal + front-end chamber), ASA FDM"),
    "upper_housing": (upper_housing, H_COL, "Upper housing (ESP32 chamber), ASA FDM"),
    "bulkhead": (bulkhead, (0.62, 0.64, 0.66), "Bulkhead, ASA FDM"),
    "grommet": (grommet, (0.05, 0.05, 0.05), "Silicone grommet, potted"),
    "oring_lower": (lambda: oring(LOWER_H - GROOVE_DEPTH / 2), (0.85, 0.30, 0.10), "O-ring 80 x 2.65 FKM"),
    "oring_upper": (lambda: oring(LOWER_H + BULKHEAD_T + GROOVE_DEPTH / 2), (0.85, 0.30, 0.10), "O-ring 80 x 2.65 FKM"),
    "carrier": (carrier, (0.80, 0.68, 0.40), "Round FR4 carrier D70"),
    "esp_headers": (esp_headers, (0.08, 0.08, 0.08), "2 x 19-way female header"),
    "esp32": (esp32, (0.10, 0.12, 0.14), "ESP32-DevKitC V4"),
    "esp32_parts": (esp32_parts, (0.72, 0.73, 0.75), "ESP32-WROOM-32E, USB, LDO"),
    "car_connector": (car_connector, (0.92, 0.92, 0.90), "JST-XH 8-way harness connector"),
    "sub_carrier": (sub_carrier, (0.80, 0.68, 0.40), "FR4 sub-carrier 30 x 30"),
    "max31865": (max31865, (0.15, 0.20, 0.55), "MAX31865 breakout"),
    "max_parts": (max_parts, (0.10, 0.10, 0.10), "MAX31865 IC, Rref, header"),
    "max_terminal": (max_terminal, (0.10, 0.45, 0.78), "4-way 3.5 mm RTD terminal"),
    "terminal_block": (terminal_block, (0.62, 0.64, 0.68), "3-way terminal block (5 V in)"),
    "screws": (screws, (0.55, 0.57, 0.60), "4 x M4 A2-70 SHCS"),
    "vent": (vent, (0.90, 0.90, 0.92), "M12 ePTFE vent"),
    "light_pipe": (light_pipe, (0.60, 0.85, 1.00), "PC light pipe"),
    "neck": (neck, (0.72, 0.74, 0.77), "SS304 finned neck + 1/2 NPT"),
    "neck_gasket": (neck_gasket, (0.05, 0.05, 0.05), "FKM flange gasket"),
    "sheath": (sheath, (0.80, 0.82, 0.85), "Class A PT100, 6 mm SS sheath"),
    "power_cable": (power_cable, (0.12, 0.12, 0.13), "2-core 0.5 mm2 power cable"),
    "blank_plug": (blank_plug, (0.07, 0.07, 0.08), "PG7 blanking plug"),
    "spi_harness": (spi_harness, (0.85, 0.85, 0.85), "8-core harness (SPI, 3V3/5V, GND)"),
}
for i, a in enumerate(GLAND_ANGLES):
    PARTS[f"gland_{i}"] = ((lambda a=a: gland(a)[0]), (0.08, 0.08, 0.08), "PG7 nylon gland IP68")
    PARTS[f"locknut_{i}"] = ((lambda a=a: gland(a)[1]), (0.08, 0.08, 0.08), "PG7 locknut")
_WC = {"r": (0.80, 0.10, 0.10), "w": (0.95, 0.95, 0.95), "k": (0.05, 0.05, 0.05), "rd": (0.85, 0.12, 0.10)}
for _k, (_shp, _c) in {**rtd_leads(), **power_wires()}.items():
    PARTS["wire_" + _k] = ((lambda s_=_shp: s_), _WC[_c], "0.5 mm2 core")


def explode_offset(name):
    off = {
        "neck": (0, 0, -55), "neck_gasket": (0, 0, -28), "sheath": (0, 0, -95),
        "lower_housing": (0, 0, 0), "terminal_block": (0, 0, 0),
        "sub_carrier": (0, 0, 0), "max31865": (0, 0, 0), "max_parts": (0, 0, 0), "max_terminal": (0, 0, 0),
        "oring_lower": (0, 0, 30), "bulkhead": (0, 0, 55), "grommet": (0, 0, 55),
        "oring_upper": (0, 0, 80), "carrier": (0, 0, 95), "car_connector": (0, 0, 95),
        "esp_headers": (0, 0, 105), "esp32": (0, 0, 118), "esp32_parts": (0, 0, 118),
        "upper_housing": (0, 0, 165), "vent": (0, 0, 200), "light_pipe": (0, 0, 188), "screws": (0, 0, 230),
    }
    if name.startswith(("gland", "locknut", "blank_plug", "power_cable")):
        i = 1 if name.endswith("1") or name == "blank_plug" else 0
        a = math.radians(GLAND_ANGLES[i])
        d = -10 if name.startswith("locknut") else 32
        return (d * math.cos(a), d * math.sin(a), 0)
    if name.startswith(("wire_", "spi_")):
        return None
    return off.get(name, (0, 0, 0))
