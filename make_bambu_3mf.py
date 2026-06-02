#!/usr/bin/env python3
"""Create a Bambu Studio oriented 3MF project for the sand vac head."""

from __future__ import annotations

import datetime as dt
import json
import math
import os
import struct
import xml.sax.saxutils as xml_escape
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
SOURCE_STL = OUT / "sand_vac_head_combined_smooth.stl"
TARGET_3MF = OUT / "sand_vac_head_combined_smooth_vertical_PLA.3mf"
TEMPLATE_3MF = ROOT / "renders" / "sand_vac_head_X1C_PETG_strong.3mf"
TEMPLATE_SETTINGS = (
    Path(os.environ.get("TEMP", ""))
    / "bambu_3mf_inspect"
    / "Metadata"
    / "project_settings.config"
)


def read_stl(path: Path) -> list[tuple[tuple[float, float, float], ...]]:
    data = path.read_bytes()
    if len(data) >= 84:
        tri_count = struct.unpack_from("<I", data, 80)[0]
        expected = 84 + tri_count * 50
        if expected == len(data):
            triangles = []
            offset = 84
            for _ in range(tri_count):
                coords = struct.unpack_from("<12f", data, offset)
                triangles.append((coords[3:6], coords[6:9], coords[9:12]))
                offset += 50
            return triangles

    triangles: list[tuple[tuple[float, float, float], ...]] = []
    vertices: list[tuple[float, float, float]] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        parts = line.strip().split()
        if len(parts) == 4 and parts[0].lower() == "vertex":
            vertices.append(tuple(float(x) for x in parts[1:4]))
            if len(vertices) == 3:
                triangles.append(tuple(vertices))
                vertices = []
    if not triangles:
        raise ValueError(f"Could not parse STL: {path}")
    return triangles


def rotate_upright(
    triangles: list[tuple[tuple[float, float, float], ...]],
) -> tuple[list[tuple[tuple[float, float, float], ...]], dict[str, float]]:
    """Rotate the long original X axis to Z for vertical printing.

    Keep the object centered on local X/Y and use the 3MF build transform to
    place it on the plate. This mirrors Bambu Studio project exports.
    """
    transformed = []
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []

    for tri in triangles:
        new_tri = []
        for x, y, z in tri:
            nx, ny, nz = z, y, x
            new_tri.append((nx, ny, nz))
            xs.append(nx)
            ys.append(ny)
            zs.append(nz)
        transformed.append(tuple(new_tri))

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    min_z, max_z = min(zs), max(zs)
    shift_x = -(min_x + max_x) / 2.0
    shift_y = -(min_y + max_y) / 2.0
    shift_z = -min_z

    shifted = []
    for tri in transformed:
        shifted.append(
            tuple((x + shift_x, y + shift_y, z + shift_z) for x, y, z in tri)
        )

    stats = {
        "min_x": min_x + shift_x,
        "max_x": max_x + shift_x,
        "min_y": min_y + shift_y,
        "max_y": max_y + shift_y,
        "min_z": 0.0,
        "max_z": max_z + shift_z,
    }
    return shifted, stats


def write_root_model() -> str:
    today = dt.date.today().isoformat()
    return "".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>\n',
            '<model unit="millimeter" xml:lang="en-US" ',
            'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" ',
            'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" ',
            'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" requiredextensions="p">\n',
            ' <metadata name="Application">BambuStudio-02.07.00.55</metadata>\n',
            ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n',
            f' <metadata name="CreationDate">{today}</metadata>\n',
            f' <metadata name="ModificationDate">{today}</metadata>\n',
            ' <metadata name="Title">Sand Vac Head Vertical PLA Prototype</metadata>\n',
            " <resources>\n",
            '  <object id="2" name="sand_vac_head_combined_smooth_vertical_PLA" p:UUID="00000009-61cb-4c03-9d28-80fed5dfa1dc" type="model">\n',
            "   <components>\n",
            '    <component p:path="/3D/Objects/object_9.model" objectid="1" p:UUID="00090000-b206-40ff-9872-83e8017abed1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n',
            "   </components>\n",
            "  </object>\n",
            " </resources>\n",
            ' <build p:UUID="2c7c17d8-22b5-4d84-8835-1976022ea369">\n',
            '  <item objectid="2" p:UUID="00000002-b1ec-4553-aec9-835e5b724bb4" transform="1 0 0 0 1 0 0 0 1 128 128 0" printable="1"/>\n',
            " </build>\n",
            "</model>\n",
        ]
    )


