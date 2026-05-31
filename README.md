# Pool Sand Vac Print

This is a printable functional equivalent of the Pentair `542090` sand vac head. It follows the same basic layout shown in current retail photos: a scoop body, a large exhaust outlet for `1-1/4"` pool hose, and a separate pressurized water jet that drives suction through an eductor effect.

Files:

- `sand_vac_head.scad`: parametric OpenSCAD model for the scoop body and injector
- `DESIGN_REVIEW.md`: render/export notes and first-order venturi/eductor analysis
- `renders/sand_vac_head.stl`: exported default STL with the recommended `5.8 mm` nozzle
- `renders/sand_vac_head_5p4_high_velocity.stl`: lower-flow nozzle variant
- `renders/sand_vac_head_5p8_recommended.stl`: recommended first print
- `renders/sand_vac_head_6p2_high_flow.stl`: higher-flow nozzle variant
- `renders/sand_vac_head_X1C_PETG_strong.3mf`: Bambu Lab X1C-oriented 3MF using the recommended `5.8 mm` nozzle
- `renders/head.png`: full render
- `renders/section.png`: cutaway render
- `renders/flow_check.png`: cutaway render with colored flow paths
- `README_PRINT_X1C.md`: X1C-specific print settings and preflight check

Expected part modes:

- `head`: printable one-piece model
- `section`: y-axis cutaway for checking internal geometry
- `flow_check`: cutaway plus colored flow-path guides for OpenSCAD preview

Recommended starting settings:

- Material: `PETG`, `ASA`, or `ABS`
- Layer height: `0.20 mm`
- Walls: `5+`
- Top/bottom layers: `6+`
- Infill: `40-60%`
- Brim: `5 mm`
- Print the `head` with the narrow center skid on the build plate
- Do not use slicer auto-orient if it stands the part upright; the intended print orientation is the low `187 x 85 x 80 mm` footprint with the skid down
- Avoid supports inside the slurry path or water-jet path
- Use build-plate-only or painted supports only under the external hose boss if your slicer requires them

Notes on fit and tuning:

- The hose-side thread is a printable approximation of `3/4-11.5 GHT` with a `26.9 mm` major diameter and intentionally stronger flat crest. It should be treated as a first-pass fit, not a guaranteed production thread.
- The nozzle orifice is parameterized with `nozzle_orifice_d_override`. Start with the `5.8 mm` recommended STL. If suction is weak, try `5.4 mm`. If flow is too restricted and your water supply is strong, try `6.2 mm`.
- The exhaust barb is sized for nominal `1-1/4"` corrugated pool hose. Hose tolerances vary. If your hose is loose or tight, adjust `barb_peak_d` by about `0.5 mm`.
- For reliable pressure handling, seal any visibly porous interior print surfaces with epoxy or polyurethane sealant.
- Keep the exhaust hose continuously sloping downward during use. Pentair's published instructions for the original tool call this out because any uphill section lets sand collect in the discharge hose.

What I based this on:

- Product dimensions and fitment notes from Pool Warehouse
- Operating instructions and hose sizes from INYOPools
- Current product photos from both sellers to infer the head layout and inlet/outlet arrangement

Current design assumptions:

- Exhaust hose: `1-1/4"` nominal
- Garden hose connection: standard US female hose end screwing onto a male fitting on the injector
- Household water pressure: roughly `40-60 psi`

Because eductor tools are sensitive to nozzle geometry, expect one tuning cycle after the first print. Three nozzle-size STL variants are included so the first test does not require editing the SCAD.
