# Portfolio Management Hub

Central operational control center for the autonomous multi-agent engineering organization (Agents 00–08 + Browser Subagent).

## Quick Links
- [Live Project Status](./PROJECT-STATUS.md)
- [Master Roadmap](./MASTER-ROADMAP.md)
- [Agent Registry](./AGENT-REGISTRY.md)
- [Development Log](./DEVELOPMENT-LOG.md)
- [Resume State Checkpoint](./RESUME-STATE.md)
- [GitHub Repositories Tracker](./github-repositories.md)
- [Bulk GitHub Publisher Script](./publish-all-github.ps1)

## Engineering & Safety Standards
1. **No Fake Implementations**: Real flight log parsers, real OpenCV/ONNX/PyTorch inference pipelines, real 3D kinematics & A*/RRT*/APF planners, real KiCad schematics/PCBs/BOMs/STLs, and real ESP32 PlatformIO C++ firmware.
2. **Hardware Safety Boundaries**:
   - `04-FLIGHTCORE` is strictly a telemetry & sensor expansion module (no motor actuation).
   - `06-CELLGUARD` is strictly a monitoring & health analytics instrument used alongside an external commercial BMS + inline fuse (no charging, no balancing, no FET switching).
   - `03-SWARMFORGE` enforces `HARDWARE_ACTUATION_LOCKED = True` by default.
3. **Continuous Verification**: Every project has automated unit/integration tests and undergoes an independent QA & secret scan by Agent 08 before publication.
