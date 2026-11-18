# Master Engineering Roadmap

## Phase 1: Infrastructure, Governance & Checkpointing (Active)
- [x] Inspect environment tools (Python 3.12.10, Node v26.7.0, Git 2.55.0, PlatformIO 6.2.0, FastAPI, OpenCV, PyTorch, ONNX Runtime, SQLAlchemy, SciPy, NumPy).
- [x] Initialize `ENGINEERING-PORTFOLIO/` directory layout (`00` through `07`).
- [x] Create governance, roadmap, registry, resume-state, and GitHub publishing automation scripts.
- [ ] Configure 15-minute `schedule` checkpointing and 5-hour resumption automation sidecar.

## Phase 2: Parallel Vertical-Slice Engineering (Agents 01–07 + Browser)
- [ ] **01-AEROLENS**: Modular ArduPilot/PX4 ULog/MAVLink parsers, spectral/electrical/GPS anomaly engine, SQLite persistence, FastAPI REST, PDF/HTML/CSV export, React+TS+Plotly aerospace UI, synthetic test logs, pytest suite.
- [ ] **02-SARVISION**: High-res aerial tiler + global NMS, ONNX/PyTorch + OpenCV spectral SAR detector, EXIF pinhole GPS raycaster, Precision/Recall/IoU evaluator, human verification queue, React+TS inspector UI, synthetic aerial evaluation set, pytest suite.
- [ ] **03-SWARMFORGE**: 3D multi-UAV kinematic/wind/battery engine, 3D A*, RRT*, and APF planners + benchmark comparator, multi-agent collision avoidance & geofencing, comm-loss failsafe, FastAPI WebSockets, React+Three.js 3D digital twin UI, pytest suite.
- [ ] **04-FLIGHTCORE**: PlatformIO ESP32 modular firmware (MPU6050, VL53L0X, SX1278 LoRa CRC-16 protocol, Hall RPM, ADC voltage/current/NTC), KiCad 8 schematic/PCB/Gerbers/BOM, BenchTwin export package, C++/Python verification tests.
- [ ] **05-ROVERSAR**: PlatformIO ESP32 differential-drive firmware (PID wheel encoders, VL53L0X, MPU6050 odometry, 500ms comm-loss failsafe, E-STOP), Python navigation simulator + mobile/desktop web dashboard, OpenSCAD/STL 3D printable chassis, KiCad schematic/BOM, BenchTwin export package, pytest suite.
- [ ] **06-CELLGUARD**: PlatformIO ESP32 21700 4S/6S pack monitor firmware (INA226 shunt/bus, NTC dT/dt thermal runaway monitor, Coulomb+OCV SoC/SoH/R_dc estimator, NVS calibration), KiCad 8 Kelvin-shunt PCB/Gerbers/BOM/Safety Guide, FastAPI analytics dashboard, BenchTwin export package, pytest suite.
- [ ] **07-PORTFOLIO-WEBSITE**: Dark-mode aerospace/robotics React+TS+Vite showcase synchronized with live project metrics, interactive telemetry previews, architecture diagrams, hardware BOM/STL views, and repository verification tests.
- [ ] **Browser Automation (`benchtwin.com` & Visual QA)**: Inspect BenchTwin component library, request user Google auth if gated, build/capture physical circuits, capture real UI screenshots of local running web dashboards.

## Phase 3: Independent QA, Security Scan & GitHub Release (Agent 08)
- [ ] Execute every project test suite and log exact pass/fail counts.
- [ ] Start every FastAPI/web backend and verify health & functional endpoints.
- [ ] Run secret scanning across all 7 Git repositories and verify clean `.gitignore` + `.env.example`.
- [x] Authenticate `gh` CLI (with user OAuth completion if needed) and push all 7 repositories to GitHub `main`.
- [x] Deliver 10-part Final Engineering Report.

## Phase 4: KiCad 10.0.8 Automation, Hardware PCB Audits & NIDAR VEGAPilot [PRIVATE]
- [x] Auto-detect KiCad `10.0.8` (`C:\Program Files\KiCad\10.0`) and create reusable toolkit `00-PORTFOLIO-MANAGEMENT/kicad-automation/` (`kicad-config.json`, `kicad_toolkit.py`, 8 PowerShell automation scripts).
- [x] Audit and regenerate `04-FLIGHTCORE` (`1ee6709`, 20/20 passed), `05-ROVERSAR` (`8507294`, 20/20 passed), and `06-CELLGUARD` (`a030ef1`, 23/23 passed) in KiCad `10.0.8` with `0` ERC / `0` DRC / `0` unconnected / `0` parity issues, updated Gerbers/DRL/BOM/STEP/GLB.
- [x] Launch Priority-1 confidential project `08-NIDAR-VEGAPILOT-ARIES-V3/` in strictly private repository `jagjyot2/nidar-vegapilot` (`032d036`, `private: true`, ignored in public hub `.gitignore`).
