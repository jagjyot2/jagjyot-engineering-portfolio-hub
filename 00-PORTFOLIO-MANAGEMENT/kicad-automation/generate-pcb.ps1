[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectDir,
    [Parameter(Mandatory = $true)]
    [string]$ProjectName,
    [string]$GeneratorScript = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AbsDir = [System.IO.Path]::GetFullPath($ProjectDir)

if ($GeneratorScript -and (Test-Path $GeneratorScript)) {
    & python $GeneratorScript
    exit $LASTEXITCODE
}

$LocalGen = Join-Path $AbsDir "generate_${ProjectName}.py"
if (Test-Path $LocalGen) {
    & python $LocalGen
    exit $LASTEXITCODE
}

$PcbPath = Join-Path $AbsDir "$ProjectName.kicad_pcb"
$SchPath = Join-Path $AbsDir "$ProjectName.kicad_sch"
$Cli = (Get-Content (Join-Path $ScriptDir "kicad-config.json") | ConvertFrom-Json).kicad.executables.kicad_cli

if (-not (Test-Path $SchPath)) {
    Write-Error "Schematic not found: $SchPath"
    exit 1
}

& $Cli sch export netlist --format kicadsexpr --output (Join-Path $AbsDir "$ProjectName.net") $SchPath
if (Test-Path $PcbPath) {
    & $Cli pcb drc --refill-zones --save-board --schematic-parity --output (Join-Path $AbsDir "gerbers\${ProjectName}_drc.txt") $PcbPath
    Write-Output "Verified & updated zones on existing PCB: $PcbPath"
} else {
    Write-Error "PCB file missing and no generator script provided: $PcbPath"
    exit 1
}
