# KiCad 10.0.8 Shared Engineering Automation Toolkit

Centralized KiCad electronics automation suite for `ENGINEERING-PORTFOLIO` hardware projects (`04-FLIGHTCORE`, `05-ROVERSAR`, `06-CELLGUARD`, and `08-NIDAR-VEGAPILOT-ARIES-V3`).

## Detected Toolchain (`kicad-config.json`)
- **KiCad Version**: `10.0.8`
- **Install Dir**: `C:\Program Files\KiCad\10.0`
- **CLI**: `C:\Program Files\KiCad\10.0\bin\kicad-cli.exe`
- **Python `pcbnew` API**: `C:\Program Files\KiCad\10.0\bin\python.exe` (`10.0.8`)

## PowerShell Scripts
- `.\kicad-automation\detect-kicad.ps1` — Auto-discovers installed KiCad executables, libraries, 3D models, and Python scripting support; updates `kicad-config.json`.
- `.\kicad-automation\new-project.ps1` — Scaffolds a KiCad 10 project (`.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, `sym-lib-table`, `fp-lib-table`, project libraries).
- `.\kicad-automation\generate-pcb.ps1` — Invokes project generator or verifies schematic-to-PCB netlist & copper zone refill.
- `.\kicad-automation\run-erc.ps1` — Runs `kicad-cli sch erc --severity-all --exit-code-violations`.
- `.\kicad-automation\run-drc.ps1` — Runs `kicad-cli pcb drc --refill-zones --save-board --schematic-parity --exit-code-violations`.
- `.\kicad-automation\export-gerbers.ps1` — Exports 2-layer fabrication Gerbers (`F.Cu`, `B.Cu`, masks, silkscreens, paste, `Edge.Cuts`) + Excellon PTH/NPTH drill files & map.
- `.\kicad-automation\export-bom.ps1` — Exports engineering BOM CSV with MPN, Manufacturer, Rating, Origin, Qty.
- `.\kicad-automation\build-all.ps1` — Full pipeline: ERC -> Netlist -> DRC/Zone-Fill/Parity -> Gerbers + Drill -> BOM -> STEP/GLB/PNG 3D renders -> `DESIGN-VALIDATION-REPORT.md`.

## Python Core (`kicad_toolkit.py`)
Provides `SchematicBuilder`, `PCBBuilder`, lockstep `.kicad_sym` / `.kicad_mod` library emitters, `1.27 mm` exact grid enforcement, and UTF-8 (no-BOM) writers required by KiCad 10 CLI.
