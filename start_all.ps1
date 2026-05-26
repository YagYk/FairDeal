<#
.SYNOPSIS
    FAIRDEAL one-shot launcher (Windows / PowerShell).

.DESCRIPTION
    Starts the backend (FastAPI + uvicorn on port 8000) and the frontend
    (Vite on port 5173) in two separate PowerShell windows so you can see
    the logs of each. After both come up the script opens
    http://localhost:5173/ in your default browser.

    Safe to re-run. If a previous instance is already listening on either
    port, the script offers to free it before starting fresh.

.PARAMETER NoBrowser
    Do not auto-open the browser. The servers still launch.

.PARAMETER InstallDeps
    Force a `pip install -r backend/requirements*.txt` and `npm install`
    before starting. Use this on the first run, after pulling new deps,
    or when something feels off.

.PARAMETER BackendPort
    Port for the FastAPI server. Default: 8000.

.PARAMETER FrontendPort
    Port for the Vite dev server. Default: 5173.

.EXAMPLE
    .\start_all.ps1

.EXAMPLE
    .\start_all.ps1 -InstallDeps -NoBrowser
#>

[CmdletBinding()]
param(
    [switch]$NoBrowser,
    [switch]$InstallDeps,
    [int]$BackendPort  = 8000,
    [int]$FrontendPort = 5173
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

# ─── Helpers ────────────────────────────────────────────────────────────────

function Write-Section($text) {
    Write-Host ""
    Write-Host ("=" * 72) -ForegroundColor Cyan
    Write-Host $text -ForegroundColor Cyan
    Write-Host ("=" * 72) -ForegroundColor Cyan
}

function Write-Ok($msg)   { Write-Host "  [ok]   $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  [warn] $msg" -ForegroundColor Yellow }
function Write-Fail($msg) { Write-Host "  [fail] $msg" -ForegroundColor Red }

function Test-Port {
    param([int]$Port)
    try {
        $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        return [bool]$listener
    } catch {
        # Get-NetTCPConnection is Windows-only; fall back to a socket probe.
        try {
            $client = New-Object System.Net.Sockets.TcpClient
            $client.Connect("127.0.0.1", $Port)
            $client.Close()
            return $true
        } catch {
            return $false
        }
    }
}

function Stop-PortListener {
    param([int]$Port)
    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $conns) { return }
    $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($targetPid in $pids) {
        try {
            $proc = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Warn "killing existing listener on port $Port (pid=$targetPid, name=$($proc.ProcessName))"
                Stop-Process -Id $targetPid -Force -ErrorAction SilentlyContinue
            }
        } catch {
            Write-Warn "could not kill pid $targetPid - try it manually"
        }
    }
    Start-Sleep -Milliseconds 600
}

function Wait-ForPort {
    param([int]$Port, [int]$TimeoutSeconds = 60)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Port -Port $Port) { return $true }
        Start-Sleep -Milliseconds 500
    }
    return $false
}

function Resolve-PythonExe {
    # Prefer a project venv if one exists, otherwise fall back to PATH.
    $candidates = @(
        (Join-Path $PSScriptRoot ".venv\Scripts\python.exe"),
        (Join-Path $PSScriptRoot "venv\Scripts\python.exe"),
        (Join-Path $PSScriptRoot "backend\.venv\Scripts\python.exe")
    )
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) { return $candidate }
    }
    return "python"
}

