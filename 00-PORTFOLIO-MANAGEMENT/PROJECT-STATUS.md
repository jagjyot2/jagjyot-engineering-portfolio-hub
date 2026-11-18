# Portfolio Project Status

**Updated**: `2026-11-18` (Phase 2 — Independent Engineering Verification & Hardware Readiness Complete)

| Project | Domain | Hardware / KiCad Status | Software / Simulation Verification | Readiness Verdict |
|---|---|---|---|---|
| `01-AEROLENS` | CV / Perception | Software-only | Existing portfolio baseline | Baseline Complete |
| `02-SARVISION` | Search & Rescue CV | Software-only | Existing portfolio baseline | Baseline Complete |
| `03-SWARMFORGE` | Multi-Agent Autonomy | Software-only | Existing portfolio baseline | Baseline Complete |
| `04-FLIGHTCORE` | Telemetry Logger + LoRa | KiCad 10.0.8 ERC/DRC `0/0` (`flightcore_{erc,drc}`); [Manufacturing Readiness](../04-FLIGHTCORE/hardware/MANUFACTURING-READINESS.md) | `20/20` pytest + MSVC C++ native tests (`exit 0`) | **`HOLD FAB`** (60 A power-bus trace width & 4-wire Kelvin remediation required) |
| `05-ROVERSAR` | Autonomous SAR Rover | KiCad 10.0.8 ERC/DRC `0/0` (`roversar_{erc,drc}`); [Manufacturing Readiness](../05-ROVERSAR/hardware/MANUFACTURING-READINESS.md) | `20/20` pytest passed (`exit 0`) | **`PROVISIONAL / HOLD`** (`F1`/`SW1` footprint & power-trace upgrades needed) |
| `06-CELLGUARD` | 6S BMS Monitor | KiCad 10.0.8 ERC/DRC `0/0` (`cellguard_{erc,drc}`); [Manufacturing Readiness](../06-CELLGUARD/hardware/MANUFACTURING-READINESS.md) | `23/23` pytest passed (`exit 0`) | **`HOLD FAB`** (2 oz copper pour upgrade for 50 A + JST-XH `2.50 mm` headers needed) |
| `07-PORTFOLIO-WEBSITE` | Web Showcase | Software-only | Existing portfolio baseline | Baseline Complete |
| `08-NIDAR-VEGAPILOT-ARIES-V3` | **Private** Flight Controller Project | KiCad 10.0.8 ERC/DRC `0/0`; hardware fabrication **HOLD** (audited inside private repo) | `15/15` pytest (incl. C `-DHOST_SIM=1` harness + 6-DoF SITL) & `7/7` scenario profiles passed; target silicon deploy **`HOLD`** | **`HOLD FAB & HOLD FLIGHT`** (details restricted to private repo) |

- **KiCad Automation (`00-PORTFOLIO-MANAGEMENT/kicad-automation/`)**: KiCad `10.0.8` CLI verification active across all 4 hardware PCBs (`run-erc.ps1`, `run-drc.ps1`).
