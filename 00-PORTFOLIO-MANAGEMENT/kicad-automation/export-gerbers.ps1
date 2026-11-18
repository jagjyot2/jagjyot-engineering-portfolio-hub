[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PcbPath,
    [string]$OutputDir = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Cfg = Get-Content (Join-Path $ScriptDir "kicad-config.json") | ConvertFrom-Json
$Cli = $Cfg.kicad.executables.kicad_cli

$Pcb = [System.IO.Path]::GetFullPath($PcbPath)
$Dir = if ($OutputDir) { [System.IO.Path]::GetFullPath($OutputDir) } else { Join-Path (Split-Path -Parent $Pcb) "gerbers" }
New-Item -ItemType Directory -Force -Path $Dir | Out-Null

& $Cli pcb export gerbers --check-zones --subtract-soldermask -l "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts" --output "$Dir/" $Pcb
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $Cli pcb export drill --excellon-units mm --excellon-separate-th --generate-map --output "$Dir/" $Pcb
exit $LASTEXITCODE
