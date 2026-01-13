$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$distPath = Join-Path $root "ejecutable"
$workPath = Join-Path $root "temp-pyinstaller"
$exePath = Join-Path $distPath "control-monotributistas.exe"
$venvPython = Join-Path $root ".venv\\Scripts\\python.exe"

# Reset temp folder and ensure output folders exist
if (Test-Path $workPath) {
    Remove-Item -Recurse -Force $workPath
}
New-Item -ItemType Directory -Force -Path $distPath | Out-Null
New-Item -ItemType Directory -Force -Path $workPath | Out-Null

if (Test-Path $exePath) {
    try {
        Remove-Item -Force $exePath -ErrorAction Stop
    } catch {
        throw "No se pudo eliminar el ejecutable existente ($exePath). ¿Está en uso? Ciérralo e intenta de nuevo."
    }
}

$pythonExe = $null
if (Test-Path $venvPython) {
    $pythonExe = $venvPython
} else {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        $pythonCmd = Get-Command py -ErrorAction SilentlyContinue
    }
    if (-not $pythonCmd) {
        throw "Python is not available in PATH and no .venv found."
    }
    $pythonExe = $pythonCmd.Source
}

try {
    & $pythonExe -m PyInstaller --version > $null
} catch {
    throw "PyInstaller is not installed. Install it with `pip install pyinstaller`."
}

$pyinstallerArgs = @(
    "gui.py",
    "--onefile",
    "--windowed",
    "--name", "control-monotributistas",
    "--icon", (Join-Path $root "lib\\ABP.ico"),
    "--distpath", $distPath,
    "--workpath", $workPath,
    "--specpath", $workPath,
    "--noconfirm",
    "--clean"
)

& $pythonExe -m PyInstaller @pyinstallerArgs

$assetSource = Join-Path $root "lib"
$assetTarget = Join-Path $distPath "lib"
New-Item -ItemType Directory -Force -Path $assetTarget | Out-Null
Get-ChildItem -Path $assetSource -Filter "*.png" -ErrorAction SilentlyContinue | Copy-Item -Destination $assetTarget -Force
Get-ChildItem -Path $assetSource -Filter "*.ico" -ErrorAction SilentlyContinue | Copy-Item -Destination $assetTarget -Force

Write-Host "Executable created in $distPath"
Write-Host "Temporary build files stored in $workPath"
