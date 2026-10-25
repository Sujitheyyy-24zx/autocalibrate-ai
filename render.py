import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pyvista as pv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import r1c as r1

OUT = "/home/claude/cad_r1b/out"
STL = OUT + "/stl"
META = {n: (c, d) for n, (_, c, d) in r1.PARTS.items()}
METAL = {"screws", "esp32_parts", "neck", "sheath"}
only = sys.argv[1:] or ["iso", "lower", "upper", "cutaway", "exploded", "mount"]

_cache = {}


SHORT = {"v": False}


def load(name, offset=(0, 0, 0)):
    key = (name, SHORT["v"])
    if key not in _cache:
        m = pv.read(f"{STL}/{name}.stl").clean()
        if SHORT["v"] and name == "power_cable":
            m = m.clip(normal=(1, -0.7, 0), origin=(70, -49, 0), invert=True).extract_surface(algorithm="dataset_surface")
        _cache[key] = m.compute_normals(feature_angle=30, split_vertices=True)
    return _cache[key].translate(offset, inplace=False)


def plotter(w, h):
    p = pv.Plotter(off_screen=True, window_size=(w, h), lighting="none")
    p.set_background("white")
    p.add_light(pv.Light(position=(250, -350, 450), intensity=0.85, light_type="scene light"))
    p.add_light(pv.Light(position=(-400, -100, 200), intensity=0.35, light_type="scene light"))
    p.add_light(pv.Light(position=(100, 300, -200), intensity=0.25, light_type="scene light"))
    p.add_light(pv.Light(light_type="headlight", intensity=0.25))
    p.enable_anti_aliasing("ssaa")
    return p


def add(p, mesh, name, opacity=1.0, color=None):
    col = color or META[name][0]
    metal = name in METAL
    p.add_mesh(mesh, color=col, smooth_shading=True, opacity=opacity,
               specular=0.7 if metal else 0.22, specular_power=40 if metal else 12,
               ambient=0.20, diffuse=0.85)


def safe_add(p, mesh, name):
    m = mesh.extract_surface(algorithm="dataset_surface") if not isinstance(mesh, pv.PolyData) else mesh
    m = m.triangulate()
    if m.n_cells == 0 or m.n_faces_strict == 0:
        return
    add(p, m.compute_normals(feature_angle=30, split_vertices=True), name)


def camera(p, focal, direction, dist, up=(0, 0, 1), angle=22):
    d = np.array(direction, float); d /= np.linalg.norm(d)
    p.camera.focal_point = focal
    p.camera.position = tuple(np.array(focal) + d * dist)
    p.camera.up = up
    p.camera.view_angle = angle


def to_px(p, pt, h):
    r = p.renderer
    r.SetWorldPoint(*pt, 1.0); r.WorldToDisplay()
    x, y, _ = r.GetDisplayPoint()
    return x, h - y


def annotate(raw, anchors, out, W, H, fs=None, margin=470):
    """Labels in clean side columns (outside the model), leader lines to anchor points."""
    img = plt.imread(raw)
    fs = fs or W / 95
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(img); ax.axis("off")
    ax.set_xlim(0, W); ax.set_ylim(H, 0)
    lh = fs * 1.75
    for side in ("L", "R"):
        items = sorted([a for a in anchors if a[2] == side], key=lambda a: a[0][1])
        if not items:
            continue
        heights = [(t.count("\n") + 1) * lh + 22 for _, t, _ in items]
        ys, last = [], 30
        for ((x, y), _, _), h in zip(items, heights):
            yy = max(y - h / 2 + lh / 2, last); ys.append(yy); last = yy + h
        over = last - (H - 20)
        if over > 0:
            ys = [v - over for v in ys]
            for i in range(1, len(ys)):
                ys[i] = max(ys[i], ys[i - 1] + heights[i - 1])
        for ((x, y), text, _), yy in zip(items, ys):
            tx = 30 if side == "L" else W - 30
            edge = margin if side == "L" else W - margin
            ly = yy + (text.count("\n") + 1) * lh / 2
            ax.plot([x, edge, edge + (-14 if side == "L" else 14)], [y, ly, ly], color="#c2410c", lw=1.6)
            ax.plot([x], [y], "o", color="#c2410c", ms=6.5, mec="white", mew=1.1)
            ax.text(edge + (-22 if side == "L" else 22), ly, text, ha="right" if side == "L" else "left",
                    va="center", fontsize=fs, color="#111111", linespacing=1.3)
    fig.savefig(out, dpi=100); plt.close(fig)



