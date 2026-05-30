# Sand Vac Design Review

Generated outputs:

- `renders/sand_vac_head.stl`: default `5.8 mm` nozzle
- `renders/sand_vac_head_5p4_high_velocity.stl`: smaller nozzle, lower water demand
- `renders/sand_vac_head_5p8_recommended.stl`: recommended first print
- `renders/sand_vac_head_6p2_high_flow.stl`: larger nozzle, needs a strong water supply
- `renders/head.png`
- `renders/section.png`
- `renders/flow_check.png`

OpenSCAD export:

- OpenSCAD version: `2021.01`
- Default STL triangles: `17806`
- Bounding box: about `185.0 mm x 84.8 mm x 79.5 mm`
- Estimated model volume from STL: about `114.9 cm3`
- Non-manifold edges: `0` in the regenerated STL variants and Bambu 3MF
- Connected mesh components: `1`
- OpenSCAD export completed without warnings

Iteration review:

| Iteration | Change | Reason |
|---|---|---|
| V1 | Straight taper, vertical hose boss, `30 mm` tube, `5.8 mm` jet | Proved the eductor path but made the hose connector too tall and left no deliberate suction throat. |
| V2 | Larger mouth, `27.5 mm` throat, flat print skid, vertical/upward hose boss, smaller `5.4 mm` jet | Improved pickup and printability, but the hose connector was still not close enough to the original low-profile orientation. |
| V3 | `76 x 48 mm` mouth, `26 mm` throat, `31 mm` outlet, low rearward hose boss, `5.8 mm` recommended jet | Current design. It keeps a large sand opening while increasing throat velocity and keeping the garden hose angled up/rearward away from the sand bed. |

Flow path check:

- Sand enters through a large `76 mm x 48 mm` elliptical mouth.
- The mouth area is about `2865 mm2`.
- The flow converges into a `26 mm` suction throat with area about `531 mm2`.
- Mouth-to-throat area ratio is about `5.4:1`, so the mouth resists clogging while the throat keeps slurry velocity high.
- Pressure water enters through a low-profile garden-hose boss angled about `14 degrees` upward from the body axis toward the exhaust side.
- The feed turns down to a plenum and exits through a downstream-facing jet on the centerline of the throat.
- The `7.4 mm` nozzle tip leaves about `488 mm2` of annular suction area in the `26 mm` throat.
- The outlet diffuses to `31 mm` and then into the nominal `1-1/4 in.` exhaust barb.

Nozzle options:

| Nozzle | Estimated flow at 40 psi | Estimated flow at 50 psi | Estimated flow at 60 psi | Use case |
|---|---:|---:|---:|---|
| `5.4 mm` | `5.3-6.4 gpm` | `5.9-7.2 gpm` | `6.5-7.8 gpm` | Weak supply, long garden hose, or if the larger nozzle cannot stay primed. |
| `5.8 mm` | `6.1-7.4 gpm` | `6.8-8.3 gpm` | `7.5-9.0 gpm` | Recommended first print. Best balance for a normal `5/8 in.` garden hose. |
| `6.2 mm` | `7.0-8.4 gpm` | `7.8-9.4 gpm` | `8.5-10.3 gpm` | Strong supply and short garden hose. Highest driving water flow but more sensitive to hose pressure loss. |

Assessment:

The current design uses the right eductor geometry for removing a large amount of pool-filter sand: a high-speed pressure jet discharges downstream inside a smaller throat, entraining sand/water from a much larger pickup mouth. The large mouth prevents wet sand from bridging at the opening, while the controlled `26 mm` throat keeps slurry velocity high enough to move sand into the exhaust hose.

The hose connector is now low and rearward/upward, closer to the original part. With the scoop on the sand bed, the connected garden hose should naturally lead up and away from the bottom rather than pushing directly into the sand.

Printability review:

- Print with the flat skid on the build plate.
- Do not use slicer auto-orient if it stands the part upright at about `185 mm` tall. That orientation puts the exhaust path vertical; the intended print orientation is the low `185 x 85 x 79 mm` skid-down footprint.
- Use PETG, ASA, or ABS. Avoid PLA for hot sun and threaded hose stress.
- Use at least `5` walls, `6` top/bottom layers, and `40-60%` infill.
- Avoid internal supports in the slurry path or water jet path.
- If the slicer insists on supports, use build-plate-only or painted supports under the external hose boss and thread area.
- Seal the printed garden-hose thread and any visible layer porosity with epoxy or polyurethane if it leaks.

Remaining risks:

- This is a geometric and first-order hydraulic review, not CFD validation.
- The printed GHT thread may leak or wear. A real hose washer is required, and overtightening may damage the print.
- Sand transport still depends on priming the exhaust hose and keeping it continuously downhill.
- If suction is weak, print the `5.4 mm` nozzle variant.
- If it moves water but not enough sand, and supply pressure is strong, print the `6.2 mm` nozzle variant.
