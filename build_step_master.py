import math
from pathlib import Path

import cadquery as cq
from cadquery import exporters


P = {
    "wall": 3.6,
    "rim_wall": 4.4,
    "mouth_opening_major": 76.0,
    "mouth_opening_minor": 48.0,
    "converge_len": 72.0,
    "throat_id": 26.0,
    "throat_len": 72.0,
    "diffuser_len": 30.0,
    "outlet_id": 31.0,
    "barb_length": 44.0,
    "barb_root_d": 32.2,
    "barb_peak_d": 35.0,
    "barb_count": 4,
    "hose_junction": (64.0, 0.0, 30.0),
    "hose_axis_deg": 76.0,
    "jet_plenum": (74.0, 0.0, 0.0),
    "jet_exit_x": 87.0,
    "feed_bore_d": 9.0,
    "feed_support_od": 15.2,
    "feed_socket_od": 19.0,
    "feed_socket_depth": 8.0,
    "feed_socket_extension": 6.0,
    "feed_junction_blend_od": 20.0,
    "jet_body_d": 12.5,
    "jet_tip_d": 8.6,
    "nozzle_orifice_d": 5.8,
    "nozzle_straight_len": 5.0,
    "ght_pitch": 25.4 / 11.5,
    "ght_female_major_d": 27.4,
    "ght_female_minor_d": 24.8,
    "ght_thread_len": 18.0,
    "ght_thread_overlap": 0.25,
    "female_socket_od": 33.0,
    "female_socket_len": 22.0,
    "female_socket_chamfer_d": 29.0,
    "washer_face_d": 30.5,
    "washer_face_t": 3.0,
    "grip_hex_d": 34.0,
    "grip_hex_t": 6.0,
    "feed_curve_c1": (66.0, 0.0, 22.0),
    "feed_curve_c2": (66.0, 0.0, 3.0),
    "feed_curve_steps": 5,
    "feed_curve_sample_count": 18,
}

P["mouth_outer_major"] = P["mouth_opening_major"] + (P["rim_wall"] * 2.0)
P["mouth_outer_minor"] = P["mouth_opening_minor"] + (P["rim_wall"] * 2.0)
P["barb_start"] = P["converge_len"] + P["throat_len"] + P["diffuser_len"]
P["barb_pitch"] = P["barb_length"] / P["barb_count"]
P["external_hose_len"] = P["washer_face_t"] + P["grip_hex_t"] + P["female_socket_len"]


def v(pt):
    return cq.Vector(*pt)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def length(a):
    return math.sqrt((a[0] ** 2) + (a[1] ** 2) + (a[2] ** 2))


def normalize(a):
    mag = length(a)
    if mag == 0:
        raise ValueError("Zero-length vector")
    return (a[0] / mag, a[1] / mag, a[2] / mag)


def axis_dir(deg):
    rad = math.radians(deg)
    return (math.sin(rad), 0.0, math.cos(rad))


def bezier_point(p0, p1, p2, p3, t):
    omt = 1.0 - t
    return (
        (omt ** 3) * p0[0] + 3.0 * (omt ** 2) * t * p1[0] + 3.0 * omt * (t ** 2) * p2[0] + (t ** 3) * p3[0],
        (omt ** 3) * p0[1] + 3.0 * (omt ** 2) * t * p1[1] + 3.0 * omt * (t ** 2) * p2[1] + (t ** 3) * p3[1],
        (omt ** 3) * p0[2] + 3.0 * (omt ** 2) * t * p1[2] + 3.0 * omt * (t ** 2) * p2[2] + (t ** 3) * p3[2],
    )


def circle_wire_x(x_pos, diameter):
    return cq.Workplane("YZ").workplane(offset=x_pos).circle(diameter / 2.0).wire().val()


def ellipse_wire_x(x_pos, major, minor):
    return cq.Workplane("YZ").workplane(offset=x_pos).ellipse(major / 2.0, minor / 2.0).wire().val()


def loft_closed(wires):
    return cq.Solid.makeLoft(wires, True)