ALL = list(META)
Z_UP = r1.LOWER_H + r1.BULKHEAD_T
SHORT["v"] = True


def clip_y(p, names, sec_y=0.0, closed=("lower_housing", "upper_housing", "bulkhead", "neck", "sheath", "carrier",
                                       "sub_carrier", "esp32", "neck_gasket", "grommet", "oring_lower", "oring_upper")):
    for n in names:
        m = load(n)
        if m.bounds[3] < sec_y - 0.01:
            continue
        if m.bounds[2] >= sec_y:
            add(p, m, n); continue
        c = None
        if n in closed:
            try:
                c = m.clip_closed_surface(normal=(0, -1, 0), origin=(0, sec_y, 0))
                if c.n_points == 0:
                    c = None
            except Exception:
                c = None
        if c is None:
            c = m.clip(normal=(0, -1, 0), origin=(0, sec_y, 0))
        safe_add(p, c, n)


if "iso" in only:
    W, H = 1500, 1900
    p = plotter(W, H)
    for n in ALL:
        add(p, load(n), n)
    camera(p, (5, 0, -40), (1.25, -0.95, 0.75), 800)
    p.screenshot(f"{OUT}/v_isometric.png"); p.close()

if "lower" in only:
    # lower chamber with bulkhead, upper parts removed
    W, H = 2300, 1400
    p = plotter(W, H)
    hide = {"upper_housing", "bulkhead", "grommet", "oring_upper", "carrier", "esp_headers", "esp32", "esp32_parts",
            "car_connector", "screws", "vent", "light_pipe", "spi_harness", "neck", "sheath", "neck_gasket"}
    for n in ALL:
        if n in hide:
            continue
        add(p, load(n), n)
    camera(p, (6, 0, 18), (0.55, -0.80, 1.45), 560)
    p.render()
    a0 = r1.GLAND_ANGLES[0]; a1 = r1.GLAND_ANGLES[1]
    A = [
        ((r1.MAX_X0 + 10, -8, r1.Z_MAX + 1.6), "MAX31865 breakout on 30 x 30 FR4\nsub-carrier, 4 printed standoffs", "L"),
        ((r1.MAX_X0 + r1.MAX_LX - 3.6, 6, r1.Z_MAX + 9.6), "RTD terminal faces the neck bore:\n3-wire PT100 leads < 40 mm long", "L"),
        ((0, 0, r1.FLOOR_T + 0.2), "Floor hole D8: RTD leads up\nfrom the SS304 neck", "L"),
        ((r1.TB_X, 0, r1.FLOOR_T + r1.PED_H + 12), "3-way terminal block on pedestal\n(5 V field wiring)", "R"),
        (r1.polar(r1.ANCHOR_R, a0, r1.GLAND_Z - 3), "Cable-tie anchor on the gland axis\n(secondary strain relief)", "R"),
        (r1.polar(r1.BODY_OD / 2 + 10, a0, r1.GLAND_Z + 6), "PG7 gland: power cable 3-6.5 mm", "R"),
        (r1.polar(r1.BODY_OD / 2 + 10, a1, r1.GLAND_Z + 6), "Spare PG7 (blanked): remote probe\nor comms cable", "R"),
        ((-r1.GROOVE_OD / 2 + 1.8, 0, r1.LOWER_H), "2.0 mm O-ring groove (from R0)", "L"),
    ]
    anchors = [(to_px(p, pt, H), t, s) for pt, t, s in A]
    p.screenshot(f"{OUT}/_lower_raw.png"); p.close()
    annotate(f"{OUT}/_lower_raw.png", anchors, f"{OUT}/v_lower_chamber.png", W, H, margin=720)

