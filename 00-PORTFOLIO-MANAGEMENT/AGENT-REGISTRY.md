# Autonomous Multi-Agent Registry

| Agent ID | Subagent Type / Role | Conversation ID | Workspace Scope | Responsibilities | Status |
|---|---|---|---|---|---|
| **Agent 00** | Chief Engineering Orchestrator (Coordinator) | Current Session | `00-PORTFOLIO-MANAGEMENT/` | Architecture governance, KiCad 10.0.8 automation toolkit (`kicad-automation/`), hardware audits (`04`–`06`), checkpointing, GitHub orchestration | Active |
| **Agent 01** | `aerolens-engineer` | `0e1c1f83-bbdb-4bc6-8ff3-529143e55ac3` | `01-AEROLENS/` | Flight log parsers, anomaly detection, PDF/CSV/HTML exporter, React+TS dashboard, tests | Running |
| **Agent 02** | `sarvision-engineer` | `8bdbcbd8-185a-4114-b005-0af7d87df6f9` | `02-SARVISION/` | Image tiling, ONNX/OpenCV SAR detector, EXIF GPS projection, P/R evaluation, React+TS UI, tests | Running |
| **Agent 03** | `swarmforge-engineer` | `f8b0385c-c74d-4ab2-9c31-2a6bd911c3e8` | `03-SWARMFORGE/` | 3D multi-UAV physics, A*/RRT*/APF planners, collision/geofence safety, WebSocket + Three.js 3D UI, tests | Running |
| **Agent 04** | `flightcore-engineer` | `6e9a9e08-c8cd-4eae-bd00-1308ee961bfc` | `04-FLIGHTCORE/` | ESP32 PlatformIO telemetry firmware, KiCad schematic/PCB/Gerbers/BOM, BenchTwin prep, tests | Running |
| **Agent 05** | `roversar-engineer` | `efd6fcbb-e302-4d0d-9d51-d79b0094944d` | `05-ROVERSAR/` | ESP32 diff-drive firmware, FastAPI/WebSocket nav simulator, web dashboard, STL CAD, KiCad/BOM, tests | Running |
| **Agent 06** | `cellguard-engineer` | `1db2b32a-bb24-4330-9e85-add8440eb691` | `06-CELLGUARD/` | ESP32 INA226/NTC SoC/SoH firmware, KiCad Kelvin-shunt PCB/Gerbers/Safety, web dashboard, tests | Running |
| **Agent 07** | `portfolio-web-engineer` | `666ef9fc-0dd0-43d8-9048-3be17ccfc6f1` | `07-PORTFOLIO-WEBSITE/` | Aerospace-themed React+TS+Vite showcase synchronized with real project data, interactive previews, tests | Running |
| **Agent 08** | `qa-security-auditor` | `00-PORTFOLIO-MANAGEMENT/` | Read/Verify across `01`–`08` | Independent code review, test execution, privacy boundary checks, secret scan, quality gate sign-off | Active |
| **NIDAR Team** | `nidar-01..05` | Private Project Orchestration | `08-NIDAR-VEGAPILOT-ARIES-V3/` (gitignored in Hub) | Competition research (`jagjyot2/nidar-vegapilot` private repo), carrier KiCad 10.0.8 PCB, RV32IM firmware, 6-DoF SITL/HIL, GCS | Completed Phase 2 |
| **Browser** | `browser` (`flash`) | `ad3f999b-2751-47b9-bf87-2b9f70e8e547` | `benchtwin.com` & local UI URLs | BenchTwin 3D workbench interaction/login coordination & live dashboard screenshots | Completed |
