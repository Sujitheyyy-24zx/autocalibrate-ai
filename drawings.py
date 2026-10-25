"""Dimensioned 2D drawings from the R1 B-rep (hidden-line removal + section hatching)."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.backends.backend_pdf import PdfPages
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.BRepLib import BRepLib
from OCP.BRepTools import BRepTools_WireExplorer
from OCP.TopAbs import TopAbs_REVERSED
import r1c as r1

OUT = "/home/claude/cad_r1b/out"
LW, LWH, LWD = 0.55, 0.3, 0.35
INK = "black"


def solid(fn):
    w = fn()
    v = w.vals()
    return v[0] if len(v) == 1 else cq.Compound.makeCompound(v)


def hlr(shape, view):
    d, x = {"front": ((0, -1, 0), (1, 0, 0)), "top": ((0, 0, 1), (1, 0, 0)),
            "side": ((1, 0, 0), (0, 1, 0))}[view]
    algo = HLRBRep_Algo(); algo.Add(shape.wrapped)
    algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*d), gp_Dir(*x))))
    algo.Update(); algo.Hide()
    h = HLRBRep_HLRToShape(algo)
    res = {"vis": [], "hid": []}
    for key, comps in (("vis", [h.VCompound(), h.OutLineVCompound()]), ("hid", [h.HCompound()])):
        for c in comps:
            if c.IsNull():
                continue
            BRepLib.BuildCurves3d_s(c, 1e-6)
            for e in cq.Shape.cast(c).Edges():
                n = 2 if e.geomType() == "LINE" else 40
                pts = np.array([[p.x, p.y] for p in e.positions(np.linspace(0, 1, n))])
                res[key].append(pts)
    return res


def draw_hlr(ax, res, dx=0, dy=0, hidden=True):
    for p in res["vis"]:
        ax.plot(p[:, 0] + dx, p[:, 1] + dy, color=INK, lw=LW, solid_capstyle="round")
    if hidden:
        for p in res["hid"]:
            ax.plot(p[:, 0] + dx, p[:, 1] + dy, color=INK, lw=LWH, ls=(0, (3, 2)))


def section(shape, plane="XZ", offset=0.0):
    """Cut shape at y = offset (XZ) and return (hlr of remaining back half, hatched section faces in 2D)."""
    box = cq.Solid.makeBox(1000, 500, 1000, pnt=cq.Vector(-500, offset - 500, -500))
    back = shape.cut(box)
    face = cq.Face.makePlane(1000, 1000, basePnt=cq.Vector(0, offset, 0), dir=cq.Vector(0, 1, 0))
    sec = shape.intersect(face)
    polys = []
    for f in sec.Faces():
        loops = [f.outerWire()] + f.innerWires()
        verts, codes = [], []
        for wire in loops:
            pts = []
            exp = BRepTools_WireExplorer(wire.wrapped)
            while exp.More():
                e = cq.Edge(exp.Current())
                n = 2 if e.geomType() == "LINE" else 24
                ps = [(p.x, p.z) for p in e.positions(np.linspace(0, 1, n))]
                if exp.Current().Orientation() == TopAbs_REVERSED:
                    ps = ps[::-1]
                pts += ps
                exp.Next()
            verts += pts + [pts[0]]
            codes += [Path.MOVETO] + [Path.LINETO] * (len(pts) - 1) + [Path.CLOSEPOLY]
        polys.append(Path(verts, codes))
    return hlr(back, "front"), polys


def draw_section(ax, sec, dx=0, dy=0, hatch="////"):
    res, polys = sec
    draw_hlr(ax, res, dx, dy, hidden=False)
    for pth in polys:
        v = pth.vertices + [dx, dy]
        ax.add_patch(PathPatch(Path(v, pth.codes), facecolor="white", edgecolor=INK, lw=LW, hatch=hatch))


# ---------------- dimensions ----------------
plt.rcParams["hatch.linewidth"] = 0.35
FS = 6.2


def dim_h(ax, x1, x2, y, yref1, yref2, text, above=True):
    for x, yr in ((x1, yref1), (x2, yref2)):
        ax.plot([x, x], [yr + (1 if y > yr else -1) * 1.0, y + (1.5 if y > yr else -1.5)], color=INK, lw=0.25)
    ax.annotate("", xy=(x1, y), xytext=(x2, y), arrowprops=dict(arrowstyle="<|-|>", lw=0.35, color=INK,
                                                                 mutation_scale=5, shrinkA=0, shrinkB=0))
    ax.text((x1 + x2) / 2, y + (1.0 if above else -1.0), text, ha="center", va="bottom" if above else "top",
            fontsize=FS, color=INK)


def dim_v(ax, y1, y2, x, xref1, xref2, text, left=True):
    for y, xr in ((y1, xref1), (y2, xref2)):
        ax.plot([xr + (1 if x > xr else -1) * 1.0, x + (1.5 if x > xr else -1.5)], [y, y], color=INK, lw=0.25)
    ax.annotate("", xy=(x, y1), xytext=(x, y2), arrowprops=dict(arrowstyle="<|-|>", lw=0.35, color=INK,
                                                                 mutation_scale=5, shrinkA=0, shrinkB=0))
    ax.text(x + (-1.0 if left else 1.0), (y1 + y2) / 2, text, ha="right" if left else "left", va="center",
            fontsize=FS, color=INK, rotation=90 if len(text) > 7 else 0)


def leader(ax, xy, xytext, text, ha="left"):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=FS, color=INK, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-|>", lw=0.3, color=INK, mutation_scale=5, shrinkA=1, shrinkB=0))


def centre(ax, x1, x2, y, vertical=False):
    if vertical:
        ax.plot([y, y], [x1, x2], color=INK, lw=0.25, ls=(0, (8, 2, 1.5, 2)))
    else:
        ax.plot([x1, x2], [y, y], color=INK, lw=0.25, ls=(0, (8, 2, 1.5, 2)))


def sheet(title, number, scale_note):
    fig = plt.figure(figsize=(16.54, 11.69))  # A3 landscape
    ax = fig.add_axes([0.03, 0.10, 0.94, 0.86])
    ax.set_aspect("equal"); ax.axis("off")
    fig.patches.append(plt.Rectangle((0.015, 0.015), 0.97, 0.97, transform=fig.transFigure, fill=False, lw=1.0, color=INK))
    tb = fig.add_axes([0.58, 0.02, 0.40, 0.075]); tb.axis("off")
    tb.add_patch(plt.Rectangle((0, 0), 1, 1, fill=False, lw=0.8, color=INK, transform=tb.transAxes))
    for xv in (0.55, 0.78):
        tb.plot([xv, xv], [0, 1], color=INK, lw=0.5, transform=tb.transAxes)
    tb.plot([0, 1], [0.5, 0.5], color=INK, lw=0.5, transform=tb.transAxes)
    tb.text(0.01, 0.75, "AutoCalibrate AI - PT100 node R1 (from R0)", fontsize=8.5, va="center", weight="bold", transform=tb.transAxes)
    tb.text(0.01, 0.25, title, fontsize=9, va="center", transform=tb.transAxes)
    tb.text(0.56, 0.75, "Units: mm   " + scale_note, fontsize=7.5, va="center", transform=tb.transAxes)
    tb.text(0.56, 0.25, "Tol: FDM +/-0.3, metal ISO 2768-m", fontsize=6.0, va="center", transform=tb.transAxes)
    tb.text(0.79, 0.75, f"Sheet {number}", fontsize=8.5, va="center", transform=tb.transAxes)
    tb.text(0.79, 0.25, "R1 prelim. 25 Oct 2026", fontsize=6.8, va="center", transform=tb.transAxes)
    return fig, ax


def frame(ax, x0, x1, yc):
    """Set limits with equal aspect filling the drawing area (axes ratio ~1.54)."""
    r = (x1 - x0) / 1.54
    ax.set_xlim(x0, x1); ax.set_ylim(yc - r / 2, yc + r / 2)


def notes(fig, lines, x=0.03, y=0.095):
    fig.text(x, y, "NOTES\n" + "\n".join(lines), fontsize=7.2, va="top", family="DejaVu Sans")


print("building solids ...")
S = {n: solid(fn) for n, (fn, _, _) in r1.PARTS.items() if not n.startswith(("wire_", "spi_", "power_cable"))}
assy_names = [n for n in S if n not in ("blank_plug",)]
ASSY = cq.Compound.makeCompound([S[n] for n in assy_names])
pdf = PdfPages(f"{OUT}/R1_drawings.pdf")
Z_TOP = r1.LOWER_H + r1.BULKHEAD_T + r1.UPPER_H
Z_TIP = -194.0

# ---------------- Sheet 1: general arrangement ----------------
fig, ax = sheet("General arrangement: front, top and side views", "1 / 4", "Not to scale - A3")
front = hlr(ASSY, "front")
draw_hlr(ax, front, 0, 0, hidden=False)
centre(ax, Z_TIP - 8, Z_TOP + 14, 0, vertical=True)
dim_v(ax, 0, Z_TOP, -75, -44, -44, f"{Z_TOP:.0f}")
dim_v(ax, Z_TOP, Z_TOP + 6, 30, 30, 30, "6 vent", left=False)
dim_v(ax, -r1.GASKET_T - r1.NECK_FLANGE_T - r1.NECK_L - r1.HEX_H, 0, -75, -15, -25, "75 (neck + flange to hex)")
dim_v(ax, Z_TIP, 0, -100, -3, -44, "194 housing base to sensing tip")
dim_v(ax, -94.5, -75.0, 22, 11, 14, "19 NPT", left=False)
dim_h(ax, -r1.FLANGE_OD / 2, r1.FLANGE_OD / 2, Z_TOP + 20, r1.LOWER_H + r1.BULKHEAD_T + r1.FLANGE_T, r1.LOWER_H + r1.BULKHEAD_T + r1.FLANGE_T, "D108 flanges")
dim_h(ax, -r1.BODY_OD / 2, r1.BODY_OD / 2, Z_TOP + 12, Z_TOP - 6, Z_TOP - 6, "D88 body")
dim_v(ax, 0, r1.LOWER_H, 64, 44, 54, "45 lower", left=False)
dim_v(ax, r1.LOWER_H + r1.BULKHEAD_T, Z_TOP, 64, 54, 44, "50 upper", left=False)
leader(ax, (r1.FIN_D / 2, -30), (40, -30), "4 fins D40 x 1.5, pitch 12")
leader(ax, (r1.HEX_AF / 2, -80), (40, -80), "Hex 27 AF")
leader(ax, (3, -150), (25, -150), "PT100 sheath D6 SS316/304")
leader(ax, (r1.FLANGE_OD / 2, r1.LOWER_H + 2), (70, 70), "Bulkhead 4 thk, clamped by 4 x M4")
# top view
DXT = 240
top = hlr(cq.Compound.makeCompound([S[n] for n in assy_names if n not in ("sheath",)]), "top")
draw_hlr(ax, top, DXT, 0, hidden=False)
centre(ax, DXT - 62, DXT + 62, 0); centre(ax, -62, 62, DXT, vertical=True)
for a in r1.GLAND_ANGLES:
    ax.plot([DXT, DXT + 70 * math.cos(math.radians(a))], [0, 70 * math.sin(math.radians(a))], color=INK, lw=0.25, ls=(0, (8, 2, 1.5, 2)))
ax.text(DXT + 58, 52, "PG7 glands at +/-35 deg\n(-35: power, +35: spare, blanked)", fontsize=FS)
ax.text(DXT - 60, -66, "4 x M4 on PCD 98 at 0/90/180/270 deg", fontsize=FS)
ax.text(DXT - 60, 62, "Vent M12 at X+22, light pipe D5 at X-22", fontsize=FS)
ax.text(DXT - 20, 80, "TOP VIEW", fontsize=8, weight="bold")
ax.text(-20, Z_TOP + 32, "FRONT VIEW", fontsize=8, weight="bold")
# side view (from +X)
DXS = 400
side = hlr(ASSY, "side")
draw_hlr(ax, side, DXS, 0, hidden=False)
centre(ax, Z_TIP - 8, Z_TOP + 14, DXS, vertical=True)
dim_v(ax, 0, r1.GLAND_Z, DXS - 70, DXS - 42, DXS - 42, "22")
ax.text(DXS - 25, Z_TOP + 32, "SIDE VIEW (from +X)", fontsize=8, weight="bold")
frame(ax, -150, 480, -38)
notes(fig, ["1. Housing parts FDM ASA (PETG acceptable for processes <= 100 C); neck SS304; sheath per probe supplier.",
            "2. Assembly is the R0 IP65_PT100_Enclosure geometry with the R1 changes listed in the report (boards, gland clocking, anchors).",
            "3. IP65 is a design intent only - not claimed until tested to IEC 60529 (see validation plan)."])
pdf.savefig(fig); fig.savefig(f"{OUT}/dwg_1_GA.png", dpi=110); plt.close(fig)

# ---------------- Sheet 2: lower housing ----------------
fig, ax = sheet("Lower housing (terminal + front-end chamber) - ASA, FDM", "2 / 4", "Not to scale - A3")
LH = S["lower_housing"]
t = hlr(LH, "top")
draw_hlr(ax, t, 0, 0, hidden=False)
centre(ax, -62, 62, 0); centre(ax, -62, 62, 0, vertical=True)
th = np.linspace(0, 2 * np.pi, 200)
ax.plot(49 * np.cos(th), 49 * np.sin(th), color=INK, lw=0.25, ls=(0, (8, 2, 1.5, 2)))
ax.plot(19 * np.cos(th), 19 * np.sin(th), color=INK, lw=0.25, ls=(0, (8, 2, 1.5, 2)))
leader(ax, (49, 0), (66, 14), "4 x D5.6 x 14 deep, M4 heat-set\ninserts, PCD 98, 0/90/180/270")
leader(ax, r1.polar(19, 150, 0)[:2], (-80, 30), "3 x D4.5 thru, PCD 38, at 30/150/270\n(M4 to neck flange)", ha="right")
leader(ax, (0, -4), (-80, -8), "D8 thru (RTD leads)", ha="right")
hx = r1.sub_holes()[0]
leader(ax, hx, (-80, -30), "4 x D7 standoffs, D4.0 x 6 for M3 inserts\nat X -29.5 / -6.5, Y +/-11.5 (sub-carrier)", ha="right")
leader(ax, (r1.TB_X, 7.5), (66, -22), "Pedestal 12 x 19 x 5, 2 x D4.0 at Y +/-7.5")
leader(ax, r1.polar(r1.ANCHOR_R, -35, 0)[:2], (66, -40), "Anchor posts 5 x 10, tie slot 2.2 x 12\non gland axes, r 29")
leader(ax, (r1.GROOVE_OD / 2 - 1, 30), (66, 40), "O-ring groove D78 / D85.2, 2.0 deep\n(3.6 wide) in top face")
ax.text(-20, 66, "TOP VIEW", fontsize=8, weight="bold")
# section A-A through X axis
DX = 205
sec = section(LH, offset=0.0)
draw_section(ax, sec, DX, 5)
Y0 = 5
centre(ax, Y0 - 8, Y0 + 55, DX, vertical=True)
dim_v(ax, Y0, Y0 + r1.LOWER_H, DX - 66, DX - 44, DX - 54, "45")
dim_v(ax, Y0, Y0 + r1.FLOOR_T, DX - 50, DX - 37, DX - 37, "6")
dim_v(ax, Y0 + r1.LOWER_H - r1.FLANGE_T, Y0 + r1.LOWER_H, DX + 62, DX + 54, DX + 54, "8", left=False)
dim_v(ax, Y0 + r1.LOWER_H - r1.GROOVE_DEPTH, Y0 + r1.LOWER_H, DX + 72, DX + 44, DX + 44, "2.0 groove", left=False)
dim_h(ax, DX - r1.BODY_ID / 2, DX + r1.BODY_ID / 2, Y0 - 10, Y0 + r1.FLOOR_T, Y0 + r1.FLOOR_T, "D74 bore", above=False)
dim_h(ax, DX - r1.BODY_OD / 2, DX + r1.BODY_OD / 2, Y0 - 19, Y0, Y0, "D88", above=False)
dim_h(ax, DX - r1.FLANGE_OD / 2, DX + r1.FLANGE_OD / 2, Y0 + 54, Y0 + r1.LOWER_H, Y0 + r1.LOWER_H, "D108")
ax.text(DX - 30, Y0 + 66, "SECTION A-A (XZ plane)", fontsize=8, weight="bold")
# gland detail (section through gland axis, rotated into XZ)
LHr = LH.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 35)
secg = section(LHr, offset=0.0)
YG = -85
draw_section(ax, secg, DX, YG)
leader(ax, (DX + 44 + 2, YG + r1.GLAND_Z), (DX + 66, YG + 30), "PG7 hole D12.7, axis Z22\nouter pad 22 x 22\nlocal wall 5 mm\ninner spot-face D21 (locknut)")
dim_v(ax, YG, YG + r1.GLAND_Z, DX - 66, DX - 44, DX + 40, "22")
ax.text(DX - 40, YG + 62, "SECTION B-B (through gland axis, -35 deg)", fontsize=8, weight="bold")
frame(ax, -140, 330, -25)
notes(fig, ["1. Print open side up, 0.2 mm layers, >= 6 perimeters (walls fully solid), 40 % infill elsewhere, no supports except gland pads.",
            "2. Groove faces: print last layers at 0.1 mm; check groove depth 2.0 +0.1/-0 with depth gauge; lightly sand land to Ra <= 3.2.",
            "3. Insert holes D5.6 (M4 x 8.1 inserts) and D4.0 (M3 x 5.7 inserts) - press at 220-240 C with insert tip."])
pdf.savefig(fig); fig.savefig(f"{OUT}/dwg_2_lower.png", dpi=110); plt.close(fig)

# ---------------- Sheet 3: upper housing + bulkhead ----------------
fig, ax = sheet("Upper housing (ESP32 chamber) and bulkhead - ASA, FDM", "3 / 4", "Not to scale - A3")
UH, BH = S["upper_housing"], S["bulkhead"]
z0 = r1.LOWER_H + r1.BULKHEAD_T
secu = section(UH.translate(cq.Vector(0, 0, -z0)), offset=0.0)
draw_section(ax, secu, 0, 0)
centre(ax, -10, 62, 0, vertical=True)
dim_v(ax, 0, r1.UPPER_H, -66, -44, -54, "50")
dim_v(ax, r1.UPPER_H - r1.ROOF_T, r1.UPPER_H, -50, -30, -30, "5")
dim_v(ax, 0, r1.FLANGE_T, 62, 54, 54, "8", left=False)
leader(ax, (22, r1.UPPER_H), (40, 62), "D12 thru, M12x1.5 ePTFE vent at X+22")
leader(ax, (-22, r1.UPPER_H), (-40, 62), "D5 thru, light pipe at X-22", ha="right")
leader(ax, (49, r1.FLANGE_T), (70, 18), "4 x D4.6 thru, C'bore D8 x 4.5\nPCD 98 (M4 SHCS)")
leader(ax, (r1.GROOVE_ID / 2 + 1.8, 0.5), (70, 2), "Groove D78 / D85.2 x 2.0 deep\nin mating face")
leader(ax, (r1.BODY_OD / 2 - 2, r1.UPPER_H - 2), (70, 40), "R6 top edge")
ax.text(-30, 72, "UPPER HOUSING - SECTION C-C", fontsize=8, weight="bold")
# bulkhead top view
DXB = 220
bt = hlr(BH, "top")
draw_hlr(ax, bt, DXB, 25, hidden=False)
centre(ax, 25 - 60, 25 + 60, DXB, vertical=True); centre(ax, DXB - 60, DXB + 60, 25)
ax.plot(DXB + 30 * np.cos(th), 25 + 30 * np.sin(th), color=INK, lw=0.25, ls=(0, (8, 2, 1.5, 2)))
leader(ax, (DXB - 20, 25), (DXB - 80, 70), "D10 thru at X-20: potted grommet\n(SPI + 5 V harness)", ha="right")
leader(ax, (DXB + 21.2, 25 + 21.2), (DXB + 50, 72), "4 x standoff D7 x 8 high,\nD4.0 bore, M3 inserts,\non R30 at 45 deg")
leader(ax, (DXB + 49, 25), (DXB + 62, 0), "4 x D4.6 thru, PCD 98")
dim_h(ax, DXB - r1.FLANGE_OD / 2, DXB + r1.FLANGE_OD / 2, 25 - 66, 25 - 30, 25 - 30, "D108 x 4 thk", above=False)
ax.text(DXB - 25, 85, "BULKHEAD - TOP VIEW", fontsize=8, weight="bold")
frame(ax, -110, 310, 25)
notes(fig, ["1. Upper housing prints roof-down on a raft or roof-up with tree supports inside; vent and light-pipe holes drilled to size.",
            "2. Bulkhead prints flat; seal the grommet with silicone RTV or 2-part epoxy after the harness is fitted.",
            "3. Keep metal (inserts, screws) >= 15 mm from the ESP32 antenna end (+X)."])
pdf.savefig(fig); fig.savefig(f"{OUT}/dwg_3_upper.png", dpi=110); plt.close(fig)

# ---------------- Sheet 4: carriers, neck, bracket ----------------
fig, ax = sheet("Electronics carriers (board layout), SS304 neck, rig bracket", "4 / 4", "Not to scale - A3")
# ESP carrier top
car = cq.Compound.makeCompound([S["carrier"], S["esp32"], S["esp_headers"], S["esp32_parts"]])
draw_hlr(ax, hlr(car, "top"), 0, 30, hidden=False)
centre(ax, -40, 40, 30); centre(ax, -10, 70, 0, vertical=True)
leader(ax, (21.2, 51.2), (40, 72), "4 x D3.2 on R30 at 45 deg (M3 x 6)")
dim_h(ax, -27, 27, 30 - 42, 30 - 14, 30 - 14, "54 ESP32-DevKitC (measure)", above=False)
dim_v(ax, 30 - 14, 30 + 14, -48, -30, -30, "28")
leader(ax, (25, 30), (45, 40), "Antenna end (+X)")
leader(ax, (-25, 30), (-45, 46), "USB (-X)", ha="right")
ax.text(-30, 80, "ESP32 CARRIER D70 x 1.6 FR4", fontsize=8, weight="bold")
# sub-carrier
sub = cq.Compound.makeCompound([S["sub_carrier"], S["max31865"], S["max_terminal"]])
DXS = 110
draw_hlr(ax, hlr(sub.translate(cq.Vector(-r1.SUB_X, 0, 0)), "top"), DXS, 30, hidden=False)
dim_h(ax, DXS - 15, DXS + 15, 30 - 22, 30 - 15, 30 - 15, "30", above=False)
dim_v(ax, 30 - 15, 30 + 15, DXS - 24, DXS - 15, DXS - 15, "30")
leader(ax, (DXS - 11.5, 30 + 11.5), (DXS - 10, 62), "4 x D3.2, 23 x 23 pitch")
leader(ax, (DXS + 11, 30), (DXS + 26, 45), "RTD terminal faces +X")
ax.text(DXS - 25, 80, "MAX31865 SUB-CARRIER", fontsize=8, weight="bold")
# neck section
DXN = 220
secn = section(S["neck"].translate(cq.Vector(0, 0, r1.GASKET_T)), offset=0.0)
draw_section(ax, secn, DXN, 60, hatch="xxxx")
dim_h(ax, DXN - 25, DXN + 25, 66, 60, 60, "D50 x 4 flange")
dim_v(ax, 60 - r1.NECK_FLANGE_T - r1.NECK_L, 60 - r1.NECK_FLANGE_T, DXN - 34, DXN - 11, DXN - 11, "60")
dim_v(ax, 60 - 93.5, 60 - 74.5, DXN - 34, DXN - 11, DXN - 11, "19")
leader(ax, (DXN + 10.65, 60 - 30), (DXN + 30, 60 - 20), "Tube D21.3 x 2.77 wall\n(1/2\" Sch 10S, SS304)")
leader(ax, (DXN + 20, 60 - 16), (DXN + 30, 60 - 5), "4 fins D40 x 1.5, pitch 12\n(laser-cut, brazed or press-fit)")
leader(ax, (DXN + 13.5, 60 - 70), (DXN + 30, 60 - 62), "Hex 27 AF x 10")
leader(ax, (DXN + 10.6, 60 - 85), (DXN + 30, 60 - 82), "1/2\"-14 NPT male, 19 long")
leader(ax, (DXN + 19, 60 - 2), (DXN + 30, 70), "3 x M4 tapped, PCD 38")
ax.text(DXN - 20, 82, "SS304 NECK - SECTION", fontsize=8, weight="bold")
# bracket
DXK = 340
b, nut = r1.rig_bracket()
draw_hlr(ax, hlr(b.val().translate(cq.Vector(0, 0, 79)), "top"), DXK, 30, hidden=False)
dim_h(ax, DXK - 60, DXK + 60, 30 - 40, 30 - 32, 30 - 32, "120", above=False)
dim_v(ax, 30 - 32, 30 + 32, DXK - 70, DXK - 60, DXK - 60, "64")
leader(ax, (DXK, 30 + 10.9), (DXK - 10, 74), "D21.8 thru")
leader(ax, (DXK + 48, 30 + 22), (DXK + 30, 74), "4 x slot 11 x 5.5, at X+/-48, Y+/-22")
ax.text(DXK - 40, 84, "RIG BRACKET (mode B) 4 mm Al 6061", fontsize=8, weight="bold")
frame(ax, -60, 410, 25)
notes(fig, ["1. Board sizes are datasheet/vendor values (ESP32-DevKitC ~54 x 28; Adafruit 3328 28.0 x 25.5): measure your boards and edit r1c.py.",
            "2. Neck can be fabricated from a 1/2\" NPT SS304 hex nipple + 1/2\" Sch 10S tube + laser-cut flange (TIG welded), fins optional.",
            "3. Bracket: laser or hand-cut 4 mm Al 6061-T6, deburr; locknut 1/2\" NPT (conduit) steel, zinc plated."])
pdf.savefig(fig); fig.savefig(f"{OUT}/dwg_4_parts.png", dpi=110); plt.close(fig)
pdf.close()
print("drawings done")