if "upper" in only:
    W, H = 2300, 1400
    p = plotter(W, H)
    hide = {"upper_housing", "screws", "vent", "light_pipe", "oring_upper", "neck", "sheath", "neck_gasket"}
    for n in ALL:
        if n in hide:
            continue
        add(p, load(n), n)
    camera(p, (0, 0, 52), (0.55, -0.85, 1.25), 400)
    p.render()
    A = [
        ((10, -6, r1.Z_ESP + 1.6), "ESP32-DevKitC V4 on 2 x 19-way\nfemale headers (plug-in, replaceable)", "R"),
        ((22, 0, r1.Z_ESP + 2.5), "Antenna end: plastic wall, no metal\nwithin 15 mm", "R"),
        ((25, 25, r1.Z_CAR + 1.6), "D70 FR4 carrier, 4 x M3 into\nheat-set inserts in bulkhead standoffs", "R"),
        ((-20, -14, r1.Z_CAR - 3), "JST-XH 8-way: unplug harness to\nlift the ESP32 stage out", "L"),
        ((-30, 30, r1.LOWER_H + r1.BULKHEAD_T), "Bulkhead: thermal + EMI barrier\nbetween chambers", "L"),
        ((-20, 0, r1.LOWER_H + r1.BULKHEAD_T + 1.5), "Potted grommet feed-through", "L"),
    ]
    anchors = [(to_px(p, pt, H), t, s) for pt, t, s in A]
    p.screenshot(f"{OUT}/_upper_raw.png"); p.close()
    annotate(f"{OUT}/_upper_raw.png", anchors, f"{OUT}/v_upper_chamber.png", W, H, margin=700)

if "cutaway" in only:
    W, H = 2200, 2200
    p = plotter(W, H)
    clip_y(p, ALL)
    camera(p, (0, 0, -45), (0.42, -1.3, 0.38), 1000)
    p.render()
    A = [
        ((-28, 0, 85), "Upper chamber: ESP32-DevKitC\n(RF, heat, USB access)", "L"),
        ((-20, 0, 24), "Lower chamber: MAX31865 + terminals\n(sealed field wiring)", "L"),
        ((-r1.ORING_MEAN_D / 2, 0, r1.LOWER_H - 1), "Two FKM O-rings in 2.0 mm\ngrooves, bulkhead clamped", "L"),
        ((10.65, 0, -40), "SS304 finned neck, 60 mm:\nthermal decoupling", "R"),
        ((r1.NPT_OD / 2, 0, -85), "1/2\"-14 NPT process thread", "R"),
        ((3, 0, -180), "Class A PT100, 6 mm sheath,\ntip 194 mm below housing", "R"),
        ((0, 0, 8), "RTD leads up the neck bore", "R"),
        ((14, 0, r1.Z_ESP + 2), "17+ mm free above ESP32", "R"),
    ]
    anchors = [(to_px(p, pt, H), t, s) for pt, t, s in A]
    p.screenshot(f"{OUT}/_cutaway_raw.png"); p.close()
    annotate(f"{OUT}/_cutaway_raw.png", anchors, f"{OUT}/v_cutaway.png", W, H, margin=720)