def indexed_mesh(
    triangles: list[tuple[tuple[float, float, float], ...]],
) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    vertices: list[tuple[float, float, float]] = []
    vertex_index: dict[tuple[float, float, float], int] = {}
    indexed_triangles: list[tuple[int, int, int]] = []

    for tri in triangles:
        ids = []
        for point in tri:
            key = tuple(round(coord, 6) for coord in point)
            if key not in vertex_index:
                vertex_index[key] = len(vertices)
                vertices.append(key)
            ids.append(vertex_index[key])
        indexed_triangles.append(tuple(ids))

    return vertices, indexed_triangles


def write_object_model(triangles: list[tuple[tuple[float, float, float], ...]]) -> str:
    vertices, indexed_triangles = indexed_mesh(triangles)
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<model unit="millimeter" xml:lang="en-US" ',
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" ',
        'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" ',
        'requiredextensions="p">\n',
        " <resources>\n",
        '  <object id="1" name="sand_vac_head_combined_smooth_vertical_PLA.stl" type="model" p:UUID="00090000-b206-40ff-9872-83e8017abed1">\n',
        "   <mesh>\n",
        "    <vertices>\n",
    ]
    for x, y, z in vertices:
        out.append(f'     <vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>\n')
    out.extend(["    </vertices>\n", "    <triangles>\n"])
    for v1, v2, v3 in indexed_triangles:
        out.append(f'     <triangle v1="{v1}" v2="{v2}" v3="{v3}"/>\n')
    out.extend(
        [
            "    </triangles>\n",
            "   </mesh>\n",
            "  </object>\n",
            " </resources>\n",
            " <build />\n",
            "</model>\n",
        ]
    )
    return "".join(out)


def set_all(settings: dict, key: str, value: str) -> None:
    if key not in settings:
        settings[key] = value
        return
    old = settings[key]
    if isinstance(old, list):
        settings[key] = [value for _ in old]
    else:
        settings[key] = value


