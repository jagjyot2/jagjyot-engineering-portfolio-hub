# Autonomous GitHub Secret Scan & Multi-Repo Publisher
# Verifies gh authentication, scans for accidental secrets/artifacts, creates public repos, and pushes main branches.

$ErrorActionPreference = "Stop"
$PortfolioRoot = Split-Path -Parent $PSScriptRoot

Write-Host "=== 1. Checking GitHub CLI Authentication ===" -ForegroundColor Cyan
gh auth status
if ($LASTEXITCODE -ne 0) {
    Write-Error "GitHub CLI is not authenticated. Run 'gh auth login --web' first, then re-run this script."
    exit 1
}

$Repos = @(
    @{ Dir = "01-AEROLENS"; Name = "aerolens-flight-analytics"; Desc = "AeroLens: Modular Drone Flight Log Analytics, Anomaly Detection & Reporting Platform" },
    @{ Dir = "02-SARVISION"; Name = "sarvision-ai"; Desc = "SARVision: AI-Powered Aerial Search & Rescue Tiled Vision, Geolocation & Verification System" },
    @{ Dir = "03-SWARMFORGE"; Name = "swarmforge-uav-simulator"; Desc = "SwarmForge: Multi-Drone Autonomous Mission Planning (A*, RRT*, APF) & 3D WebGL Digital Twin" },
    @{ Dir = "04-FLIGHTCORE"; Name = "flightcore-telemetry"; Desc = "FlightCore: Modular ESP32-Based Drone Sensor & LoRa Telemetry System (KiCad + PlatformIO)" },
    @{ Dir = "05-ROVERSAR"; Name = "roversar-autonomous-robot"; Desc = "RoverSAR: Autonomous Search & Rescue Differential-Drive Ground Robot & Nav Simulator" },
    @{ Dir = "06-CELLGUARD"; Name = "cellguard-battery-monitor"; Desc = "CellGuard: Intelligent 21700 Li-Ion Battery Monitoring & Health Analytics (INA226 + ESP32)" },
    @{ Dir = "07-PORTFOLIO-WEBSITE"; Name = "jagjyot-engineering-portfolio"; Desc = "Interactive Aerospace & Robotics Engineering Portfolio Website" }
)

$SecretPatterns = @(
    "ghp_[A-Za-z0-9]{20,}",
    "github_pat_[A-Za-z0-9_]{20,}",
    "sk-[A-Za-z0-9]{20,}",
    "AIza[0-9A-Za-z\-_]{35}",
    "-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"
)

Write-Host "=== 2. Running Pre-Release Secret Scan ===" -ForegroundColor Cyan
foreach ($r in $Repos) {
    $path = Join-Path $PortfolioRoot $r.Dir
    if (-not (Test-Path $path)) { Write-Error "Missing project directory: $path"; exit 1 }
    $files = Get-ChildItem -Path $path -Recurse -File | Where-Object {
        $_.FullName -notmatch "\\(\.git|node_modules|__pycache__|\.venv|dist|build)\\"
    }
    foreach ($f in $files) {
        if ($f.Length -gt 2MB) { continue }
        $content = Get-Content -Path $f.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }
        foreach ($pat in $SecretPatterns) {
            if ($content -match $pat) {
                Write-Error "SECURITY BLOCK: Potential secret pattern ($pat) found in $($f.FullName)"
                exit 1
            }
        }
    }
    Write-Host "  [OK] Secret scan clean: $($r.Dir)" -ForegroundColor Green
}

Write-Host "=== 3. Creating & Pushing Public Repositories ===" -ForegroundColor Cyan
$Owner = (gh api user --jq ".login").Trim()
foreach ($r in $Repos) {
    $path = Join-Path $PortfolioRoot $r.Dir
    Push-Location $path
    try {
        if (-not (Test-Path ".git")) {
            Write-Error "Git not initialized in $path"
            exit 1
        }
        $existingOrigin = git remote get-url origin 2>$null
        if (-not $existingOrigin) {
            gh repo create "$Owner/$($r.Name)" --public --description "$($r.Desc)" --source=. --remote=origin --push
        } else {
            git push -u origin main
        }
        Write-Host "  [PUBLISHED] https://github.com/$Owner/$($r.Name)" -ForegroundColor Green
    } finally {
        Pop-Location
    }
}

Write-Host "=== 4. All repositories processed cleanly ===" -ForegroundColor Cyan