if "exploded" in only:
    W, H = 2300, 2700
    p = plotter(W, H)
    for n in ALL:
        off = r1.explode_offset(n)
        if off is None or n == "power_cable":
            continue
        add(p, load(n, off), n)
    camera(p, (0, 0, 20), (1.0, -1.3, 0.55), 1650)
    p.render()
    bp = r1.bolt_points()[3]
    A = [
        ((bp[0], bp[1], 56 + 230), "4 x M4 A2-70 SHCS into brass\nheat-set inserts (lower flange)", "R"),
        ((22, 0, 105 + 200), "M12 ePTFE vent", "R"),
        ((30, -30, 80 + 165), "Upper housing, ASA, 7 mm wall", "R"),
        ((12, -6, r1.Z_ESP + 118 + 2), "ESP32-DevKitC V4", "R"),
        ((25, -25, r1.Z_CAR + 95 + 1), "D70 FR4 carrier", "R"),
        ((r1.ORING_MEAN_D / 2 * 0.7, -r1.ORING_MEAN_D / 2 * 0.7, 50 + 80), "FKM O-ring 80 x 2.65", "R"),
        ((-r1.FLANGE_OD / 2 * 0.7, -r1.FLANGE_OD / 2 * 0.7, 47 + 55), "Bulkhead + potted grommet", "L"),
        ((-r1.ORING_MEAN_D / 2 * 0.7, -r1.ORING_MEAN_D / 2 * 0.7, 44 + 30), "FKM O-ring 80 x 2.65", "L"),
        ((-30, -25, 25), "Lower housing, ASA: MAX31865 +\nterminal block inside", "L"),
        (r1.polar(r1.BODY_OD / 2 + 40, r1.GLAND_ANGLES[0], r1.GLAND_Z), "2 x PG7 glands (1 blanked)", "R"),
        ((0, -r1.NECK_FLANGE_D / 2 + 3, -0.5 - 28), "FKM flange gasket", "L"),
        ((r1.FIN_D / 2 * 0.7, -r1.FIN_D / 2 * 0.7, -30 - 55), "SS304 finned neck, 1/2\" NPT", "R"),
        ((0, -3, -170 - 95), "Class A PT100, 6 mm sheath", "L"),
    ]
    anchors = [(to_px(p, pt, H), t, s) for pt, t, s in A]
    p.screenshot(f"{OUT}/_exploded_raw.png"); p.close()
    annotate(f"{OUT}/_exploded_raw.png", anchors, f"{OUT}/v_exploded.png", W, H, margin=760)

SHORT["v"] = False
if "mount" in only:
    W, H = 3000, 1700
    p = plotter(W, H)
    DX = 130.0
    for n in ALL:
        add(p, load(n, (-DX, 0, 0)), n)
        add(p, load(n, (DX, 0, 0)), n)
    add(p, load("rig_bracket", (DX, 0, 0)), "lower_housing", color=(0.70, 0.72, 0.75))
    add(p, load("npt_locknut", (DX, 0, 0)), "screws", color=(0.62, 0.64, 0.66))
    camera(p, (0, 0, -50), (0.35, -1.3, 0.40), 1250)
    p.render()
    A = [
        ((DX + 48, -22, -79), "Mode B (bench / rig / bath):\n4 mm Al 6061 bracket, D21.8 hole,\nclamped by a 1/2\" NPT locknut;\n4 x M5 slots", "R"),
        ((-DX, -r1.NPT_OD / 2, -85), "Mode A (process): 1/2\" NPT thread\ninto a pipe / vessel port, PTFE tape,\nspanner on the 27 AF hex", "L"),
        ((-DX + 3, 0, -165), "Sensing tip in the process", "L"),
        ((DX + r1.BODY_OD / 2, 0, 60), "Electronics 65 mm above\nthe process fitting", "R"),
    ]
    anchors = [(to_px(p, pt, H), t, s_) for pt, t, s_ in A]
    p.screenshot(f"{OUT}/_mount_raw.png"); p.close()
    annotate(f"{OUT}/_mount_raw.png", anchors, f"{OUT}/v_mounting.png", W, H, margin=860, fs=26)
print("renders:", only)
