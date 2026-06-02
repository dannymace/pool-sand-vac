# Pool Sand Vac Print

This is a printable functional pool sand filter vac head. Its purpose is to remove sand from a sand filter.

Files:

- `sand_vac_head.scad`: parametric OpenSCAD model for the scoop body and injector
- `DESIGN_REVIEW.md`: render/export notes and first-order venturi/eductor analysis
- `renders/sand_vac_head.stl`: exported default STL with the recommended `5.8 mm` nozzle
- `renders/sand_vac_head_5p4_high_velocity.stl`: lower-flow nozzle variant
- `renders/sand_vac_head_5p8_recommended.stl`: recommended first print
- `renders/sand_vac_head_6p2_high_flow.stl`: higher-flow nozzle variant
- `renders/sand_vac_head_X1C_PETG_strong.3mf`: Bambu Lab X1C-oriented 3MF using the recommended `5.8 mm` nozzle
- `renders/head.png`: full render
- `renders/hose_thread_closeup.png`: close-up render of the garden-hose thread
- `renders/section.png`: cutaway render
- `renders/flow_check.png`: cutaway render with colored flow paths
- `README_PRINT_X1C.md`: X1C-specific print settings and preflight check

CadQuery/STEP package files:

- `build_step_master.py`: rebuilds the editable STEP/STL package from the current smoothed geometry
- `make_bambu_3mf.py`: regenerates the vertical PLA prototype 3MF from the combined STL
- `VERSION`: package version for the STEP/CadQuery export set
- `fusion_thread_data/GardenHoseThreads.xml`: optional Fusion 360 thread profile for an editable `3/4-11.5 GHT` thread feature
- `out/sand_vac_head_combined_smooth.step`: preferred editable combined STEP
- `out/sand_vac_head_combined_smooth.stl`: matching combined STL
- `out/sand_vac_head_clean_master.step`: compatibility alias for the combined STEP
- `out/sand_vac_head_clean_master.stl`: compatibility alias for the combined STL
- `out/sand_vac_head_venturi_insert.step`: separate pressure-feed venturi insert STEP
- `out/sand_vac_head_venturi_insert.stl`: separate pressure-feed venturi insert STL
- `out/sand_vac_head_combined_smooth_vertical_PLA.3mf`: Bambu Studio-style vertical PLA prototype project

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
- Print vertically with the large pickup mouth on the build plate and the exhaust barb upward
- Do not use slicer auto-orient if it changes this mouth-down orientation; the intended 3MF bounds are about `85 x 78 x 180 mm`
- Supports should be disabled by default so the slurry path and water-jet path stay clear
- If your slicer insists on supports, use painted supports externally only and keep support out of the mouth, throat, and nozzle

PLA prototype 3MF:

- `out/sand_vac_head_combined_smooth_vertical_PLA.3mf` is intended for a PLA prototype print in Bambu Studio.
- It rotates the STEP-derived combined body upright, giving about a `77 x 85 mm` bed footprint and `218 mm` print height.
- The embedded prototype preset uses `0.20 mm` baseline layers, variable layers down to `0.12 mm` near the hose-thread zone, `6` walls, `6` top/bottom layers, `30%` gyroid infill, tree/auto supports, and a `10 mm` brim.
- It is a slicer project, not sliced G-code; it reuses the known-good Bambu project container layout and should be opened in Bambu Studio so you can confirm the selected printer, plate, and loaded PLA before printing.

STEP/Fusion workflow:

1. Install CadQuery 2.4+ or open the script in CQ-editor.
2. Run `build_step_master.py`.
3. Run `make_bambu_3mf.py` if you want to regenerate the vertical PLA prototype print project.
4. Import `out/sand_vac_head_combined_smooth.step` into Fusion 360.
5. Inspect the included garden-hose thread; replace it with `fusion_thread_data/GardenHoseThreads.xml` only if you need an editable Fusion Thread feature.

Notes on fit and tuning:

- The hose-side thread is a printable approximation of `3/4-11.5 GHT` with a `26.9 mm` major diameter, about `23.8 mm` root diameter, and an intentionally aggressive flat crest/groove so it is visible in PETG. It should be treated as a first-pass fit, not a guaranteed production thread.
- The nozzle orifice is parameterized with `nozzle_orifice_d_override`. Start with the `5.8 mm` recommended STL. If suction is weak, try `5.4 mm`. If flow is too restricted and your water supply is strong, try `6.2 mm`.
- The exhaust barb is sized for nominal `1-1/4"` corrugated pool hose. Hose tolerances vary. If your hose is loose or tight, adjust `barb_peak_d` by about `0.5 mm`.
- For reliable pressure handling, seal any visibly porous interior print surfaces with epoxy or polyurethane sealant.
- Keep the exhaust hose continuously sloping downward during use. Pentair's published instructions for the original tool call this out because any uphill section lets sand collect in the discharge hose.

Model note:

- The STEP rebuild follows the current OpenSCAD geometry closely for the main body, diffuser, outlet barb, hose angle, feed bore, and venturi path.
- The pressure-feed tube is fused into the hose connector with an enlarged socket and blend so the printed water path is sealed at that junction.
- The pressure-feed curve starts at the hose junction face so the bore and swept venturi tube overlap instead of leaving an exposed side opening in the feed path.
- The venturi throat keeps about `57 mm` of straight post-jet mixing length (`2.19x` the `26 mm` throat diameter) before the diffuser.
- The pressure nozzle tip has a `1.4 mm` radial wall around the `5.8 mm` orifice.
- The preferred combined STEP is one re-importable solid and uses the same functional boolean order as the OpenSCAD STL: hollow slurry body first, then hose boss and venturi insert, then pressure-water bore cut.

What I based this on:

- Product dimensions and fitment notes from Pool Warehouse
- Operating instructions and hose sizes from INYOPools
- Current product photos from both sellers to infer the head layout and inlet/outlet arrangement

Current design assumptions:

- Exhaust hose: `1-1/4"` nominal
- Garden hose connection: standard US female hose end screwing onto a male fitting on the injector
- Household water pressure: roughly `40-60 psi`

Because eductor tools are sensitive to nozzle geometry, expect one tuning cycle after the first print. Three nozzle-size STL variants are included so the first test does not require editing the SCAD.

The old bottom skid is still available in the SCAD as `bottom_skid_enabled = true`, but it is disabled in the default model and the X1C 3MF.
