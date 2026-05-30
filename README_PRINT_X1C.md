# Bambu Lab X1C Print Setup

Prepared file:

- `renders/sand_vac_head_X1C_PETG_strong.3mf`

Packaging note:

- Rebuilt as a native-style Bambu project archive using a known Bambu Studio 3MF layout, not a sparse generic 3MF.

Encoded intent:

- Printer: `Bambu Lab X1 Carbon 0.4 nozzle`
- Filament profile: `Bambu PETG Basic @BBL X1C`
- Process baseline: `0.20mm Strength @BBL X1C`
- Orientation: flat skid on build plate, model centered on X1C bed
- Layer height: `0.20 mm`
- Wall loops: `6`
- Top layers: `7`
- Bottom layers: `7`
- Sparse infill: `45%`
- Infill pattern: `gyroid`
- Supports: enabled
- Support type: `tree(auto)`
- Support limit: `build plate only`
- Support threshold angle: `35 degrees`
- Brim: disabled

Before printing:

- Open the 3MF in Bambu Studio and slice it once before sending.
- In preview, confirm supports are external, mainly under the garden-hose boss and thread.
- Do not print if support appears inside the small water nozzle bore or blocks the suction throat.
- If Bambu Studio drops the partial project settings, manually set the values above.
- Use a real hose washer on the printed garden-hose thread and do not overtighten.

Material note:

PETG is the default because it is water-tolerant and easier than ASA. ASA is also a good choice for outdoor/UV exposure, but switch the filament profile before slicing if using ASA.
