# Quantum-Level Display Analysis
# Investigates displacement convergence, scaling factors, and rendering anomalies

Write-Host "QUANTUM-LEVEL DISPLAY PIPELINE ANALYSIS" -ForegroundColor Magenta
Write-Host "=" * 80 -ForegroundColor Magenta

# Display Scaling Factors from Registry
Write-Host "Analyzing Display Scaling Factors..." -ForegroundColor Yellow
$scalePath = "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\ScaleFactors"
if (Test-Path $scalePath) {
    Write-Host "ScaleFactors registry key found" -ForegroundColor Green
    $scaleKeys = Get-ChildItem $scalePath -ErrorAction SilentlyContinue
    foreach ($key in $scaleKeys) {
        Write-Host "  Scale Key: $($key.Name)" -ForegroundColor Cyan
        $values = Get-ItemProperty $key.PSPath -ErrorAction SilentlyContinue
        foreach ($prop in $values.PSObject.Properties) {
            if ($prop.Name -notlike "PS*") {
                Write-Host "    $($prop.Name): $($prop.Value)" -ForegroundColor White
            }
        }
    }
} else {
    Write-Host "ScaleFactors not found in registry" -ForegroundColor Gray
}
Write-Host ""

# DPI Awareness and Scaling
Write-Host "Collecting DPI Awareness Information..." -ForegroundColor Yellow
try {
    Add-Type -AssemblyName System.Windows.Forms
    $graphics = [System.Drawing.Graphics]::FromHwnd([System.Windows.Forms.Control]::Handle)
    $dpiX = $graphics.DpiX
    $dpiY = $graphics.DpiY
    Write-Host "  System DPI X: $dpiX" -ForegroundColor Green
    Write-Host "  System DPI Y: $dpiY" -ForegroundColor Green
    Write-Host "  Scaling Factor: $([math]::Round($dpiX / 96, 2))x" -ForegroundColor Green
} catch {
    Write-Host "  DPI collection failed" -ForegroundColor Gray
}
Write-Host ""

# ClearType and Sub-pixel Rendering
Write-Host "Analyzing Sub-pixel Rendering Settings..." -ForegroundColor Yellow
try {
    $cleartypePath = "HKCU:\Control Panel\Desktop"
    $cleartype = Get-ItemProperty $cleartypePath -ErrorAction SilentlyContinue
    Write-Host "  Font Smoothing: $($cleartype.FontSmoothing)" -ForegroundColor White
    Write-Host "  Font Smoothing Type: $($cleartype.FontSmoothingType)" -ForegroundColor White
    Write-Host "  Font Smoothing Contrast: $($cleartype.FontSmoothingContrast)" -ForegroundColor White
    Write-Host "  ClearType Text: $($cleartype.ClearTypeText)" -ForegroundColor White
} catch {
    Write-Host "  ClearType settings collection failed" -ForegroundColor Gray
}
Write-Host ""

# Monitor Timing and Convergence
Write-Host "Analyzing Monitor Timing Parameters..." -ForegroundColor Yellow
try {
    $timingInfo = Get-WmiObject -Namespace "root\wmi" -Class WmiMonitorTiming -ErrorAction SilentlyContinue
    if ($timingInfo) {
        foreach ($timing in $timingInfo) {
            Write-Host "  Monitor: $($timing.InstanceName)" -ForegroundColor Cyan
            Write-Host "    Horizontal Frequency: $($timing.HorizontalFrequency) kHz" -ForegroundColor White
            Write-Host "    Vertical Frequency: $($timing.VerticalFrequency) Hz" -ForegroundColor White
            Write-Host "    Timing Status: $($timing.TimingStatus)" -ForegroundColor White
        }
    } else {
        Write-Host "  Timing information not available" -ForegroundColor Gray
    }
} catch {
    Write-Host "  Timing collection failed" -ForegroundColor Gray
}
Write-Host ""

# Display Brightness and Contrast
Write-Host "Analyzing Display Brightness Levels..." -ForegroundColor Yellow
try {
    $brightness = Get-WmiObject -Namespace "root\wmi" -Class WmiMonitorBrightness -ErrorAction SilentlyContinue
    if ($brightness) {
        Write-Host "  Current Brightness: $($brightness.CurrentBrightness)" -ForegroundColor Green
        Write-Host "  Maximum Brightness: $($brightness.MaxBrightness)" -ForegroundColor Green
    } else {
        Write-Host "  Brightness information not available" -ForegroundColor Gray
    }
} catch {
    Write-Host "  Brightness collection failed" -ForegroundColor Gray
}
Write-Host ""

