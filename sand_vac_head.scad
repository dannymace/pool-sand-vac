$fn = 112;

// Functional sand-vac eductor head for 3D printing.
//
// Flow direction:
//   large sand pickup mouth -> controlled suction throat -> mixing tube ->
//   1-1/4 in. exhaust hose barb
//
// This model uses an eductor/jet-pump layout rather than a passive pipe
// venturi. Garden-hose water exits a small downstream-facing jet inside the
// throat; the high-speed jet entrains the surrounding sand/water slurry.

part = "head"; // "head", "section", "flow_check"

// Print and strength settings
wall = 3.6;
rim_wall = 4.4;
bottom_skid_enabled = false;

// Sand pickup and main slurry path
mouth_opening_major = 76;  // wide enough to avoid bridging in wet sand
mouth_opening_minor = 48;
mouth_outer_major = mouth_opening_major + (rim_wall * 2);
mouth_outer_minor = mouth_opening_minor + (rim_wall * 2);
converge_len = 72;
throat_id = 26.0;          // smaller than outlet to keep pickup velocity high
throat_len = 34;
diffuser_len = 30;
outlet_id = 31.0;
barb_start = converge_len + throat_len + diffuser_len;

// Exhaust hose barb for nominal 1-1/4 in. pool hose
barb_length = 44;
barb_root_d = 32.2;
barb_peak_d = 35.0;
barb_count = 4;
barb_pitch = barb_length / barb_count;

// Garden hose and pressure jet. The hose boss is low-profile and points
// rearward/upward so a connected hose naturally exits away from the sand bed.
hose_junction = [64, 0, 30];
hose_axis_deg = 76;        // about 14 degrees above the main body axis
jet_plenum = [74, 0, 0];
jet_exit_x = 87;
feed_bore_d = 9.0;
feed_support_od = 15.2;
jet_body_d = 12.5;
jet_tip_d = 7.4;
nozzle_keel_width = 3.2; // printable internal web that supports the center jet
nozzle_orifice_d_default = 5.8;
nozzle_orifice_d = is_undef(nozzle_orifice_d_override) ? nozzle_orifice_d_default : nozzle_orifice_d_override;
nozzle_straight_len = 5.0;

// Standard US garden hose thread, printable approximation.
ght_pitch = 25.4 / 11.5;
ght_female_major_d = 27.4; // internal female GHT groove diameter
ght_female_minor_d = 24.8; // internal female thread crest / tap-drill diameter
ght_thread_depth = 1.45;
ght_thread_root_overlap = 0.35; // fuses thread root into the connector body
ght_thread_len = 18.0;
female_socket_od = 33.0;
female_socket_len = 22.0;
female_socket_chamfer_d = 29.0;
washer_face_d = 30.5;
washer_face_t = 3.0;
grip_hex_d = 34;
grip_hex_t = 6;

external_hose_len = washer_face_t + grip_hex_t + female_socket_len;

feed_curve_steps = 5;
feed_curve_start = [
    hose_junction[0] - sin(hose_axis_deg) * 1.4,
    0,
    hose_junction[2] - cos(hose_axis_deg) * 1.4
];
feed_curve_c1 = [66, 0, 22];
feed_curve_c2 = [66, 0, 3];

function y_axis_angle(from, to) =
    atan2(to[0] - from[0], to[2] - from[2]);

function bezier_point(p0, p1, p2, p3, t) = [
    pow(1 - t, 3) * p0[0] + 3 * pow(1 - t, 2) * t * p1[0] + 3 * (1 - t) * pow(t, 2) * p2[0] + pow(t, 3) * p3[0],
    pow(1 - t, 3) * p0[1] + 3 * pow(1 - t, 2) * t * p1[1] + 3 * (1 - t) * pow(t, 2) * p2[1] + pow(t, 3) * p3[1],
    pow(1 - t, 3) * p0[2] + 3 * pow(1 - t, 2) * t * p1[2] + 3 * (1 - t) * pow(t, 2) * p2[2] + pow(t, 3) * p3[2]
];

function feed_curve_point(i) =
    bezier_point(feed_curve_start, feed_curve_c1, feed_curve_c2, jet_plenum, i / feed_curve_steps);

module x_cylinder(len, d, center = true) {
    rotate([0, 90, 0]) cylinder(h = len, d = d, center = center);
}

module x_taper(len, d1, d2) {
    rotate([0, 90, 0]) cylinder(h = len, d1 = d1, d2 = d2, center = false);
}