def load_project_settings() -> dict:
    if TEMPLATE_3MF.exists():
        with zipfile.ZipFile(TEMPLATE_3MF) as zf:
            settings = json.loads(
                zf.read("Metadata/project_settings.config").decode("utf-8")
            )
    elif TEMPLATE_SETTINGS.exists():
        settings = json.loads(TEMPLATE_SETTINGS.read_text(encoding="utf-8"))
    else:
        settings = {}

    scalar_updates = {
        "layer_height": "0.20",
        "initial_layer_print_height": "0.24",
        "min_layer_height": "0.08",
        "max_layer_height": "0.28",
        "wall_loops": "6",
        "top_shell_layers": "6",
        "bottom_shell_layers": "6",
        "sparse_infill_density": "30%",
        "sparse_infill_pattern": "gyroid",
        "enable_support": "1",
        "support_type": "tree(auto)",
        "support_threshold_angle": "50",
        "support_on_build_plate_only": "0",
        "support_interface_top_layers": "3",
        "support_interface_bottom_layers": "2",
        "support_top_z_distance": "0.20",
        "support_bottom_z_distance": "0.20",
        "support_object_xy_distance": "0.35",
        "support_remove_small_overhang": "1",
        "tree_support_branch_angle": "45",
        "tree_support_branch_diameter": "2",
        "tree_support_branch_distance": "5",
        "brim_type": "outer_only",
        "brim_width": "10",
        "brim_object_gap": "0.1",
        "seam_position": "aligned",
        "apply_scarf_seam_on_circles": "1",
        "bridge_speed": "40",
        "outer_wall_speed": "55",
        "inner_wall_speed": "120",
        "sparse_infill_speed": "140",
        "support_speed": "100",
        "support_interface_speed": "60",
        "initial_layer_speed": "35",
        "initial_layer_infill_speed": "45",
        "detect_thin_wall": "1",
        "detect_overhang_wall": "1",
        "elefant_foot_compensation": "0.15",
    }
    for key, value in scalar_updates.items():
        set_all(settings, key, value)

    list_updates = {
        "default_filament_profile": ["Bambu PLA Basic @BBL X1C"],
        "filament_settings_id": ["Bambu PLA Basic @BBL X1C"],
        "filament_type": ["PLA"],
        "filament_colour": ["#D8D8D8"],
        "nozzle_temperature": ["215"],
        "nozzle_temperature_initial_layer": ["220"],
        "hot_plate_temp": ["55"],
        "hot_plate_temp_initial_layer": ["60"],
        "textured_plate_temp": ["55"],
        "textured_plate_temp_initial_layer": ["60"],
        "cool_plate_temp": ["35"],
        "cool_plate_temp_initial_layer": ["35"],
        "fan_min_speed": ["100"],
        "fan_max_speed": ["100"],
        "first_x_layer_fan_speed": ["0"],
        "close_fan_the_first_x_layers": ["3"],
        "additional_cooling_fan_speed": ["20"],
        "filament_max_volumetric_speed": ["12"],
    }
    for key, value in list_updates.items():
        settings[key] = value

    settings["print_sequence"] = "by layer"
    settings["curr_bed_type"] = "Textured PEI Plate"
    settings["from"] = "Sand vac vertical PLA prototype preset"
    return settings


def model_settings_xml(face_count: int, height: float) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<config>
  <object id="2">
    <metadata key="name" value="sand_vac_head_combined_smooth_vertical_PLA"/>
    <metadata key="extruder" value="1"/>
    <metadata key="support_threshold_angle" value="50"/>
    <metadata key="support_type" value="tree(auto)"/>
    <metadata face_count="{face_count}"/>
    <part id="1" subtype="normal_part">
      <metadata key="name" value="sand_vac_head_combined_smooth_vertical_PLA"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <metadata key="source_file" value="{xml_escape.escape(SOURCE_STL.name)}"/>
      <metadata key="source_object_id" value="0"/>
      <metadata key="source_volume_id" value="0"/>
      <metadata key="source_offset_x" value="0"/>
      <metadata key="source_offset_y" value="0"/>
      <metadata key="source_offset_z" value="0"/>
      <mesh_stat face_count="{face_count}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>
    </part>
  </object>
  <plate>
    <metadata key="plater_id" value="1"/>
    <metadata key="plater_name" value="Plate 1"/>
    <metadata key="locked" value="false"/>
    <metadata key="filament_map_mode" value="Auto For Flush"/>
    <metadata key="filament_maps" value="1"/>
    <metadata key="filament_volume_maps" value="0"/>
    <metadata key="printable_height" value="{height:.3f}"/>
    <model_instance>
      <metadata key="object_id" value="2"/>
      <metadata key="instance_id" value="0"/>
      <metadata key="identify_id" value="159"/>
    </model_instance>
  </plate>
  <assemble>
    <assemble_item object_id="2" instance_id="0" transform="1 0 0 0 1 0 0 0 1 128 128 0" offset="0 0 0" />
  </assemble>
