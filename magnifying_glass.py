import cadquery as cq
from types import SimpleNamespace as ns

INCH = 25.4

measured = ns(
    diameter = 5*INCH,
    thickness = ns(edge = 4, center = 20)
)

def sagitta_radius(sag, stride):
    return sag/2 + stride**2/(8*sag)

grind_radius = sagitta_radius(
    (measured.thickness.center - measured.thickness.edge)/2,
    measured.diameter
)

lens = cq.Workplane().cylinder(grind_radius*2, measured.diameter/2)
sphere_center = grind_radius-measured.thickness.center/2
for z in [sphere_center, -sphere_center]:
    lens = lens.intersect(
        cq.Workplane().sphere(grind_radius).translate([0,0,z])
    )

glass = {'color':'light blue', 'alpha':0.4}
show_object(lens, name='lens', options=glass)