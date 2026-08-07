# Professional Monitor Information Gathering Script
# Uses WMI and .NET framework for accurate display detection

Write-Host "Professional Monitor Analysis System - Data Collection" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

# Get monitor information using WMI
Write-Host "Collecting monitor data via WMI..." -ForegroundColor Yellow

$monitors = Get-WmiObject -Namespace "root\wmi" -Class WmiMonitorID -ErrorAction SilentlyContinue
$displaySettings = Get-WmiObject -Namespace "root\cimv2" -Class Win32_DesktopMonitor -ErrorAction SilentlyContinue
$videoControllers = Get-WmiObject -Namespace "root\cimv2" -Class Win32_VideoController -ErrorAction SilentlyContinue
$screenInfo = Get-WmiObject -Namespace "root\cimv2" -Class Win32_Desktop -ErrorAction SilentlyContinue

# Get display configuration using .NET
Add-Type -AssemblyName System.Windows.Forms
$screenCount = [System.Windows.Forms.Screen]::AllScreens.Count

Write-Host "Detected $screenCount display(s)" -ForegroundColor Green
Write-Host ""

# Collect detailed screen information
$screenData = @()
$i = 0

foreach ($screen in [System.Windows.Forms.Screen]::AllScreens) {
    $i++
    Write-Host "Display $i Information:" -ForegroundColor Cyan
    Write-Host "-" * 80 -ForegroundColor Cyan
    
    $isPrimary = $screen.Primary
    $bounds = $screen.Bounds
    $workingArea = $screen.WorkingArea
    
    $screenInfoObj = [PSCustomObject]@{
        Index = $i
        DeviceName = $screen.DeviceName
        Primary = $isPrimary
        BoundsWidth = $bounds.Width
        BoundsHeight = $bounds.Height
        BoundsX = $bounds.X
        BoundsY = $bounds.Y
        WorkingAreaWidth = $workingArea.Width
        WorkingAreaHeight = $workingArea.Height
        BitsPerPixel = if ($screenInfo) { $screenInfo[0].ScreenWidth } else { 32 }
    }
    
    Write-Host "  Device Name: $($screen.DeviceName)" -ForegroundColor White
    Write-Host "  Primary: $isPrimary" -ForegroundColor White
    Write-Host "  Resolution: $($bounds.Width) x $($bounds.Height)" -ForegroundColor White
    Write-Host "  Position: ($($bounds.X), $($bounds.Y))" -ForegroundColor White
    Write-Host "  Working Area: $($workingArea.Width) x $($workingArea.Height)" -ForegroundColor White
    Write-Host ""
    
    $screenData += $screenInfoObj
}

# Get refresh rate information from registry
Write-Host "Collecting refresh rate data from registry..." -ForegroundColor Yellow

$refreshRates = @()
$regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Configuration"

if (Test-Path $regPath) {
    $configs = Get-ChildItem $regPath -Recurse -ErrorAction SilentlyContinue
    
    foreach ($config in $configs) {
        $refreshRate = Get-ItemProperty $config.PSPath -Name "RefreshRate" -ErrorAction SilentlyContinue
        if ($refreshRate) {
            $refreshRates += [PSCustomObject]@{
                Path = $config.PSPath
                RefreshRate = $refreshRate.RefreshRate
            }
        }
    }
}

# Try to get current refresh rate from PNP devices
Write-Host "Collecting PNP display information..." -ForegroundColor Yellow

$pnpDisplays = Get-PnpDevice -Class Display | Where-Object { $_.Status -eq "OK" }

foreach ($display in $pnpDisplays) {
    Write-Host "  PNP Device: $($display.FriendlyName)" -ForegroundColor White
    Write-Host "    Instance ID: $($display.InstanceId)" -ForegroundColor Gray
}

# Export data to JSON
$outputData = @{
    Timestamp = (Get-Date).ToString("o")
    ScreenCount = $screenCount
    Screens = $screenData
    RefreshRates = $refreshRates
    PNPDisplays = $pnpDisplays | ForEach-Object {
        @{
            FriendlyName = $_.FriendlyName
            InstanceId = $_.InstanceId
            Status = $_.Status
        }
    }
}

$jsonOutput = $outputData | ConvertTo-Json -Depth 4
$jsonOutput | Out-File -FilePath "monitor_data.json" -Encoding UTF8

Write-Host ""
Write-Host "Data exported to: monitor_data.json" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan

# Return the JSON for Python processing
Write-Output $jsonOutput
