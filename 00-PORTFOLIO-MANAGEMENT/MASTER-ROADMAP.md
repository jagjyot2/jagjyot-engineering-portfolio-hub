# Portfolio Master Roadmap

## Phase 1 — Infrastructure & Baseline Systems (Completed)
- KiCad `10.0.8` environment detection & shared automation toolkit (`kicad-automation/`).
- Public hardware/simulation baselines for `04-FLIGHTCORE`, `05-ROVERSAR`, and `06-CELLGUARD`.
- Initial architecture and simulation pipeline established in private repository `08-NIDAR-VEGAPILOT-ARIES-V3`.

## Phase 2 — Independent Engineering Verification & Hardware Readiness (Completed `2026-11-18`)
- Independent KiCad `10.0.8` ERC/DRC re-execution, Gerber/drill verification, S-expression PCB geometry/net-width inspection, and per-board `MANUFACTURING-READINESS.md` generation across all 4 hardware PCBs (`04`, `05`, `06`, `08`).
- Full regression re-run of `78` pytest tests (`20` FlightCore + `20` RoverSAR + `23` CellGuard + `15` private NIDAR VEGAPilot tests including native C11 `-DHOST_SIM=1` checks and abnormal fault injection).
- Honest readiness classification assigning fabrication `HOLD` gates where trace ampacity, footprint accuracy, or silicon register alignment remains unverified or failed.

## Phase 3 — Hardware Remediation & Bench bring-up (Upcoming)
- Upgrade `04-FLIGHTCORE`, `05-ROVERSAR`, and `06-CELLGUARD` footprints/copper pours for clean DFM release (`2 oz` Cu / polygon pours for high-current paths, keyed `2.50 mm` JST-XH footprints, ATO fuse clip on `05-ROVERSAR`).
- Address private `08-NIDAR-VEGAPILOT-ARIES-V3` blockers against official vendor hardware/SDK documentation prior to carrier fabrication and hardware-in-the-loop bench testing.
