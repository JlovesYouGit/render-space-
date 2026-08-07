# Deep GPU and Display Pipeline Analysis
# Investigates quantum-like rendering effects and display convergence

Write-Host "DEEP GPU RENDERING AND DISPLAY PIPELINE ANALYSIS" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

# GPU Information
Write-Host "Collecting GPU Information..." -ForegroundColor Yellow
$gpu = Get-WmiObject -Namespace "root\cimv2" -Class Win32_VideoController | Select-Object Name, DriverVersion, AdapterRAM, CurrentRefreshRate, CurrentBitsPerPixel, CurrentHorizontalResolution, CurrentVerticalResolution

Write-Host "GPU Details:" -ForegroundColor Green
Write-Host "  Name: $($gpu.Name)" -ForegroundColor White
Write-Host "  Driver Version: $($gpu.DriverVersion)" -ForegroundColor White
Write-Host "  VRAM: $([math]::Round($gpu.AdapterRAM / 1GB, 2)) GB" -ForegroundColor White
Write-Host "  Current Refresh Rate: $($gpu.CurrentRefreshRate) Hz" -ForegroundColor White
Write-Host "  Current Resolution: $($gpu.CurrentHorizontalResolution) x $($gpu.CurrentVerticalResolution)" -ForegroundColor White
Write-Host "  Color Depth: $($gpu.CurrentBitsPerPixel) bits" -ForegroundColor White
Write-Host ""

# DirectX Information
Write-Host "Collecting DirectX and Rendering Information..." -ForegroundColor Yellow
try {
    $directX = Get-WmiObject -Namespace "root\cimv2" -Class Win32_DirectX -ErrorAction SilentlyContinue
    if ($directX) {
        Write-Host "DirectX Version: $($directX.DirectXVersion)" -ForegroundColor Green
    }
} catch {
    Write-Host "DirectX information not available via WMI" -ForegroundColor Gray
}
Write-Host ""

# Display Controller Information
Write-Host "Collecting Display Controller Details..." -ForegroundColor Yellow
$displayControllers = Get-WmiObject -Namespace "root\cimv2" -Class Win32_DisplayControllerConfiguration

foreach ($controller in $displayControllers) {
    Write-Host "  Display Controller: $($controller.Name)" -ForegroundColor White
    Write-Host "  Resolution: $($controller.HorizontalResolution) x $($controller.VerticalResolution)" -ForegroundColor White
    Write-Host "  Refresh Rate: $($controller.RefreshRate) Hz" -ForegroundColor White
    Write-Host "  Bits Per Pel: $($controller.BitsPerPel)" -ForegroundColor White
}
Write-Host ""

