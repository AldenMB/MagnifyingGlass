import cadquery as cq
from types import SimpleNamespace as ns
import math

INCH = 25.4

measured = ns(diameter=5 * INCH, thickness=ns(edge=4, center=20))

screw = ns(head=11, length=20, clearance_diameter=4.25, grip_diameter=2.75)

min_wall_thickness = 1.6
fillet = 4


def sagitta_radius(sag, stride):
    return sag / 2 + stride**2 / (8 * sag)


grind_radius = sagitta_radius(
    (measured.thickness.center - measured.thickness.edge) / 2, measured.diameter
)

lens = cq.Workplane().cylinder(grind_radius * 2, measured.diameter / 2)
sphere_center = grind_radius - measured.thickness.center / 2
for z in [sphere_center, -sphere_center]:
    lens = lens.intersect(cq.Workplane().sphere(grind_radius).translate([0, 0, z]))

rim = cq.Workplane("YZ")
rim = rim.moveTo(
    rim_center := measured.diameter / 2
    + screw.clearance_diameter / 2
    + min_wall_thickness,
    0,
)
rim = rim.rect(
    border := screw.head + 2 * fillet, thickness := screw.length + min_wall_thickness
)
rim = rim.revolve()

# show_object(rim, name='rim', options={'color':'green', 'alpha':0.1})


def polar(r, theta):
    return r * math.cos(theta), r * math.sin(theta)


handle = cq.Workplane("XY")
handle = handle.lineTo(*polar(R := rim_center + border / 2, theta := math.pi / 6))
r = (R * math.sin(theta) - thickness / 2) / (1 - math.sin(theta))
handle = handle.radiusArc([(R + r) * math.cos(theta), thickness / 2], -r)
handle = handle.hLineTo(3 * measured.diameter / 2)
handle = handle.vLineTo(0)
handle = handle.close()
handle = handle.revolve(axisEnd=[1, 0, 0])
handle = handle.workplane().circle(measured.diameter / 2).cutThruAll()
handle = handle.intersect(
    cq.Workplane().box(5 * measured.diameter, 5 * measured.diameter, thickness)
)

# show_object(handle, name='handle', options={'color':'red','alpha':0.1})

frame = rim.union(handle).fillet(fillet).cut(lens)

for depth, diameter in [
    (screw.length, screw.grip_diameter),
    (thickness / 2, screw.clearance_diameter),
]:
    frame = frame.faces(">Z").workplane()
    frame = frame.polarArray(rim_center, 0, 360, 6)
    frame = frame.hole(diameter, depth)
    frame = frame.faces(">Z").workplane()
    frame = frame.moveTo(rim_center + 30, 0)
    frame = frame.hole(diameter, depth)

# show_object(frame,options={'color':'green', 'alpha':0.1})

division = frame.faces(">Z").workplane(offset=-thickness / 2)
top = division.split(keepTop=True)
bottom = division.split(keepBottom=True)

cq.exporters.export(bottom.mirror(), "frame_bottom.stl")
cq.exporters.export(top, "frame_top.stl")


# show a preview in CQgui
if __name__ == "temp":
    glass = {"color": "light blue", "alpha": 0.4}
    show_object(lens, name="lens", options=glass)
    show_object(bottom, name="bottom", options={"color": "orange", "alpha": 0.1})
    show_object(top, name="top", options={"color": "red", "alpha": 0.1})