def cylinder_x(x_pos, diameter, distance):
    return cq.Solid.makeCylinder(diameter / 2.0, distance, cq.Vector(x_pos, 0.0, 0.0), cq.Vector(1.0, 0.0, 0.0))


def cone_x(x_pos, d1, d2, distance):
    return cq.Solid.makeCone(d1 / 2.0, d2 / 2.0, distance, cq.Vector(x_pos, 0.0, 0.0), cq.Vector(1.0, 0.0, 0.0))


def cylinder_along(start, end, diameter):
    delta = sub(end, start)
    return cq.Solid.makeCylinder(diameter / 2.0, length(delta), v(start), v(normalize(delta)))


def sphere_at(center, diameter):
    return cq.Solid.makeSphere(diameter / 2.0, v(center))


def fuse_all(solids):
    result = solids[0]
    for solid in solids[1:]:
        result = result.fuse(solid)
    return result


def feed_curve_points():
    start = P["hose_junction"]
    points = []
    for i in range(P["feed_curve_sample_count"] + 1):
        t = i / P["feed_curve_sample_count"]
        points.append(bezier_point(start, P["feed_curve_c1"], P["feed_curve_c2"], P["jet_plenum"], t))
    return points


def spline_edge(points):
    return cq.Edge.makeSpline([v(pt) for pt in points])


def circle_wire_at(point, normal, diameter, x_dir=(0.0, 1.0, 0.0)):
    tangent = normalize(normal)
    plane = cq.Plane(origin=v(point), xDir=v(x_dir), normal=v(tangent))
    return cq.Workplane(plane).circle(diameter / 2.0).wire().val()


def smooth_sweep(points, diameter):
    path = spline_edge(points)
    tangent = sub(points[1], points[0])
    profile = circle_wire_at(points[0], tangent, diameter)
    return cq.Solid.sweep(profile, [], path, makeSolid=True, isFrenet=False, transitionMode="round")


def make_outer_body():
    outer_wires = [
        ellipse_wire_x(0.0, P["mouth_outer_major"], P["mouth_outer_minor"]),
        circle_wire_x(P["converge_len"], P["throat_id"] + (P["wall"] * 2.0)),
    ]
    throat_d = P["throat_id"] + (P["wall"] * 2.0)
    diffuser_out_d = P["outlet_id"] + (P["wall"] * 2.0)

    body_sections = [
        loft_closed(outer_wires),
        cylinder_x(P["converge_len"], throat_d, P["throat_len"]),
        loft_closed(
            [
                circle_wire_x(P["converge_len"] + P["throat_len"], throat_d),
                circle_wire_x(P["barb_start"], diffuser_out_d),
            ]
        ),
    ]

    for i in range(P["barb_count"]):
        x0 = P["barb_start"] + (i * P["barb_pitch"])
        x1 = x0 + (P["barb_pitch"] * 0.66)
        x2 = x0 + P["barb_pitch"]
        body_sections.append(cone_x(x0, P["barb_peak_d"], P["barb_root_d"], x1 - x0))
        body_sections.append(cylinder_x(x1, P["barb_root_d"], x2 - x1))

    return fuse_all(body_sections)


def make_inner_body():
    inner_wires = [
        ellipse_wire_x(-1.5, P["mouth_opening_major"], P["mouth_opening_minor"]),
        circle_wire_x(P["converge_len"] + 2.0, P["throat_id"]),
    ]

    return fuse_all(
        [
            loft_closed(inner_wires),
            cylinder_x(P["converge_len"], P["throat_id"], P["throat_len"] + 3.0),
            loft_closed(
                [
                    circle_wire_x(P["converge_len"] + P["throat_len"], P["throat_id"]),
                    circle_wire_x(P["barb_start"], P["outlet_id"]),
                ]
            ),
            cylinder_x(P["barb_start"] - 2.0, P["outlet_id"], P["barb_length"] + 8.0),
        ]
    )