module x_ellipse_disc(thickness, major, minor) {
    rotate([0, 90, 0])
        scale([1, major / minor, 1])
        cylinder(h = thickness, d = minor, center = true);
}

module y_plane_cylinder(from, to, d) {
    len = sqrt(
        pow(to[0] - from[0], 2) +
        pow(to[1] - from[1], 2) +
        pow(to[2] - from[2], 2)
    );

    translate(from)
        rotate([0, y_axis_angle(from, to), 0])
        cylinder(h = len, d = d, center = false);
}

module segment_tube(from, to, d, fn = 48) {
    len = sqrt(
        pow(to[0] - from[0], 2) +
        pow(to[1] - from[1], 2) +
        pow(to[2] - from[2], 2)
    );

    translate(from)
        rotate([0, y_axis_angle(from, to), 0])
        cylinder(h = len, d = d, center = false, $fn = fn);
}

module smooth_tube(points, d, fn = 48) {
    for (i = [0 : len(points) - 2]) {
        segment_tube(points[i], points[i + 1], d, fn);
    }

    for (i = [0 : len(points) - 1]) {
        translate(points[i])
            sphere(d = d, $fn = fn);
    }
}

module hose_axis() {
    translate(hose_junction)
        rotate([0, hose_axis_deg, 0])
        children();
}

module section_cut() {
    translate([-120, -120, -90])
        cube([360, 120, 200]);
}

module flat_print_skid() {
    // A narrow center skid replaces the earlier wide plate. It supports the
    // lowest centerline of the scoop and gives the internal jet keel a printable
    // load path without creating a large sheet under the mouth.
    hull() {
        translate([2, 0, -(mouth_outer_minor / 2) - 1.2])
            cube([18, 18, 2.4], center = true);

        translate([barb_start - 8, 0, -(throat_id / 2) - wall - 0.8])
            cube([18, 14, 2.0], center = true);
    }
}

module barb_profile() {
    for (i = [0 : barb_count - 1]) {
        x0 = i * barb_pitch;
        x1 = x0 + barb_pitch * 0.66;

        translate([barb_start + x0, 0, 0])
            x_taper(x1 - x0, barb_peak_d, barb_root_d);

        translate([barb_start + x1, 0, 0])
            x_taper(barb_pitch * 0.34, barb_root_d, barb_root_d);
    }
}

module outer_shell() {
    union() {
        hull() {
            translate([0, 0, 0])
                x_ellipse_disc(0.2, mouth_outer_major, mouth_outer_minor);

            translate([converge_len, 0, 0])
                x_cylinder(0.2, throat_id + (wall * 2));
        }

        translate([converge_len, 0, 0])
            x_taper(throat_len, throat_id + (wall * 2), throat_id + (wall * 2));

        translate([converge_len + throat_len, 0, 0])
            x_taper(diffuser_len, throat_id + (wall * 2), outlet_id + (wall * 2));

        barb_profile();

        if (bottom_skid_enabled)
            flat_print_skid();
    }
}

module inner_shell() {
    union() {
        hull() {
            translate([-1.5, 0, 0])
                x_ellipse_disc(0.2, mouth_opening_major, mouth_opening_minor);

            translate([converge_len + 2, 0, 0])
                x_cylinder(0.2, throat_id);
        }

        translate([converge_len, 0, 0])
            x_taper(throat_len + 3, throat_id, throat_id);

        translate([converge_len + throat_len, 0, 0])
            x_taper(diffuser_len + 4, throat_id, outlet_id);

        translate([barb_start - 2, 0, 0])
            x_taper(barb_length + 8, outlet_id, outlet_id);
    }
}

module body_shell() {
    difference() {
        outer_shell();
        inner_shell();
    }
}

module thread_helix(major_d, pitch, length, depth, root_overlap = 0) {
    slices_per_turn = 36;
    flank_w = pitch * 0.42;
    crest_w = pitch * 0.20;

    linear_extrude(
        height = length,
        twist = -360 * length / pitch,
        slices = max(20, ceil(length / pitch) * slices_per_turn),
        convexity = 10
    )
        translate([(major_d / 2) - depth - root_overlap, 0, 0])
        polygon([
            [0, -flank_w],
            [depth + root_overlap, -crest_w],
            [depth + root_overlap, crest_w],
            [0, flank_w]
        ]);
}

module external_ght_thread_cutter(thread_start_z, major_d, minor_d, thread_len) {
    union() {
        translate([0, 0, thread_start_z])
            cylinder(h = thread_len, d = minor_d, center = false);

