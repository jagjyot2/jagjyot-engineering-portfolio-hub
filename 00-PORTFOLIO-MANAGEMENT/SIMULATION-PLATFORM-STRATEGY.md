# Simulation Platform Strategy: Wokwi Active / BenchTwin Preserved

Last Updated: 2026-11-18T09:35:00+05:30

## 1. Strategic Decision
- **Active Primary Electronics Simulator**: **Wokwi** (`wokwi.com` / `wokwi-cli` + PlatformIO)
- **Temporarily Paused Platform**: **BenchTwin** (`benchtwin.com` v3.75.1 beta)
- **Canonical Engineering Source of Truth**: **KiCad 8** (`hardware/`) + **PlatformIO C++** (`firmware/`)

All hardware projects (`04-FLIGHTCORE`, `05-ROVERSAR`, `06-CELLGUARD`) follow a **simulator-independent architecture** where firmware, pin mappings, KiCad schematics, PCBs, Gerbers, BOMs, and 3D CAD remain completely decoupled from both Wokwi and BenchTwin.

---

## 2. Why BenchTwin Is Temporarily Paused
During live browser verification on `https://benchtwin.com/#app` (v3.75.1 beta), the following operational blockers were observed:
1. **CPU Software WebGL Starvation**: BenchTwin's Three.js (`three.r128`) 3D workbench consumes ~13–15 seconds per page load under headless/automated browser rendering, leaving <5 seconds before the 20-second `OP_TIMEOUT`.
2. **Startup Overlay & Frame Disposal**: The `#bt-load` overlay and periodic Chromium render-frame disposal (`Render frame was disposed`) between automated turns prevented reliable multi-step 3D wiring and `File ▾` export automation.
3. **Engineering Priority**: Spending further time fighting browser WebGL timeouts delays firmware verification, fault-injection testing, and portfolio completion.

---

## 3. Why Wokwi Replaces BenchTwin as Active Simulator
1. **Deterministic Headless & CI Execution**: `wokwi.toml` + `diagram.json` integrate directly with PlatformIO (`pio run` ELF/BIN artifacts) and `wokwi-cli` without requiring a heavy 3D WebGL viewport.
2. **Native ESP32 Instruction-Set Simulation**: Accurately executes compiled ESP32 Xtensa firmware binaries (`firmware.bin` / `firmware.elf`) with real I2C, SPI, UART, GPIO, ADC, PWM, and Serial output capture.
3. **Custom Chip Extensibility**: Wokwi supports custom C/WebAssembly chips (`chip-*.chip.c` / `.json`) and deterministic scenario automation for peripherals not built into the standard library.

---

## 4. Preserved BenchTwin Work (Not Deleted)
All existing BenchTwin exports and staging packages remain intact and tracked in Git:
- `04-FLIGHTCORE/benchtwin/` (`flightcore.btw`, `flightcore-benchtwin.json`, `flightcore.net`, `BOM.csv`, `enclosure_mount.stl`, `schematic_preview.svg`, `BENCHTWIN-SIMULATION-NOTES.md`)
- `05-ROVERSAR/benchtwin/` (`roversar.btw`, `roversar-benchtwin.json`, `roversar.net`, `BOM.csv`, `roversar_base_plate.stl`, `BENCHTWIN-SIMULATION-NOTES.md`)
- `06-CELLGUARD/benchtwin/` (`cellguard.btw`, `cellguard-benchtwin.json`, `cellguard.net`, `BOM.csv`, `cellguard_enclosure.stl`, `BENCHTWIN-SIMULATION-NOTES.md`)

---

## 5. Platform Comparison

| Capability | Wokwi (Active) | BenchTwin (Preserved) | KiCad 8 + PlatformIO (Canonical Truth) |
|---|---|---|---|
| **Primary Role** | Firmware & bus-level ESP32 simulation | 3D physical breadboard & CAD workbench | Schematic, PCB, Gerbers, BOM & production firmware |
| **ESP32 DevKit V1** | Native instruction-set simulation | Simulated (`ESP32 DevKit V1`) | Canonical pinout (`PIN-MAPPING.md` / `config.h`) |
| **MPU6050 (I2C)** | Native `wokwi-mpu6050` | Simulated (`MPU-6050 motion`) | Real I2C hardware driver |
| **VL53L0X (ToF)** | Unsupported natively -> Custom Wokwi chip / mock | Simulated (`VL53L0X`) | Real I2C driver + XSHUT |
| **INA226 / INA219** | Unsupported natively -> Custom Wokwi chip / mock | `INA219` simulated; `INA226` unconfirmed | Real INA226 16-bit I2C driver |
| **LoRa SX1278 (SPI)** | Unsupported natively -> Custom Wokwi SPI stub / mock | `LoRa` library simulated | Real SPI register driver |
| **ESP32-CAM** | Unsupported natively -> UART/HTTP bridge mock | Listed in docs | Real UART/MJPEG module |
| **Headless CI / Automation** | Fast (`wokwi-cli` + `diagram.json`) | Blocked by WebGL `OP_TIMEOUT` | `pio run` + `pio check` + `pytest` |

---

## 6. How to Reactivate BenchTwin in the Future
Because `simulation/adapters/` separates simulator bindings from `firmware/` and `hardware/`:
1. Re-enable `simulation/adapters/benchtwin/` in the target hardware project.
2. Open `https://benchtwin.com/#app` in a hardware-accelerated desktop browser.
3. Import the canonical KiCad netlist (`hardware/*.net`), STL enclosures, and PlatformIO/Arduino driver code using the preserved `benchtwin/` staging files.
4. Wire components per `hardware/PIN-MAPPING.md` (using documented approximations where BenchTwin lacks exact SKUs).
5. Export updated `.btw` / `.net` / screenshots into `benchtwin/` without modifying firmware or PCB designs.