def make_hose_connector_outer():
    hose_axis = axis_dir(P["hose_axis_deg"])
    plane = cq.Plane(origin=v(P["hose_junction"]), xDir=cq.Vector(0.0, 1.0, 0.0), normal=v(hose_axis))

    washer = (
        cq.Workplane(plane)
        .workplane(offset=-3.0)
        .circle(P["washer_face_d"] / 2.0)
        .extrude(P["washer_face_t"] + 3.0)
        .val()
    )

    hex_body = (
        cq.Workplane(plane)
        .workplane(offset=P["washer_face_t"])
        .polygon(6, P["grip_hex_d"])
        .extrude(P["grip_hex_t"])
        .val()
    )

    socket = (
        cq.Workplane(plane)
        .workplane(offset=P["washer_face_t"] + P["grip_hex_t"])
        .circle(P["female_socket_od"] / 2.0)
        .extrude(P["female_socket_len"])
        .val()
    )

    return fuse_all([washer, hex_body, socket])


def make_external_ght_thread_cutter(z0, major_d, minor_d, thread_len):
    root_r = minor_d / 2.0
    major_r = major_d / 2.0
    bead_r = ((major_r - root_r) + P["ght_thread_overlap"]) / 2.0
    helix_r = root_r + bead_r - P["ght_thread_overlap"]
    helix_start_z = z0 + bead_r
    helix_height = thread_len - (2.0 * bead_r)

    root = cq.Solid.makeCylinder(root_r, thread_len, cq.Vector(0.0, 0.0, z0), cq.Vector(0.0, 0.0, 1.0))
    helix = cq.Wire.makeHelix(P["ght_pitch"], helix_height, helix_r, center=(0.0, 0.0, helix_start_z))

    tangent = (0.0, 2.0 * math.pi * helix_r, P["ght_pitch"])
    profile = circle_wire_at((helix_r, 0.0, helix_start_z), tangent, bead_r * 2.0, x_dir=(1.0, 0.0, 0.0))
    rib = cq.Solid.sweep(profile, [], helix, makeSolid=True, isFrenet=True, transitionMode="round")

    leadout = (
        cq.Workplane("XY")
        .workplane(offset=z0 + thread_len)
        .circle(minor_d / 2.0)
        .workplane(offset=1.3)
        .circle((minor_d - 1.2) / 2.0)
        .loft(combine=True)
        .val()
    )

    return fuse_all([root, rib, leadout]).clean()


def make_female_ght_socket_cut():
    z0 = P["washer_face_t"] + P["grip_hex_t"]
    socket_end = z0 + P["female_socket_len"]
    thread_start = z0 + 1.0
    thread_len = min(P["ght_thread_len"], P["female_socket_len"] - 2.0)

    bore = cq.Solid.makeCylinder(
        P["ght_female_minor_d"] / 2.0,
        P["female_socket_len"] + 2.0,
        cq.Vector(0.0, 0.0, z0 - 0.5),
        cq.Vector(0.0, 0.0, 1.0),
    )
    thread = make_external_ght_thread_cutter(
        thread_start,
        P["ght_female_major_d"],
        P["ght_female_minor_d"],
        thread_len,
    )
    lead_in = cq.Solid.makeCone(
        P["female_socket_chamfer_d"] / 2.0,
        P["ght_female_minor_d"] / 2.0,
        2.0,
        cq.Vector(0.0, 0.0, socket_end - 1.2),
        cq.Vector(0.0, 0.0, 1.0),
    )

    return fuse_all([bore, thread, lead_in]).clean().rotate((0, 0, 0), (0, 1, 0), P["hose_axis_deg"]).translate(P["hose_junction"])


def make_venturi_outer():
    points = feed_curve_points()
    hose_axis = axis_dir(P["hose_axis_deg"])
    socket_start = add(P["hose_junction"], mul(hose_axis, -P["feed_socket_depth"]))
    socket_end = add(P["hose_junction"], mul(hose_axis, P["feed_socket_extension"]))
    solids = [
        cylinder_along(socket_start, socket_end, P["feed_socket_od"]),
        cylinder_along(socket_start, points[2], P["feed_junction_blend_od"]),
        smooth_sweep(points, P["feed_support_od"]),
    ]
    solids.append(
        cone_x(
            P["jet_plenum"][0] - 3.0,
            P["jet_body_d"],
            P["jet_tip_d"],
            P["jet_exit_x"] - P["jet_plenum"][0] + 3.0,
        )
    )
    return fuse_all(solids)