# Monitor Raw EDID Data
Write-Host "Collecting Monitor EDID Data..." -ForegroundColor Yellow
try {
    $monitors = Get-WmiObject -Namespace "root\wmi" -Class WmiMonitorRawEdidData -ErrorAction SilentlyContinue
    if ($monitors) {
        $i = 0
        foreach ($monitor in $monitors) {
            $i++
            Write-Host "Monitor $i EDID Data Length: $($monitor.RawEdidData.Count) bytes" -ForegroundColor Green
            
            # Parse EDID for detailed timing information
            $edid = $monitor.RawEdidData
            if ($edid.Count -gt 0) {
                Write-Host "  EDID Header: $([System.BitConverter]::ToString($edid[0..7]))" -ForegroundColor Gray
                Write-Host "  Manufacturer ID: $([System.BitConverter]::ToString($edid[8..9]))" -ForegroundColor Gray
                Write-Host "  Product Code: $([System.BitConverter]::ToString($edid[10..11]))" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "EDID data not available" -ForegroundColor Gray
    }
} catch {
    Write-Host "EDID collection failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Desktop Wallpaper and Scaling
Write-Host "Collecting Desktop Configuration..." -ForegroundColor Yellow
$desktop = Get-WmiObject -Namespace "root\cimv2" -Class Win32_Desktop
Write-Host "  Wallpaper: $($desktop.Wallpaper)" -ForegroundColor White
Write-Host "  Screen Saver Active: $($desktop.ScreenSaverActive)" -ForegroundColor White
Write-Host "  DPI Awareness: Not directly available via WMI" -ForegroundColor Gray
Write-Host ""

# Virtual Display Information
Write-Host "Analyzing Virtual Displays..." -ForegroundColor Yellow
$virtualDisplays = Get-PnpDevice | Where-Object { $_.Class -eq "Display" -and $_.FriendlyName -like "*Virtual*" -or $_.FriendlyName -like "*Meta*" -or $_.FriendlyName -like "*VR*" }

foreach ($vd in $virtualDisplays) {
    Write-Host "  Virtual Display: $($vd.FriendlyName)" -ForegroundColor Magenta
    Write-Host "    Status: $($vd.Status)" -ForegroundColor White
    Write-Host "    Instance ID: $($vd.InstanceId)" -ForegroundColor Gray
}
Write-Host ""

# Display Adapter Registry Information
Write-Host "Collecting Registry Display Information..." -ForegroundColor Yellow
$regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
if (Test-Path $regPath) {
    Write-Host "Graphics Drivers Registry Path exists" -ForegroundColor Green
    $subKeys = Get-ChildItem $regPath -ErrorAction SilentlyContinue
    Write-Host "  Sub-keys found: $($subKeys.Count)" -ForegroundColor White
    foreach ($key in $subKeys) {
        Write-Host "    $($key.Name)" -ForegroundColor Gray
    }
} else {
    Write-Host "Graphics Drivers Registry Path not found" -ForegroundColor Red
}
Write-Host ""

# GPU Memory Usage
Write-Host "Collecting GPU Memory Information..." -ForegroundColor Yellow
try {
    $gpuCounters = Get-Counter "\GPU Process Memory(*)" -ErrorAction SilentlyContinue
    if ($gpuCounters) {
        Write-Host "GPU Memory Counters Available" -ForegroundColor Green
    } else {
        Write-Host "GPU Memory Counters not available" -ForegroundColor Gray
    }
} catch {
    Write-Host "GPU Memory collection failed" -ForegroundColor Gray
}
Write-Host ""

# Display Port Information
Write-Host "Collecting Display Port/Connector Information..." -ForegroundColor Yellow
$displayPorts = Get-WmiObject -Namespace "root\wmi" -Class WmiMonitorConnectionParams -ErrorAction SilentlyContinue
if ($displayPorts) {
    foreach ($port in $displayPorts) {
        Write-Host "  Video Output Technology: $($port.VideoOutputTechnology)" -ForegroundColor Green
        Write-Host "  Instance Name: $($port.InstanceName)" -ForegroundColor Gray
    }
} else {
    Write-Host "Display Port information not available" -ForegroundColor Gray
}
Write-Host ""

# Export comprehensive data
$deepAnalysisData = @{
    Timestamp = (Get-Date).ToString("o")
    GPU = @{
        Name = $gpu.Name
        DriverVersion = $gpu.DriverVersion
        VRAM_GB = [math]::Round($gpu.AdapterRAM / 1GB, 2)
        CurrentRefreshRate = $gpu.CurrentRefreshRate
        CurrentResolution = "$($gpu.CurrentHorizontalResolution)x$($gpu.CurrentVerticalResolution)"
        ColorDepth = $gpu.CurrentBitsPerPixel
    }
    VirtualDisplays = $virtualDisplays | ForEach-Object {
        @{
            FriendlyName = $_.FriendlyName
            Status = $_.Status
            InstanceId = $_.InstanceId
        }
    }
    DisplayControllers = $displayControllers | ForEach-Object {
        @{
            Name = $_.Name
            Resolution = "$($_.HorizontalResolution)x$($_.VerticalResolution)"
            RefreshRate = $_.RefreshRate
            BitsPerPel = $_.BitsPerPel
        }
    }
}

$jsonOutput = $deepAnalysisData | ConvertTo-Json -Depth 4
$jsonOutput | Out-File -FilePath "deep_gpu_analysis.json" -Encoding UTF8

Write-Host "Deep GPU analysis data exported to: deep_gpu_analysis.json" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Output $jsonOutput
