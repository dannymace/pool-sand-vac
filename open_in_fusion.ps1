$fusionExe = "C:\Users\dmace\AppData\Local\Autodesk\webdeploy\production\dc17ef0089c4e594bf5a4bf81f553cd441924ebc\Fusion360.exe"
$stepPath = "\\wsl.localhost\Ubuntu\home\dmace\pool-sand-vac-step-package\out\sand_vac_head_clean_master.step"
$stlPath = "C:\Users\dmace\projects\pool-sand-vac\renders\sand_vac_head_5p8_recommended.stl"

if (-not (Test-Path $fusionExe)) {
    throw "Fusion executable not found at $fusionExe"
}

$target = if (Test-Path $stepPath) { $stepPath } else { $stlPath }

if (-not (Test-Path $target)) {
    throw "Target file not found: $target"
}

Start-Process -FilePath $fusionExe -ArgumentList "`"$target`""
Write-Host "Opened Fusion 360 with: $target"