def make_water_path_cut():
    hose_axis = axis_dir(P["hose_axis_deg"])
    hose_start = add(P["hose_junction"], mul(hose_axis, -1.0))
    path_points = feed_curve_points()

    solids = [
        cq.Solid.makeCylinder(
            P["feed_bore_d"] / 2.0,
            P["external_hose_len"] + 11.0,
            v(hose_start),
            v(hose_axis),
        )
    ]

    solids.append(smooth_sweep(path_points, P["feed_bore_d"]))
    start_tangent = normalize(sub(path_points[1], path_points[0]))
    solids.append(
        cylinder_along(
            add(path_points[0], mul(start_tangent, -1.2)),
            add(path_points[0], mul(start_tangent, 1.2)),
            P["feed_bore_d"] * 1.25,
        )
    )

    solids.append(
        cone_x(
            P["jet_plenum"][0] - 1.8,
            P["feed_bore_d"],
            P["nozzle_orifice_d"],
            P["jet_exit_x"] - P["jet_plenum"][0] - P["nozzle_straight_len"] + 1.8,
        )
    )
    solids.append(
        cylinder_x(
            P["jet_exit_x"] - P["nozzle_straight_len"],
            P["nozzle_orifice_d"],
            P["nozzle_straight_len"] + 1.2,
        )
    )
    solids.append(make_female_ght_socket_cut())
    return fuse_all(solids)


def build_clean_master():
    # Match the OpenSCAD STL: hollow the slurry body first, then add the hose
    # boss and venturi insert, then cut only the pressure-water path.
    body_shell = make_outer_body().cut(make_inner_body())
    combined = fuse_all(
        [
            body_shell,
            make_hose_connector_outer(),
            make_venturi_outer(),
        ]
    )
    return combined.cut(make_water_path_cut()).clean()


def build_venturi_insert():
    # Export the pressure-feed venturi insert as a separate editable solid.
    # This keeps the jet pipe easy to identify and merge inside Fusion 360
    # if the combined master import visually obscures or drops it.
    return make_venturi_outer().cut(make_water_path_cut()).clean()


def print_shape_stats(label, shape):
    bb = shape.BoundingBox()
    print(
        f"{label}: solids={len(shape.Solids())}, "
        f"volume_cm3={shape.Volume() / 1000.0:.2f}, "
        f"bounds_mm=({bb.xlen:.2f}, {bb.ylen:.2f}, {bb.zlen:.2f})"
    )


def main():
    out_dir = Path(__file__).resolve().parent / "out"
    out_dir.mkdir(exist_ok=True)

    model = build_clean_master()
    venturi_insert = build_venturi_insert()

    combined_step_path = out_dir / "sand_vac_head_combined_smooth.step"
    combined_stl_path = out_dir / "sand_vac_head_combined_smooth.stl"
    step_path = out_dir / "sand_vac_head_clean_master.step"
    stl_path = out_dir / "sand_vac_head_clean_master.stl"
    venturi_step_path = out_dir / "sand_vac_head_venturi_insert.step"
    venturi_stl_path = out_dir / "sand_vac_head_venturi_insert.stl"

    exporters.export(model, str(combined_step_path))
    exporters.export(model, str(combined_stl_path))
    exporters.export(model, str(step_path))
    exporters.export(model, str(stl_path))
    exporters.export(venturi_insert, str(venturi_step_path))
    exporters.export(venturi_insert, str(venturi_stl_path))

    print_shape_stats("combined", model)
    print_shape_stats("venturi_insert", venturi_insert)
    print(f"Wrote {combined_step_path}")
    print(f"Wrote {combined_stl_path}")
    print(f"Wrote {step_path}")
    print(f"Wrote {stl_path}")
    print(f"Wrote {venturi_step_path}")
    print(f"Wrote {venturi_stl_path}")


if __name__ == "__main__":
    main()
