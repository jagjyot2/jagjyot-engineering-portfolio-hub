[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PcbPath,
    [string]$OutputDir = "",
    [switch]$SkipParity
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Cfg = Get-Content (Join-Path $ScriptDir "kicad-config.json") | ConvertFrom-Json
$Cli = $Cfg.kicad.executables.kicad_cli

$Pcb = [System.IO.Path]::GetFullPath($PcbPath)
$Base = [System.IO.Path]::GetFileNameWithoutExtension($Pcb)
$Dir = if ($OutputDir) { [System.IO.Path]::GetFullPath($OutputDir) } else { Join-Path (Split-Path -Parent $Pcb) "gerbers" }
New-Item -ItemType Directory -Force -Path $Dir | Out-Null

$RptOut = Join-Path $Dir "${Base}_drc.txt"
$JsonOut = Join-Path $Dir "${Base}_drc.json"

$ArgsBase = @("pcb", "drc", "--refill-zones", "--save-board", "--severity-all")
if (-not $SkipParity) { $ArgsBase += "--schematic-parity" }

& $Cli @ArgsBase --format json --output $JsonOut $Pcb | Out-Null
& $Cli @ArgsBase --format report --exit-code-violations --output $RptOut $Pcb
$rc = $LASTEXITCODE
Get-Content $RptOut
exit $rc