# GPU Rendering Pipeline
Write-Host "Analyzing GPU Rendering Pipeline..." -ForegroundColor Yellow
try {
    $gpuPipeline = Get-WmiObject -Namespace "root\cimv2" -Class Win32_VideoConfiguration -ErrorAction SilentlyContinue
    if ($gpuPipeline) {
        foreach ($pipeline in $gpuPipeline) {
            Write-Host "  Adapter: $($pipeline.Name)" -ForegroundColor Cyan
            Write-Host "  Refresh Rate: $($pipeline.RefreshRate)" -ForegroundColor White
            Write-Host "  Horizontal Resolution: $($pipeline.HorizontalResolution)" -ForegroundColor White
            Write-Host "  Vertical Resolution: $($pipeline.VerticalResolution)" -ForegroundColor White
        }
    } else {
        Write-Host "  GPU pipeline information not available via WMI" -ForegroundColor Gray
    }
} catch {
    Write-Host "  GPU pipeline collection failed" -ForegroundColor Gray
}
Write-Host ""

# Frame Buffer and Memory Analysis
Write-Host "Analyzing Frame Buffer Configuration..." -ForegroundColor Yellow
try {
    $frameBuffer = Get-WmiObject -Namespace "root\cimv2" -Class Win32_VideoSettings -ErrorAction SilentlyContinue
    if ($frameBuffer) {
        foreach ($fb in $frameBuffer) {
            Write-Host "  Setting: $($fb.Caption)" -ForegroundColor Cyan
        }
    } else {
        Write-Host "  Frame buffer information not available" -ForegroundColor Gray
    }
} catch {
    Write-Host "  Frame buffer collection failed" -ForegroundColor Gray
}
Write-Host ""

# Virtual Display Interference Analysis
Write-Host "Analyzing Virtual Display Interference..." -ForegroundColor Yellow
$allDisplays = Get-PnpDevice -Class Display
$virtualCount = 0
$physicalCount = 0

foreach ($display in $allDisplays) {
    if ($display.FriendlyName -like "*Virtual*" -or $display.FriendlyName -like "*Meta*" -or $display.FriendlyName -like "*VR*" -or $display.InstanceId -like "*BTHENUM*") {
        $virtualCount++
        Write-Host "  VIRTUAL: $($display.FriendlyName)" -ForegroundColor Magenta
        Write-Host "    Instance: $($display.InstanceId)" -ForegroundColor Gray
    } elseif ($display.Status -eq "OK") {
        $physicalCount++
        Write-Host "  PHYSICAL: $($display.FriendlyName)" -ForegroundColor Green
    }
}

Write-Host "  Total Virtual Displays: $virtualCount" -ForegroundColor Yellow
Write-Host "  Total Physical Displays: $physicalCount" -ForegroundColor Yellow
Write-Host "  Interference Risk: $(if ($virtualCount -gt 2) { 'HIGH' } elseif ($virtualCount -gt 0) { 'MODERATE' } else { 'LOW' })" -ForegroundColor $(if ($virtualCount -gt 2) { 'Red' } elseif ($virtualCount -gt 0) { 'Yellow' } else { 'Green' })
Write-Host ""

# Display Convergence Analysis
Write-Host "Analyzing Display Convergence Parameters..." -ForegroundColor Yellow
$convergenceData = @{
    VirtualDisplayCount = $virtualCount
    PhysicalDisplayCount = $physicalCount
    InterferenceRisk = if ($virtualCount -gt 2) { "HIGH" } elseif ($virtualCount -gt 0) { "MODERATE" } else { "LOW" }
    ScaleFactorsDetected = (Test-Path $scalePath)
    DPIScaling = if ($dpiX) { [math]::Round($dpiX / 96, 2) } else { 1.0 }
}

Write-Host "  Convergence Analysis:" -ForegroundColor Cyan
Write-Host "    Virtual/Physical Ratio: $([math]::Round($virtualCount / [math]::Max($physicalCount, 1), 2))" -ForegroundColor White
Write-Host "    DPI Scaling Factor: $($convergenceData.DPIScaling)x" -ForegroundColor White
Write-Host "    Scale Factors Present: $($convergenceData.ScaleFactorsDetected)" -ForegroundColor White
Write-Host ""

# Export quantum analysis data
$quantumData = @{
    Timestamp = (Get-Date).ToString("o")
    ConvergenceAnalysis = $convergenceData
    VirtualDisplays = $virtualCount
    PhysicalDisplays = $physicalCount
    DPIScaling = if ($dpiX) { [math]::Round($dpiX / 96, 2) } else { 1.0 }
    SystemDPI = @{
        X = if ($dpiX) { $dpiX } else { 96 }
        Y = if ($dpiY) { $dpiY } else { 96 }
    }
    ClearTypeSettings = @{
        FontSmoothing = if ($cleartype) { $cleartype.FontSmoothing } else { "Unknown" }
        FontSmoothingType = if ($cleartype) { $cleartype.FontSmoothingType } else { "Unknown" }
        ClearTypeText = if ($cleartype) { $cleartype.ClearTypeText } else { "Unknown" }
    }
}

$jsonOutput = $quantumData | ConvertTo-Json -Depth 4
$jsonOutput | Out-File -FilePath "quantum_display_analysis.json" -Encoding UTF8

Write-Host "Quantum display analysis exported to: quantum_display_analysis.json" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Magenta
Write-Output $jsonOutput