        translate([0, 0, thread_start_z])
            thread_helix(
                major_d = major_d,
                pitch = ght_pitch,
                length = thread_len,
                depth = ght_thread_depth,
                root_overlap = ght_thread_root_overlap
            );

        translate([0, 0, thread_start_z + thread_len])
            cylinder(h = 1.3, d1 = minor_d, d2 = minor_d - 1.2, center = false);
    }
}

module female_ght_socket_cut() {
    z0 = washer_face_t + grip_hex_t;
    socket_end = z0 + female_socket_len;

    hose_axis() {
        translate([0, 0, z0 - 0.5])
            cylinder(h = female_socket_len + 2.0, d = ght_female_minor_d, center = false);

        external_ght_thread_cutter(
            z0 + 1.0,
            ght_female_major_d,
            ght_female_minor_d,
            min(ght_thread_len, female_socket_len - 2.0)
        );

        translate([0, 0, socket_end - 1.2])
            cylinder(h = 2.0, d1 = female_socket_chamfer_d, d2 = ght_female_minor_d, center = false);
    }
}

module hose_connector_outer() {
    hose_axis() {
        translate([0, 0, -3])
            cylinder(h = washer_face_t + 3, d = washer_face_d, center = false);

        translate([0, 0, washer_face_t])
            cylinder(h = grip_hex_t, d = grip_hex_d, $fn = 6, center = false);

        translate([0, 0, washer_face_t + grip_hex_t])
            cylinder(h = female_socket_len, d = female_socket_od, center = false);
    }
}

module venturi_nozzle_outer() {
    union() {
        smooth_tube(
            [for (i = [0 : feed_curve_steps]) feed_curve_point(i)],
            feed_support_od
        );

        translate(hose_junction)
            sphere(d = feed_support_od);

        translate([jet_plenum[0] - 3, 0, jet_plenum[2]])
            x_taper(jet_exit_x - jet_plenum[0] + 3, jet_body_d, jet_tip_d);

        nozzle_print_keel();
    }
}

module nozzle_print_keel() {
    // This web is deliberately inside the slurry path. The earlier suspended
    // center jet could start in midair during FDM printing; this gives it a
    // self-supporting ramp from the lower throat wall while keeping most of the
    // annular suction area open.
    hull() {
        translate([jet_plenum[0] - 5, 0, -(throat_id / 2) - 0.9])
            cube([5, nozzle_keel_width, 1.4], center = true);

        translate([jet_exit_x - 1.5, 0, -(jet_tip_d / 2) - 0.3])
            cube([5, nozzle_keel_width, 1.2], center = true);
    }
}

module water_path_cuts() {
    hose_axis()
        translate([0, 0, -1])
        cylinder(h = external_hose_len + 11, d = feed_bore_d, center = false);

    smooth_tube(
        [for (i = [0 : feed_curve_steps]) feed_curve_point(i)],
        feed_bore_d
    );

    translate([jet_plenum[0] - 1.8, 0, jet_plenum[2]])
        x_taper(jet_exit_x - jet_plenum[0] - nozzle_straight_len + 1.8, feed_bore_d, nozzle_orifice_d);

    translate([jet_exit_x - nozzle_straight_len, 0, jet_plenum[2]])
        x_taper(nozzle_straight_len + 1.2, nozzle_orifice_d, nozzle_orifice_d);

    female_ght_socket_cut();
}

module head() {
    difference() {
        union() {
            body_shell();
            hose_connector_outer();
            venturi_nozzle_outer();
        }

        water_path_cuts();
    }
}

module sectioned_head() {
    difference() {
        head();
        section_cut();
    }
}

module flow_visuals() {
    color([0.1, 0.45, 1.0, 0.55])
        water_path_cuts();

    color([0.1, 0.8, 0.25, 0.35])
        hull() {
            translate([5, 0, 0])
                x_ellipse_disc(0.3, mouth_opening_major - 8, mouth_opening_minor - 8);

            translate([converge_len - 4, 0, 0])
                x_cylinder(0.3, throat_id - 5);
        }

    color([0.8, 0.55, 0.18, 0.45])
        translate([jet_exit_x, 0, 0])
        x_taper(barb_start + barb_length - jet_exit_x - 2, throat_id - 4, outlet_id - 2);
}

if (part == "section") {
    sectioned_head();
} else if (part == "flow_check") {
    sectioned_head();
    flow_visuals();
} else {
    head();
}
