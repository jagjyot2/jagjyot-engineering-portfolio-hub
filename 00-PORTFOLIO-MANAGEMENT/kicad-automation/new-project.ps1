[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectName,
    [Parameter(Mandatory = $true)]
    [string]$OutputDir,
    [string]$Title = "",
    [string]$LibName = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ToolkitPy = Join-Path $ScriptDir "kicad_toolkit.py"
$SafeLib = if ($LibName) { $LibName } else { ($ProjectName -replace '[^A-Za-z0-9_]', '_') }
$ProjTitle = if ($Title) { $Title } else { "$ProjectName Hardware Project" }

$TargetDir = [System.IO.Path]::GetFullPath($OutputDir)
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $TargetDir "symbols") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $TargetDir "footprints\$SafeLib.pretty") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $TargetDir "gerbers") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $TargetDir "3d-models") | Out-Null

$PyCode = @"
import sys
from pathlib import Path
sys.path.insert(0, r"$ScriptDir")
import kicad_toolkit as kt

proj_dir = Path(r"$TargetDir")
kt.write_utf8(proj_dir / "$ProjectName.kicad_pro", kt.build_kicad_pro("$ProjectName"))
kt.write_project_lib_tables(proj_dir, "$SafeLib")

sb = kt.SchematicBuilder("$ProjectName", "$SafeLib", "$ProjTitle")
sb.add_component(kt.SchComponent("J1", "PWR_IN", "${SafeLib}:Conn_1x02_P2.54mm", [
    kt.SchPin("1", "VCC", "VCC", "left", "power_out"),
    kt.SchPin("2", "GND", "GND", "right", "power_out"),
]))
sb.add_component(kt.SchComponent("R1", "1k", "${SafeLib}:R_0805", [
    kt.SchPin("1", "1", "VCC", "left", "passive"),
    kt.SchPin("2", "2", "LED_A", "right", "passive"),
]))
sb.add_component(kt.SchComponent("D1", "LED_GREEN", "${SafeLib}:LED_0805", [
    kt.SchPin("1", "A", "LED_A", "left", "passive"),
    kt.SchPin("2", "K", "GND", "right", "passive"),
]))
sb.write(proj_dir)

pb = kt.PCBBuilder("$ProjectName", "$SafeLib", 40.0, 25.0, "$ProjectName v1.0", sb.root_uuid)
fp_j = kt.fp_pin_header_1xN("Conn_1x02_P2.54mm", 2)
fp_r = kt.fp_smd_2pin("R_0805", 1.825, 1.025, 1.4, "Resistor_SMD.3dshapes/R_0805_2012Metric.step")
fp_d = kt.fp_smd_2pin("LED_0805", 1.825, 1.025, 1.4, "LED_SMD.3dshapes/LED_0805_2012Metric.step")
pb.add_component(kt.PcbComponent("J1", "PWR_IN", fp_j, 8.0, 12.5, 0.0, {"1": "VCC", "2": "GND"}))
pb.add_component(kt.PcbComponent("R1", "1k", fp_r, 18.0, 11.23, 0.0, {"1": "VCC", "2": "LED_A"}))
pb.add_component(kt.PcbComponent("D1", "LED_GREEN", fp_d, 28.0, 11.23, 0.0, {"1": "LED_A", "2": "GND"}))
pb.add_track("VCC", 0.5, [pb.pad_abs_xy("J1", "1"), pb.pad_abs_xy("R1", "1")], "F.Cu")
pb.add_track("LED_A", 0.25, [pb.pad_abs_xy("R1", "2"), pb.pad_abs_xy("D1", "1")], "F.Cu")
gnd_d1 = pb.pad_abs_xy("D1", "2")
pb.add_track("GND", 0.5, [gnd_d1, (gnd_d1[0], 17.0)], "F.Cu")
pb.add_via("GND", gnd_d1[0], 17.0, 0.7, 0.35)
pb.write(proj_dir)
print("CREATED_PROJECT:", proj_dir / "$ProjectName.kicad_pro")
"@

$PyExe = (Get-Content (Join-Path $ScriptDir "kicad-config.json") | ConvertFrom-Json).kicad.executables.python
# Use standard Python 3.12 if available, else KiCad python
$SysPy = Get-Command python.exe -ErrorAction SilentlyContinue
$Runner = if ($SysPy) { $SysPy.Source } else { $PyExe }
$PyCode | & $Runner -
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
