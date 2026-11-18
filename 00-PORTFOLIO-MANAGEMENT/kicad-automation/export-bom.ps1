[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SchematicPath,
    [string]$OutputCsv = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Cfg = Get-Content (Join-Path $ScriptDir "kicad-config.json") | ConvertFrom-Json
$Cli = $Cfg.kicad.executables.kicad_cli

$Sch = [System.IO.Path]::GetFullPath($SchematicPath)
$Out = if ($OutputCsv) { [System.IO.Path]::GetFullPath($OutputCsv) } else { Join-Path (Split-Path -Parent $Sch) "BOM-kicad.csv" }

& $Cli sch export bom `
    --fields "Reference,Value,Footprint,MPN,Manufacturer,Rating,Origin,QUANTITY" `
    --labels "Designator,Value,Footprint,MPN,Manufacturer,Rating,Origin,Qty" `
    --output $Out $Sch
exit $LASTEXITCODE
