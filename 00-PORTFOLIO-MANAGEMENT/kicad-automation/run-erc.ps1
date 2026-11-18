[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SchematicPath,
    [string]$OutputDir = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Cfg = Get-Content (Join-Path $ScriptDir "kicad-config.json") | ConvertFrom-Json
$Cli = $Cfg.kicad.executables.kicad_cli

$Sch = [System.IO.Path]::GetFullPath($SchematicPath)
$Base = [System.IO.Path]::GetFileNameWithoutExtension($Sch)
$Dir = if ($OutputDir) { [System.IO.Path]::GetFullPath($OutputDir) } else { Join-Path (Split-Path -Parent $Sch) "gerbers" }
New-Item -ItemType Directory -Force -Path $Dir | Out-Null

$RptOut = Join-Path $Dir "${Base}_erc.txt"
$JsonOut = Join-Path $Dir "${Base}_erc.json"

& $Cli sch erc --severity-all --format json --output $JsonOut $Sch | Out-Null
& $Cli sch erc --severity-all --format report --exit-code-violations --output $RptOut $Sch
$rc = $LASTEXITCODE
Get-Content $RptOut
exit $rc
