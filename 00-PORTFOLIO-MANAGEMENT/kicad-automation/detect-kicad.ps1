[CmdletBinding()]
param(
    [switch]$UpdateConfig,
    [switch]$Json
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ConfigPath = Join-Path $ScriptDir "kicad-config.json"

$CandidateRoots = @(
    "C:\Program Files\KiCad\10.0",
    "C:\Program Files\KiCad\9.0",
    "C:\Program Files\KiCad\8.0",
    "$env:LOCALAPPDATA\Programs\KiCad\10.0"
)

if (Test-Path "C:\Program Files\KiCad") {
    $FoundDirs = Get-ChildItem -Path "C:\Program Files\KiCad" -Directory | Sort-Object Name -Descending
    foreach ($d in $FoundDirs) {
        if ($CandidateRoots -notcontains $d.FullName) {
            $CandidateRoots = @($d.FullName) + $CandidateRoots
        }
    }
}

$InstallDir = $null
foreach ($root in $CandidateRoots) {
    if (Test-Path (Join-Path $root "bin\kicad-cli.exe")) {
        $InstallDir = $root
        break
    }
}

if (-not $InstallDir) {
    $cmd = Get-Command kicad-cli.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        $InstallDir = Split-Path -Parent (Split-Path -Parent $cmd.Source)
    }
}

if (-not $InstallDir) {
    Write-Error "KiCad installation with kicad-cli.exe was not found on this machine."
    exit 1
}

$BinDir = Join-Path $InstallDir "bin"
$ShareDir = Join-Path $InstallDir "share\kicad"
$CliPath = Join-Path $BinDir "kicad-cli.exe"
$Version = (& $CliPath --version 2>&1 | Out-String).Trim()
$MajorMinor = if ($Version -match "^(\d+\.\d+)") { $Matches[1] } else { Split-Path -Leaf $InstallDir }
$UserConfigDir = Join-Path $env:APPDATA "kicad\$MajorMinor"

$KiPython = Join-Path $BinDir "python.exe"
$PyAvailable = $false
$PcbnewVer = ""
if (Test-Path $KiPython) {
    try {
        $PcbnewOut = (& $KiPython -c "import pcbnew; print(pcbnew.Version())" 2>&1 | Out-String).Trim()
        if ($LASTEXITCODE -eq 0 -and $PcbnewOut) {
            $PyAvailable = $true
            $PcbnewVer = $PcbnewOut
        }
    } catch {
        $PyAvailable = $false
    }
}

$SymCount = if (Test-Path (Join-Path $ShareDir "symbols")) { (Get-ChildItem (Join-Path $ShareDir "symbols") -Filter "*.kicad_sym").Count } else { 0 }
$FpCount = if (Test-Path (Join-Path $ShareDir "footprints")) { (Get-ChildItem (Join-Path $ShareDir "footprints") -Directory -Filter "*.pretty").Count } else { 0 }
$ModelCount = if (Test-Path (Join-Path $ShareDir "3dmodels")) { (Get-ChildItem (Join-Path $ShareDir "3dmodels") -Directory -Filter "*.3dshapes").Count } else { 0 }

$Detected = [ordered]@{
    kicad = [ordered]@{
        version = $Version
        major_minor = $MajorMinor
        install_dir = $InstallDir
        bin_dir = $BinDir
        executables = [ordered]@{
            kicad_cli = $CliPath
            kicad = (Join-Path $BinDir "kicad.exe")
            eeschema = (Join-Path $BinDir "eeschema.exe")
            pcbnew = (Join-Path $BinDir "pcbnew.exe")
            gerbview = (Join-Path $BinDir "gerbview.exe")
            pcb_calculator = (Join-Path $BinDir "pcb_calculator.exe")
            pl_editor = (Join-Path $BinDir "pl_editor.exe")
            python = $KiPython
        }
        libraries = [ordered]@{
            share_dir = $ShareDir
            symbols_dir = (Join-Path $ShareDir "symbols")
            footprints_dir = (Join-Path $ShareDir "footprints")
            "3dmodels_dir" = (Join-Path $ShareDir "3dmodels")
            template_dir = (Join-Path $ShareDir "template")
            user_config_dir = $UserConfigDir
            symbol_lib_count = $SymCount
            footprint_lib_count = $FpCount
            "3dmodel_dir_count" = $ModelCount
        }
        python_scripting = [ordered]@{
            available = $PyAvailable
            module = "pcbnew"
            pcbnew_version = $PcbnewVer
        }
    }
    design_rules = [ordered]@{
        fab_baseline = "JLCPCB_2Layer_1oz"
        min_clearance_mm = 0.2
        min_track_width_mm = 0.2
        signal_width_mm = 0.25
        sensor_power_width_mm = 0.5
        power_bus_width_mm = 1.0
        high_current_width_mm = 3.0
        min_via_diameter_mm = 0.6
        min_via_drill_mm = 0.3
        std_via_diameter_mm = 0.8
        std_via_drill_mm = 0.4
        board_edge_clearance_mm = 0.5
        silk_text_size_mm = 0.9
        silk_text_thickness_mm = 0.15
        schematic_grid_mm = 1.27
    }
    detected_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssK")
}

if ($UpdateConfig -or -not (Test-Path $ConfigPath)) {
    $JsonText = $Detected | ConvertTo-Json -Depth 6
    [System.IO.File]::WriteAllText($ConfigPath, $JsonText + "`n", (New-Object System.Text.UTF8Encoding($false)))
}

if ($Json) {
    $Detected | ConvertTo-Json -Depth 6
} else {
    Write-Output "=== KiCad Detection Summary ==="
    Write-Output "Version          : $Version"
    Write-Output "Install Dir      : $InstallDir"
    Write-Output "kicad-cli.exe    : $CliPath"
    Write-Output "eeschema.exe     : $($Detected.kicad.executables.eeschema)"
    Write-Output "pcbnew.exe       : $($Detected.kicad.executables.pcbnew)"
    Write-Output "Symbols Dir      : $($Detected.kicad.libraries.symbols_dir) ($SymCount libs)"
    Write-Output "Footprints Dir   : $($Detected.kicad.libraries.footprints_dir) ($FpCount .pretty dirs)"
    Write-Output "3D Models Dir    : $($Detected.kicad.libraries.'3dmodels_dir') ($ModelCount .3dshapes dirs)"
    Write-Output "Python Scripting : $PyAvailable (pcbnew $PcbnewVer)"
    Write-Output "Config Saved     : $ConfigPath"
}
