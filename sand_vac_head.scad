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
jet_plenum = [70, 0, 0];
jet_exit_x = 87;
feed_bore_d = 9.0;
feed_support_od = 16.8;
jet_body_d = 12.5;
jet_tip_d = 7.4;
nozzle_orifice_d_default = 5.8;
nozzle_orifice_d = is_undef(nozzle_orifice_d_override) ? nozzle_orifice_d_default : nozzle_orifice_d_override;
nozzle_straight_len = 5.0;

// Standard US garden hose thread, printable approximation.
ght_pitch = 25.4 / 11.5;
ght_major_d = 26.8;
ght_minor_d = 25.2;
ght_thread_depth = 0.8;
ght_thread_root_overlap = 0.2; // prevents coincident thread-root faces in STL exports
ght_thread_len = 14.5;
washer_face_d = 30.5;
washer_face_t = 3.0;
grip_hex_d = 34;
grip_hex_t = 6;

external_hose_len = washer_face_t + grip_hex_t + ght_thread_len + 8;

function y_axis_angle(from, to) =
    atan2(to[0] - from[0], to[2] - from[2]);

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
    // A shallow skid gives the part a stable print face and helps it ride the
    // sand bed without a fragile knife edge.
    hull() {
        translate([2, 0, -(mouth_outer_minor / 2) - 1.2])
            cube([14, mouth_outer_major * 0.78, 2.4], center = true);

        translate([barb_start - 8, 0, -(throat_id / 2) - wall - 0.8])
            cube([16, throat_id + 12, 2.0], center = true);
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
    slices_per_turn = 28;

    linear_extrude(
        height = length,
        twist = -360 * length / pitch,
        slices = max(20, ceil(length / pitch) * slices_per_turn),
        convexity = 10
    )
        translate([(major_d / 2) - depth - root_overlap, 0, 0])
        polygon([
            [0, -pitch * 0.33],
            [depth + root_overlap, 0],
            [0, pitch * 0.33]
        ]);
}

module male_ght_thread() {
    union() {
        cylinder(h = ght_thread_len, d = ght_minor_d, center = false);

        thread_helix(
            major_d = ght_major_d,
            pitch = ght_pitch,
            length = ght_thread_len,
            depth = ght_thread_depth,
            root_overlap = ght_thread_root_overlap
        );

        translate([0, 0, ght_thread_len])
            cylinder(h = 1.3, d1 = ght_minor_d, d2 = ght_minor_d - 1.2, center = false);
    }
}

module hose_connector_outer() {
    hose_axis() {
        translate([0, 0, -3])
            cylinder(h = washer_face_t + 3, d = washer_face_d, center = false);

        translate([0, 0, washer_face_t])
            cylinder(h = grip_hex_t, d = grip_hex_d, $fn = 6, center = false);

        translate([0, 0, washer_face_t + grip_hex_t])
            male_ght_thread();
    }
}

module venturi_nozzle_outer() {
    union() {
        y_plane_cylinder(jet_plenum, hose_junction, feed_support_od);

        translate(hose_junction)
            sphere(d = feed_support_od);

        translate([jet_plenum[0] - 3, 0, jet_plenum[2]])
            x_taper(jet_exit_x - jet_plenum[0] + 3, jet_body_d, jet_tip_d);
    }
}

module water_path_cuts() {
    hose_axis()
        translate([0, 0, -1])
        cylinder(h = external_hose_len + 11, d = feed_bore_d, center = false);

    y_plane_cylinder(jet_plenum, hose_junction, feed_bore_d);

    translate([jet_plenum[0] - 1.8, 0, jet_plenum[2]])
        x_taper(jet_exit_x - jet_plenum[0] - nozzle_straight_len + 1.8, feed_bore_d, nozzle_orifice_d);

    translate([jet_exit_x - nozzle_straight_len, 0, jet_plenum[2]])
        x_taper(nozzle_straight_len + 1.2, nozzle_orifice_d, nozzle_orifice_d);
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
