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
- Default STL triangles: `28738`
- Source-model bounding box: about `180.1 mm x 84.8 mm x 77.6 mm`
- X1C 3MF vertical print bounds: about `84.8 mm x 77.6 mm x 180.1 mm`
- Estimated model volume from STL: about `90.2 cm3`
- Non-manifold edges: `0` in the regenerated STL variants and Bambu 3MF
- Connected mesh components: `1`
- OpenSCAD export completed without warnings

Iteration review:

| Iteration | Change | Reason |
|---|---|---|
| V1 | Straight taper, vertical hose boss, `30 mm` tube, `5.8 mm` jet | Proved the eductor path but made the hose connector too tall and left no deliberate suction throat. |
| V2 | Larger mouth, `27.5 mm` throat, flat print skid, vertical/upward hose boss, smaller `5.4 mm` jet | Improved pickup and printability, but the hose connector was still not close enough to the original low-profile orientation. |
| V3 | `76 x 48 mm` mouth, `26 mm` throat, `31 mm` outlet, low rearward hose boss, `5.8 mm` recommended jet | Kept a large sand opening while increasing throat velocity and keeping the garden hose angled up/rearward away from the sand bed. |
| V4 | Replaced the wide bottom plate with a narrow center skid, added a thin printable keel under the internal jet, and strengthened the garden-hose thread | Addresses the first print failure where the center jet printed as unsupported spaghetti and the hose thread did not survive visibly. |
| V5 | Tightened the hose-thread dimensions to a print-fit `26.9 mm` major diameter and corrected the Bambu 3MF PETG profile metadata | Keeps the visible printable thread while avoiding an oversized male fitting, and prevents the 3MF from importing with PLA temperatures. |
| V6 | Disabled the bottom skid by default, changed the X1C 3MF to vertical mouth-down printing, and replaced the hard pressure-feed turn with a smoother curved feed | Removes the unwanted bottom plate, minimizes support needs, and makes the pressure-water path less abrupt. |
| V7 | Deepened the garden-hose thread grooves while keeping the `26.9 mm` outside diameter | Makes the hose-thread form visibly present in Bambu Studio and more likely to survive PETG printing without making the male adapter oversized. |
| V8 | Switched the pressure-water connector to a female/internal GHT socket and disabled supports in the PLA 3MF | Matches the prototype fit feedback: the hose now screws into the tool instead of over an external male thread, and support material is kept out of the internal threads. |

Flow path check:

- Sand enters through a large `76 mm x 48 mm` elliptical mouth.
- The mouth area is about `2865 mm2`.
- The flow converges into a `26 mm` suction throat with area about `531 mm2`.
- Mouth-to-throat area ratio is about `5.4:1`, so the mouth resists clogging while the throat keeps slurry velocity high.
- Pressure water enters through a low-profile garden-hose boss angled about `14 degrees` upward from the body axis toward the exhaust side.
- The feed now follows a smoother curved path into the plenum and exits through a downstream-facing jet on the centerline of the throat.
- The `7.4 mm` nozzle tip leaves about `488 mm2` of annular suction area in the `26 mm` throat.
- The lower printable keel under the jet is estimated to occupy about `29 mm2`, leaving about `459 mm2` of annular slurry area around the jet tip.
- The outlet diffuses to `31 mm` and then into the nominal `1-1/4 in.` exhaust barb.

Garden-hose connection:

- Thread form: female/internal printable approximation of straight `3/4-11.5 GHT/NH`.
- Pitch: `2.2087 mm`.
- Socket outer diameter: `33.0 mm`.
- Internal thread crest diameter: about `24.8 mm`.
- Internal thread groove diameter: about `27.4 mm`.
- Radial thread depth: about `1.4 mm`, with a wider flat crest/groove for FDM survivability.
- Seal: relies on a real garden-hose washer, not thread taper.

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

- Print vertically with the large pickup mouth on the build plate and the exhaust barb upward.
- Do not use slicer auto-orient if it changes this mouth-down orientation; the intended 3MF bounds are about `85 x 78 x 180 mm`.
- Use PETG, ASA, or ABS. Avoid PLA for hot sun and threaded hose stress.
- Use at least `5` walls, `6` top/bottom layers, and `40-60%` infill.
- The PLA 3MF is encoded for Bambu PLA Basic, `220 C` first layer / `215 C` print temperature, `6` walls, `6` top/bottom layers, `30%` gyroid infill, `10 mm` brim, and supports disabled.
- Avoid supports in the slurry path, water jet path, and female hose-thread socket. If support is required, use painted external support only.
- Seal the printed garden-hose thread and any visible layer porosity with epoxy or polyurethane if it leaks.
- The old bottom skid is still available as `bottom_skid_enabled = true`, but the default model and X1C 3MF do not include it.

Remaining risks:

- This is a geometric and first-order hydraulic review, not CFD validation.
- The printed GHT thread may leak or wear. A real hose washer is required, and overtightening may damage the print. The thread is intentionally more pronounced than the earlier version so it survives FDM printing better.
- Sand transport still depends on priming the exhaust hose and keeping it continuously downhill.
- If suction is weak, print the `5.4 mm` nozzle variant.
- If it moves water but not enough sand, and supply pressure is strong, print the `6.2 mm` nozzle variant.