</config>
"""


def layer_profile(height: float) -> str:
    # Use finer layers around the hose-thread/connector zone and end details.
    points: list[tuple[float, float]] = []
    z = 0.0
    while z <= height + 0.01:
        if z < 2.0:
            lh = 0.24
        elif z < 18.0:
            lh = 0.16
        elif 65.0 <= z <= 96.0:
            lh = 0.12
        elif z > height - 24.0:
            lh = 0.16
        else:
            lh = 0.20
        points.append((min(z, height), lh))
        z += max(lh, 0.08)
    if points[-1][0] < height:
        points.append((height, points[-1][1]))
    return "object_id=1|" + ";".join(f"{z:.6f};{lh:.6f}" for z, lh in points)


def package() -> None:
    triangles = read_stl(SOURCE_STL)
    upright, stats = rotate_upright(triangles)
    height = stats["max_z"] - stats["min_z"]
    root_model_xml = write_root_model()
    object_model_xml = write_object_model(upright)
    project_settings = load_project_settings()
    notes = "\n".join(
        [
            "Sand vac head vertical PLA prototype preset.",
            "Orientation: original long X axis rotated to Z; print height about "
            f"{height:.1f} mm.",
            "Layering: 0.20 mm baseline, variable profile down to 0.12 mm near hose threads.",
            "Strength/water sealing: 6 walls, 6 top/bottom layers, 30% gyroid infill.",
            "Supports: tree/auto support enabled with interfaces; inspect before slicing.",
            "Adhesion: 10 mm brim for vertical print stability.",
            "PLA: 220 C first layer, 215 C print, 60/55 C textured or hot plate.",
        ]
    )

    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Default Extension="gcode" ContentType="text/x.gcode"/>
</Types>
"""
    root_rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
"""
    model_rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/Objects/object_9.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
"""
    slice_info = """<?xml version="1.0" encoding="UTF-8"?>
<config>
  <header>
    <metadata key="application" value="BambuStudio"/>
    <metadata key="version" value="02.07.00.55"/>
  </header>
</config>
"""
    cut_info = """<?xml version="1.0" encoding="UTF-8"?>
<config/>
"""

    replacements = {
        "3D/3dmodel.model",
        "3D/Objects/object_9.model",
        "3D/_rels/3dmodel.model.rels",
        "Metadata/project_settings.config",
        "Metadata/model_settings.config",
        "Metadata/layer_heights_profile.txt",
        "Metadata/filament_sequence.json",
        "Metadata/print_profile_notes.txt",
    }

    with zipfile.ZipFile(TARGET_3MF, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        if TEMPLATE_3MF.exists():
            with zipfile.ZipFile(TEMPLATE_3MF) as template:
                for item in template.infolist():
                    if item.filename in replacements:
                        continue
                    zf.writestr(item, template.read(item.filename))
        else:
            zf.writestr("[Content_Types].xml", content_types)
            zf.writestr("_rels/.rels", root_rels)
            zf.writestr("Metadata/slice_info.config", slice_info)
            zf.writestr("Metadata/cut_information.xml", cut_info)

        zf.writestr("3D/3dmodel.model", root_model_xml)
        zf.writestr("3D/Objects/object_9.model", object_model_xml)
        zf.writestr("3D/_rels/3dmodel.model.rels", model_rels)
        zf.writestr(
            "Metadata/project_settings.config",
            json.dumps(project_settings, indent=2, sort_keys=True),
        )
        zf.writestr("Metadata/model_settings.config", model_settings_xml(len(upright), height))
        zf.writestr("Metadata/layer_heights_profile.txt", layer_profile(height))
        zf.writestr("Metadata/filament_sequence.json", json.dumps({"sequence": [1]}))
        zf.writestr("Metadata/print_profile_notes.txt", notes + "\n")

    print(f"wrote {TARGET_3MF}")
    print(
        "vertical_bounds_mm="
        f"({stats['max_x'] - stats['min_x']:.2f}, "
        f"{stats['max_y'] - stats['min_y']:.2f}, {height:.2f})"
    )
    print(f"triangles={len(upright)}")


if __name__ == "__main__":
    package()
