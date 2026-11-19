# Engineering Portfolio — Project Status Overview

> **Portfolio Hub:** `jagjyot2/jagjyot-engineering-portfolio-hub` (Public)
> **Last Updated:** `2026-11-19` — **Phase 3 Defect Remediation & Manufacturing Verification Complete (`78/78` tests passing, `4/4` KiCad `10.0.8` boards `0` ERC/DRC/Parity)**

| Workspace / Project | Repo Visibility | Phase 3 Status | Automated Hardware & Software Verification | Notes |
|---|---|---|---|---|
| `04-FLIGHTCORE` | Public | **REMEDIATED (`READY W/ 2 oz CU NOTE`)** | `0` ERC / `0` DRC / `0` Parity (`49` footprints, `33` nets); **`20/20` `pytest` PASS** | Upgraded to 4-wire Kelvin `R11`, `3.5 mm` dual-layer `F.Cu+B.Cu` `VBAT_IN`/`LOAD`, `4.5 mm` mounting-hole inset, and keyed `2.50 mm` JST-XH headers. |
| `05-ROVERSAR` | Public | **REMEDIATED (`READY FOR PROTOTYPE FAB`)** | `0` ERC / `0` DRC / `0` Parity (`41` footprints, `34` nets); **`20/20` `pytest` PASS** | Upgraded to `9.20 mm` ATO blade fuseholder `F1`, `5.08 mm` terminal `SW1`, 4-pin `ESP32-CAM` UART+power header `U9`, JST-XH `2.50 mm`, `2.0–2.5 mm` battery buses. |
| `06-CELLGUARD` | Public | **REMEDIATED (`READY W/ 2 oz CU NOTE`)** | `0` ERC / `0` DRC / `0` Parity (`75` footprints, `51` nets); **`23/23` `pytest` PASS** | Upgraded to `3.5 mm` dual-layer `F.Cu+B.Cu` high-current buses across Kelvin shunt, single `B.Cu GND` plane, keyed `2.50 mm` JST-XH `J3/J6`, stale `cellguard.drl` removed. |
| `08-NIDAR-VEGAPILOT-ARIES-V3` | **PRIVATE** | **REMEDIATED (`HOLD MASS FAB / FLIGHT`)** | `0` ERC / `0` DRC / `0` Parity (`70` annotated BOM rows); RV32IM ELF `0` warn; **`15/15` `pytest` PASS (`C1..C7` + SITL/HIL)** | Carrier power/footprint/annotation defects and firmware PLIC/IRQ/safety fixes verified in automated checks; mass fab & flight held pending physical board & vendor SDK verification inside private repo. |
| `00-PORTFOLIO-MANAGEMENT` | Public | **ACTIVE** | Shared KiCad `10.0.8` toolkit (`kicad_toolkit.py` + PowerShell CLI scripts) | Reusable ERC/DRC/Gerber/BOM/3D pipeline driving all portfolio PCBs. |
