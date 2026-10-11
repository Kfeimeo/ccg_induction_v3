<#
Build the C++ extension ccg/_ccg_native.*.pyd (native/, nanobind + MSVC, Windows only).

    powershell -ExecutionPolicy Bypass -File scripts/build_native.ps1 [-Python E:\anaconda3\python.exe] [-Vcpkg E:\vcpkg] [-Clean]

Requirements: Visual Studio 2022+ with the C++ toolset (Ninja ships with its CMake component),
CMake >= 3.20 on PATH, vcpkg with `vcpkg install nanobind` (x64-windows).  The Python passed in
(default: the `python` on PATH) must be the interpreter that runs the project.
#>
param(
    [string]$Python = "",
    [string]$Vcpkg = $env:VCPKG_ROOT,
    [string]$Config = "Release",
    [switch]$Clean
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
if (-not $Python) { $Python = (Get-Command python).Source }
if (-not $Vcpkg) {
    foreach ($c in @('E:\vcpkg', 'C:\vcpkg', 'D:\vcpkg', "$env:USERPROFILE\vcpkg")) {
        if (Test-Path "$c\scripts\buildsystems\vcpkg.cmake") { $Vcpkg = $c; break }
    }
}
if (-not (Test-Path "$Vcpkg\scripts\buildsystems\vcpkg.cmake")) { throw "vcpkg not found (set VCPKG_ROOT or -Vcpkg)" }

$vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
$vs = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $vs) { throw "Visual Studio with the C++ toolset not found" }
$vcvars = Join-Path $vs 'VC\Auxiliary\Build\vcvars64.bat'
$ninja = Join-Path $vs 'Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe'
if (-not (Test-Path $ninja)) { $ninja = (Get-Command ninja -ErrorAction SilentlyContinue).Source }
if (-not $ninja) { throw "ninja not found" }

$build = Join-Path $root 'native\build'
if ($Clean -and (Test-Path $build)) { Remove-Item -Recurse -Force $build }
$pyRoot = Split-Path -Parent $Python

Write-Host "Python : $Python"
Write-Host "vcpkg  : $Vcpkg"
Write-Host "VS     : $vs"

# The vcpkg *toolchain* is deliberately not used: its FindPython wrapper forces vcpkg's own Python
# headers, which do not match the project interpreter.  The install prefix on CMAKE_PREFIX_PATH is
# enough for find_package(nanobind) and its robin-map dependency.
$prefix = "$Vcpkg\installed\x64-windows" -replace '\\', '/'
$configure = "cmake -S `"$root\native`" -B `"$build`" -G Ninja -DCMAKE_MAKE_PROGRAM=`"$ninja`" -DCMAKE_BUILD_TYPE=$Config " +
             "-DCMAKE_PREFIX_PATH=`"$prefix`" " +
             "-DPython_EXECUTABLE=`"$Python`" -DPython_ROOT_DIR=`"$pyRoot`" -DPython_FIND_STRATEGY=LOCATION"
$buildCmd = "cmake --build `"$build`" --config $Config"
cmd /c "call `"$vcvars`" >nul 2>nul && $configure && $buildCmd"
if ($LASTEXITCODE -ne 0) { throw "native build failed (exit $LASTEXITCODE)" }

Push-Location $root
try {
    & $Python -c "import ccg.native as n; print('ccg.native available:', n.available, '| module:', n.module_file())"
} finally { Pop-Location }
