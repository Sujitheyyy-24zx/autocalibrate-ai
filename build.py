import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cadquery as cq
import r1c as r1

OUT = "/home/claude/cad_r1b/out"
P = r1.PARTS
shapes = {}
assy = cq.Assembly(name="AutoCalibrate_PT100_Node_R1")
for name, (fn, col, desc) in P.items():
    t = time.time()
    wp = fn()
    vals = wp.vals()
    shp = vals[0] if len(vals) == 1 else cq.Compound.makeCompound(vals)
    shapes[name] = shp
    assy.add(shp, name=name, color=cq.Color(*col))
    cq.exporters.export(cq.Workplane().add(shp), f"{OUT}/stl/{name}.stl", tolerance=0.04, angularTolerance=0.12)
    bb = shp.BoundingBox()
    print(f"{name:20s} {time.time()-t:5.1f}s vol={shp.Volume():9.0f} valid={shp.isValid()} "
          f"x[{bb.xmin:7.1f},{bb.xmax:7.1f}] y[{bb.ymin:6.1f},{bb.ymax:6.1f}] z[{bb.zmin:6.1f},{bb.zmax:6.1f}]")

assy.export(f"{OUT}/step/AutoCalibrate_PT100_Node_R1_assembly.step")
for n in ("lower_housing", "upper_housing", "bulkhead", "neck", "carrier", "sub_carrier"):
    cq.exporters.export(cq.Workplane().add(shapes[n]), f"{OUT}/step/R1_{n}.step")
b, nut = r1.rig_bracket()
cq.exporters.export(b, f"{OUT}/step/R1_rig_bracket.step")
cq.exporters.export(b, f"{OUT}/stl/rig_bracket.stl", tolerance=0.05)
cq.exporters.export(nut, f"{OUT}/stl/npt_locknut.stl", tolerance=0.05)

# interference check: every pair that must not overlap
check = [n for n in shapes if not n.startswith("wire_")]
skip = {frozenset(p) for p in [("screws", "lower_housing"), ("screws", "upper_housing"), ("screws", "bulkhead"),
                                ("grommet", "bulkhead"), ("spi_harness", "grommet"), ("blank_plug", "gland_1"),
                                ("power_cable", "gland_0")]}
res = {}
for i, a in enumerate(check):
    for b in check[i + 1:]:
        if frozenset((a, b)) in skip:
            continue
        ba, bb = shapes[a].BoundingBox(), shapes[b].BoundingBox()
        if ba.xmax < bb.xmin or bb.xmax < ba.xmin or ba.ymax < bb.ymin or bb.ymax < ba.ymin or ba.zmax < bb.zmin or bb.zmax < ba.zmin:
            continue
        v = shapes[a].intersect(shapes[b]).Volume()
        if v > 0.01:
            res[f"{a} / {b}"] = round(v, 2)
print("OVERLAPS:", json.dumps(res, indent=1))
json.dump({k: {"vol": shapes[k].Volume()} for k in shapes}, open(f"{OUT}/volumes.json", "w"))
wres = {}
for w in [n for n in shapes if n.startswith("wire_")]:
    for b in ("lower_housing", "upper_housing", "bulkhead", "carrier", "max31865", "sub_carrier", "terminal_block", "neck"):
        v = shapes[w].intersect(shapes[b]).Volume()
        if v > 0.01:
            wres[f"{w} / {b}"] = round(v, 2)
print("WIRE OVERLAPS:", wres)
