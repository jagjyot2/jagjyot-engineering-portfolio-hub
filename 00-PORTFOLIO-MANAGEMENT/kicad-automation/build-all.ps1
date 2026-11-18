[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectDir,
    [Parameter(Mandatory = $true)]
    [string]$ProjectName,
    [string]$GerberDir = "",
    [string]$ModelsDir = "",
    [string]$BomPath = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AbsDir = [System.IO.Path]::GetFullPath($ProjectDir)
$GDir = if ($GerberDir) { [System.IO.Path]::GetFullPath($GerberDir) } else { Join-Path $AbsDir "gerbers" }
$MDir = if ($ModelsDir) { [System.IO.Path]::GetFullPath($ModelsDir) } else { Join-Path $AbsDir "3d-models" }
$BPath = if ($BomPath) { [System.IO.Path]::GetFullPath($BomPath) } else { Join-Path $AbsDir "BOM-kicad.csv" }

$PyCode = @"
import json, sys
from pathlib import Path
sys.path.insert(0, r"$ScriptDir")
import kicad_toolkit as kt

res = kt.build_and_verify_project(
    project_dir=Path(r"$AbsDir"),
    project_name="$ProjectName",
    gerber_dir=Path(r"$GDir"),
    bom_out_path=Path(r"$BPath"),
    models_out_dir=Path(r"$MDir"),
)
print(json.dumps(res, indent=2))
if res["erc_violations"] > 0 or res["drc_violations"] > 0 or res["drc_unconnected"] > 0 or res["drc_parity_issues"] > 0:
    sys.exit(2)
"@

$PyExe = (Get-Content (Join-Path $ScriptDir "kicad-config.json") | ConvertFrom-Json).kicad.executables.python
$SysPy = Get-Command python.exe -ErrorAction SilentlyContinue
$Runner = if ($SysPy) { $SysPy.Source } else { $PyExe }
$PyCode | & $Runner -
exit $LASTEXITCODE