function Test-PythonImport {
    <#
    Returns $true if `python -c "import <module>"` succeeds under the given
    interpreter, $false otherwise. Captures stderr so we can surface the
    real failure reason.
    #>
    param(
        [Parameter(Mandatory)] [string]$PythonExe,
        [Parameter(Mandatory)] [string]$Module
    )
    try {
        $output = & $PythonExe -c "import $Module" 2>&1
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

function Get-PythonVersion {
    param([Parameter(Mandatory)] [string]$PythonExe)
    try {
        return (& $PythonExe -c "import sys; print(sys.version.split()[0])") 2>$null
    } catch {
        return "?"
    }
}

# ─── Pre-flight checks ──────────────────────────────────────────────────────

Write-Section "FAIRDEAL launcher"
Write-Host "  repo          : $PSScriptRoot"
Write-Host "  backend port  : $BackendPort"
Write-Host "  frontend port : $FrontendPort"

$backendDir  = Join-Path $PSScriptRoot "backend"
$frontendDir = Join-Path $PSScriptRoot "frontend"

if (-not (Test-Path -LiteralPath $backendDir))  { Write-Fail "backend folder missing at $backendDir";  exit 1 }
if (-not (Test-Path -LiteralPath $frontendDir)) { Write-Fail "frontend folder missing at $frontendDir"; exit 1 }

$pythonExe = Resolve-PythonExe
$pythonVer = Get-PythonVersion -PythonExe $pythonExe
Write-Ok "python: $pythonExe ($pythonVer)"

# Verify the dependencies the backend actually needs at import time. If
# uvicorn launches under a Python that's missing one of these, you'll see
# silent 500s on /api/kb/* — so we catch it here and refuse to launch.
$mustHave = @("fastapi", "uvicorn", "pydantic", "chromadb", "sentence_transformers")
$missing  = @()
foreach ($mod in $mustHave) {
    if (-not (Test-PythonImport -PythonExe $pythonExe -Module $mod)) {
        $missing += $mod
    }
}
if ($missing.Count -gt 0) {
    Write-Fail "the chosen Python is missing these modules: $($missing -join ', ')"
    Write-Fail "fix it with one of these (whichever applies to your setup):"
    Write-Fail "    & `"$pythonExe`" -m pip install -r backend\requirements.txt"
    Write-Fail "or  .\start_all.ps1 -InstallDeps"
    Write-Fail ""
    Write-Fail "If 'prepare_demo.py' succeeded earlier, you most likely have multiple"
    Write-Fail "Python installations and uvicorn is being launched under the wrong one."
    Write-Fail "Find the right interpreter with:  py -0p"
    Write-Fail "Then re-run: .\start_all.ps1 (after dropping a .venv with the right Python)"
    exit 1
}
Write-Ok "all required Python modules import cleanly"

# Sanity-check Node + npm by asking them their version. If either is
# missing we stop early instead of opening a window that immediately dies.
try {
    $nodeVersion = (& node --version) 2>$null
    $npmVersion  = (& npm  --version) 2>$null
    if (-not $nodeVersion -or -not $npmVersion) { throw "node/npm not on PATH" }
    Write-Ok "node: $nodeVersion / npm: $npmVersion"
} catch {
    Write-Fail "Node.js + npm are required for the frontend, but were not found on PATH."
    Write-Fail "Install Node 18+ from https://nodejs.org/ and re-run this script."
    exit 1
}

# ─── Optional dependency install ────────────────────────────────────────────

if ($InstallDeps) {
    Write-Section "Installing dependencies (-InstallDeps was passed)"
    Push-Location $PSScriptRoot
    try {
        # The repo has three requirements files; install whichever exist.
        # backend/requirements.txt is the most complete and is the only one
        # that is guaranteed to be present.
        $candidates = @(
            (Join-Path $PSScriptRoot "backend\requirements.txt"),
            (Join-Path $PSScriptRoot "requirements.txt"),
            (Join-Path $PSScriptRoot "requirements-rag.txt")
        )
        foreach ($req in $candidates) {
            if (Test-Path -LiteralPath $req) {
                Write-Host "  installing $req"
                & $pythonExe -m pip install -r $req
            }
        }
    } finally {
        Pop-Location
    }

    Push-Location $frontendDir
    try {
        npm install
    } finally {
        Pop-Location
    }
} else {
    # Auto-detect the very first run and install front-end deps if needed.
    if (-not (Test-Path -LiteralPath (Join-Path $frontendDir "node_modules"))) {
        Write-Section "First-run setup: installing frontend dependencies"
        Push-Location $frontendDir
        try { npm install } finally { Pop-Location }
    }
}

# ─── Free up stuck ports ────────────────────────────────────────────────────

Write-Section "Port check"

if (Test-Port -Port $BackendPort) {
    Write-Warn "port $BackendPort is already in use"
    Stop-PortListener -Port $BackendPort
} else {
    Write-Ok "port $BackendPort is free"
}

if (Test-Port -Port $FrontendPort) {
    Write-Warn "port $FrontendPort is already in use"
    Stop-PortListener -Port $FrontendPort
} else {
    Write-Ok "port $FrontendPort is free"
}

# ─── Launch ─────────────────────────────────────────────────────────────────

Write-Section "Launching servers"

$backendTitle  = "FAIRDEAL backend  (uvicorn :$BackendPort)"
$frontendTitle = "FAIRDEAL frontend (vite :$FrontendPort)"

# We pass commands through `cmd /c start` so each server gets its own
# coloured terminal window with a meaningful title bar.
$backendCmd =
    "cd /d `"$backendDir`" && " +
    "title $backendTitle && " +
    "`"$pythonExe`" -m uvicorn app.main:app --reload --host 127.0.0.1 --port $BackendPort"

$frontendCmd =
    "cd /d `"$frontendDir`" && " +
    "title $frontendTitle && " +
    "npm run dev -- --port $FrontendPort"

Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $backendCmd  | Out-Null
Write-Ok "backend window spawned"

Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $frontendCmd | Out-Null
Write-Ok "frontend window spawned"

# ─── Wait for both to become reachable ──────────────────────────────────────

Write-Section "Waiting for servers to come up"

$backendUp = Wait-ForPort -Port $BackendPort -TimeoutSeconds 60
if ($backendUp) {
    Write-Ok "backend listening at http://127.0.0.1:$BackendPort"
    Write-Ok "  swagger : http://127.0.0.1:$BackendPort/docs"
} else {
    Write-Fail "backend did not start within 60 s; check the backend window for errors"
}

$frontendUp = Wait-ForPort -Port $FrontendPort -TimeoutSeconds 90
if ($frontendUp) {
    Write-Ok "frontend listening at http://localhost:$FrontendPort"
} else {
    Write-Fail "frontend did not start within 90 s; check the frontend window for errors"
}

# ─── Open the browser ───────────────────────────────────────────────────────

if ($frontendUp -and -not $NoBrowser) {
    Start-Sleep -Seconds 1
    Start-Process "http://localhost:$FrontendPort/"
    Write-Ok "opened http://localhost:$FrontendPort/ in your default browser"
}

Write-Section "All set"
Write-Host "  Two new windows are running uvicorn and vite."
Write-Host "  Stop a server by closing its window or pressing Ctrl+C inside it."
Write-Host ""
