#!/usr/bin/env python3
"""
Professional-Grade Monitor Analysis System v2
Advanced pixel density and display characteristics analysis
Uses multiple Windows API methods for accurate data retrieval
"""

import ctypes
import ctypes.wintypes
import math
import json
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum

# Windows API constants
ENUM_CURRENT_SETTINGS = -1
ENUM_REGISTRY_SETTINGS = -2

class DISPLAY_DEVICE(ctypes.Structure):
    _fields_ = [
        ('cb', ctypes.wintypes.DWORD),
        ('DeviceName', ctypes.wintypes.WCHAR * 32),
        ('DeviceString', ctypes.wintypes.WCHAR * 128),
        ('StateFlags', ctypes.wintypes.DWORD),
        ('DeviceID', ctypes.wintypes.WCHAR * 128),
        ('DeviceKey', ctypes.wintypes.WCHAR * 128)
    ]

class DEVMODE(ctypes.Structure):
    _fields_ = [
        ('dmDeviceName', ctypes.wintypes.WCHAR * 32),
        ('dmSpecVersion', ctypes.wintypes.WORD),
        ('dmDriverVersion', ctypes.wintypes.WORD),
        ('dmSize', ctypes.wintypes.WORD),
        ('dmDriverExtra', ctypes.wintypes.WORD),
        ('dmFields', ctypes.wintypes.DWORD),
        ('dmPosition', ctypes.wintypes.POINT),
        ('dmDisplayOrientation', ctypes.wintypes.DWORD),
        ('dmDisplayFixedOutput', ctypes.wintypes.DWORD),
        ('dmColor', ctypes.wintypes.DWORD),
        ('dmDuplex', ctypes.wintypes.DWORD),
        ('dmYResolution', ctypes.wintypes.DWORD),
        ('dmTTCOption', ctypes.wintypes.DWORD),
        ('dmCollate', ctypes.wintypes.DWORD),
        ('dmFormName', ctypes.wintypes.WCHAR * 32),
        ('dmLogPixels', ctypes.wintypes.WORD),
        ('dmBitsPerPel', ctypes.wintypes.DWORD),
        ('dmPelsWidth', ctypes.wintypes.DWORD),
        ('dmPelsHeight', ctypes.wintypes.DWORD),
        ('dmDisplayFlags', ctypes.wintypes.DWORD),
        ('dmDisplayFrequency', ctypes.wintypes.DWORD),
        ('dmICMMethod', ctypes.wintypes.DWORD),
        ('dmICMIntent', ctypes.wintypes.DWORD),
        ('dmMediaType', ctypes.wintypes.DWORD),
        ('dmDitherType', ctypes.wintypes.DWORD),
        ('dmReserved1', ctypes.wintypes.DWORD),
        ('dmReserved2', ctypes.wintypes.DWORD),
        ('dmReserved3', ctypes.wintypes.DWORD),
        ('dmReserved4', ctypes.wintypes.DWORD),
    ]

class MonitorRiskLevel(Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class MonitorSpecs:
    """Comprehensive monitor specifications"""
    device_name: str
    device_string: str
    device_id: str
    primary: bool
    resolution_width: int
    resolution_height: int
    refresh_rate: int
    color_depth: int
    position_x: int
    position_y: int
    diagonal_inches: Optional[float] = None
    ppi: Optional[float] = None
    pixel_pitch_mm: Optional[float] = None
    total_pixels: Optional[int] = None
    aspect_ratio: Optional[str] = None
    risk_level: Optional[MonitorRiskLevel] = None
    risk_factors: List[str] = None

class ProfessionalMonitorAnalyzer:
    """Advanced monitor analysis with motion sickness risk assessment"""
    
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.gdi32 = ctypes.windll.gdi32
        self.monitors: List[MonitorSpecs] = []
        
    def get_display_settings(self, device_name: str) -> Optional[DEVMODE]:
        """Get current display settings using multiple methods"""
        # Method 1: Try ENUM_CURRENT_SETTINGS
        devmode = DEVMODE()
        devmode.dmSize = ctypes.sizeof(devmode)
        
        if self.user32.EnumDisplaySettingsW(device_name, ENUM_CURRENT_SETTINGS, ctypes.byref(devmode)):
            # Verify the data is valid
            if devmode.dmPelsWidth > 0 and devmode.dmPelsHeight > 0 and devmode.dmDisplayFrequency > 0:
                return devmode
        
        # Method 2: Try iterating through all modes to find current
        mode_num = 0
        while True:
            devmode = DEVMODE()
            devmode.dmSize = ctypes.sizeof(devmode)
            
            if not self.user32.EnumDisplaySettingsW(device_name, mode_num, ctypes.byref(devmode)):
                break
            
            if devmode.dmPelsWidth > 0 and devmode.dmPelsHeight > 0:
                # Use the highest resolution mode as fallback
                return devmode
            
            mode_num += 1
        
        return None
    
    def enumerate_monitors(self) -> List[MonitorSpecs]:
        """Enumerate all connected monitors with detailed specifications"""
        monitor_count = 0
        
        for i in range(32):  # Max 32 displays
            display_device = DISPLAY_DEVICE()
            display_device.cb = ctypes.sizeof(display_device)
            
            if not self.user32.EnumDisplayDevicesW(None, i, ctypes.byref(display_device), 0):
                break
            
            # Only process active displays
            if not (display_device.StateFlags & 4):  # DISPLAY_DEVICE_ACTIVE
                continue
            
            # Get display settings
            devmode = self.get_display_settings(display_device.DeviceName)
            
            if not devmode:
                continue
                
            monitor_count += 1
            
            # Calculate total pixels
            total_pixels = devmode.dmPelsWidth * devmode.dmPelsHeight
            
            # Calculate aspect ratio
            aspect_ratio = self._calculate_aspect_ratio(devmode.dmPelsWidth, devmode.dmPelsHeight)
            
            # Determine if primary monitor
            is_primary = bool(display_device.StateFlags & 1)  # DISPLAY_DEVICE_PRIMARY_DEVICE
            
            specs = MonitorSpecs(
                device_name=display_device.DeviceName,
                device_string=display_device.DeviceString,
                device_id=display_device.DeviceID,
                primary=is_primary,
                resolution_width=devmode.dmPelsWidth,
                resolution_height=devmode.dmPelsHeight,
                refresh_rate=devmode.dmDisplayFrequency,
                color_depth=devmode.dmBitsPerPel,
                position_x=devmode.dmPosition.x,
                position_y=devmode.dmPosition.y,
                total_pixels=total_pixels,
                aspect_ratio=aspect_ratio,
                risk_factors=[]
            )
            
            self.monitors.append(specs)
        
        return self.monitors
    
    def _calculate_aspect_ratio(self, width: int, height: int) -> str:
        """Calculate simplified aspect ratio"""
        gcd = math.gcd(width, height)
        return f"{width//gcd}:{height//gcd}"
    
    def estimate_physical_dimensions(self, diagonal_inches: float = None):
        """Estimate physical dimensions and calculate PPI"""
        for monitor in self.monitors:
            if diagonal_inches:
                monitor.diagonal_inches = diagonal_inches
            else:
                # Estimate based on resolution (heuristic)
                if monitor.resolution_width >= 3840:
                    monitor.diagonal_inches = 32.0
                elif monitor.resolution_width >= 2560:
                    monitor.diagonal_inches = 27.0
                elif monitor.resolution_width >= 1920:
                    monitor.diagonal_inches = 24.0
                else:
                    monitor.diagonal_inches = 21.5
            
            # Calculate PPI
            if monitor.diagonal_inches:
                # Calculate diagonal pixels
                diagonal_pixels = math.sqrt(monitor.resolution_width**2 + monitor.resolution_height**2)
                monitor.ppi = diagonal_pixels / monitor.diagonal_inches
                
                # Calculate pixel pitch in mm
                monitor.pixel_pitch_mm = 25.4 / monitor.ppi
    
    def assess_motion_sickness_risk(self) -> Dict[str, List[str]]:
        """Advanced motion sickness risk assessment"""
        risk_assessment = {}
        
        for monitor in self.monitors:
            risk_factors = []
            risk_level = MonitorRiskLevel.LOW
            
            # Factor 1: Low refresh rate
            if monitor.refresh_rate < 60:
                risk_factors.append(f"CRITICAL: Low refresh rate ({monitor.refresh_rate}Hz) - high motion sickness risk")
                risk_level = MonitorRiskLevel.CRITICAL
            elif monitor.refresh_rate < 75:
                risk_factors.append(f"HIGH: Suboptimal refresh rate ({monitor.refresh_rate}Hz) - recommended 75Hz+")
                risk_level = MonitorRiskLevel.HIGH
            elif monitor.refresh_rate < 120:
                risk_factors.append(f"MODERATE: Refresh rate {monitor.refresh_rate}Hz - 120Hz+ recommended for sensitive users")
                if risk_level == MonitorRiskLevel.LOW:
                    risk_level = MonitorRiskLevel.MODERATE
            
            # Factor 2: Pixel density issues
            if monitor.ppi:
                if monitor.ppi < 90:
                    risk_factors.append(f"HIGH: Low pixel density ({monitor.ppi:.1f} PPI) - visible pixels may cause discomfort")
                    if risk_level == MonitorRiskLevel.LOW:
                        risk_level = MonitorRiskLevel.HIGH
                elif monitor.ppi > 150:
                    risk_factors.append(f"MODERATE: Very high pixel density ({monitor.ppi:.1f} PPI) - scaling issues possible")
                    if risk_level == MonitorRiskLevel.LOW:
                        risk_level = MonitorRiskLevel.MODERATE
            
            # Factor 3: Resolution mismatch between monitors
            if len(self.monitors) > 1:
                other_monitors = [m for m in self.monitors if m != monitor]
                for other in other_monitors:
                    if monitor.ppi and other.ppi and abs(monitor.ppi - other.ppi) > 30:
                        risk_factors.append(f"HIGH: Significant PPI mismatch with other monitor ({abs(monitor.ppi - other.ppi):.1f} PPI difference)")
                        if risk_level == MonitorRiskLevel.LOW:
                            risk_level = MonitorRiskLevel.HIGH
                    if monitor.refresh_rate != other.refresh_rate:
                        risk_factors.append(f"MODERATE: Refresh rate mismatch with other monitor")
                        if risk_level == MonitorRiskLevel.LOW:
                            risk_level = MonitorRiskLevel.MODERATE
            
            # Factor 4: Color depth
            if monitor.color_depth < 24:
                risk_factors.append(f"MODERATE: Low color depth ({monitor.color_depth}-bit) - may cause visual fatigue")
                if risk_level == MonitorRiskLevel.LOW:
                    risk_level = MonitorRiskLevel.MODERATE
            
            # Factor 5: Ultra-wide considerations
            if monitor.aspect_ratio in ["21:9", "32:9"]:
                risk_factors.append("MODERATE: Ultra-wide aspect ratio - requires careful panning settings")
                if risk_level == MonitorRiskLevel.LOW:
                    risk_level = MonitorRiskLevel.MODERATE
            
            monitor.risk_factors = risk_factors
            monitor.risk_level = risk_level
            risk_assessment[monitor.device_name] = risk_factors
        
        return risk_assessment
    
    def generate_technical_report(self) -> str:
        """Generate comprehensive technical analysis report"""
        report = []
        report.append("=" * 80)
        report.append("PROFESSIONAL MONITOR ANALYSIS REPORT v2.0")
        report.append("Advanced Display Characterization & Motion Sickness Risk Assessment")
        report.append("=" * 80)
        report.append("")
        
        # System overview
        report.append("SYSTEM OVERVIEW")
        report.append("-" * 80)
        report.append(f"Total Monitors Detected: {len(self.monitors)}")
        if len(self.monitors) > 0:
            report.append(f"Combined Resolution: {sum(m.resolution_width for m in self.monitors)}x{max(m.resolution_height for m in self.monitors)}")
            report.append(f"Total Pixels Across All Displays: {sum(m.total_pixels for m in self.monitors):,}")
        report.append("")
        
        # Individual monitor analysis
        for idx, monitor in enumerate(self.monitors, 1):
            report.append(f"MONITOR {idx} - {'PRIMARY' if monitor.primary else 'SECONDARY'}")
            report.append("-" * 80)
            report.append(f"Device Name: {monitor.device_name}")
            report.append(f"Device String: {monitor.device_string}")
            report.append(f"Device ID: {monitor.device_id}")
            report.append("")
            report.append("DISPLAY SPECIFICATIONS:")
            report.append(f"  Resolution: {monitor.resolution_width} x {monitor.resolution_height}")
            report.append(f"  Aspect Ratio: {monitor.aspect_ratio}")
            report.append(f"  Total Pixels: {monitor.total_pixels:,}")
            report.append(f"  Refresh Rate: {monitor.refresh_rate} Hz")
            report.append(f"  Color Depth: {monitor.color_depth}-bit")
            report.append(f"  Position: ({monitor.position_x}, {monitor.position_y})")
            report.append("")
            
            if monitor.diagonal_inches:
                report.append("PHYSICAL CHARACTERISTICS:")
                report.append(f"  Estimated Diagonal: {monitor.diagonal_inches}\"")
                report.append(f"  Pixel Density: {monitor.ppi:.2f} PPI")
                report.append(f"  Pixel Pitch: {monitor.pixel_pitch_mm:.3f} mm")
                report.append("")
            
            report.append("MOTION SICKNESS RISK ASSESSMENT:")
            report.append(f"  Risk Level: {monitor.risk_level.value}")
            if monitor.risk_factors:
                for factor in monitor.risk_factors:
                    report.append(f"  - {factor}")
            else:
                report.append("  No significant risk factors detected")
            report.append("")
        
        # Comparative analysis
        if len(self.monitors) > 1:
            report.append("COMPARATIVE ANALYSIS")
            report.append("-" * 80)
            
            for i in range(len(self.monitors)):
                for j in range(i + 1, len(self.monitors)):
                    m1, m2 = self.monitors[i], self.monitors[j]
                    report.append(f"Monitor {i+1} vs Monitor {j+1}:")
                    
                    if m1.ppi and m2.ppi:
                        ppi_diff = abs(m1.ppi - m2.ppi)
                        report.append(f"  PPI Difference: {ppi_diff:.2f} PPI ({'SIGNIFICANT' if ppi_diff > 30 else 'MINIMAL'})")
                    
                    refresh_diff = abs(m1.refresh_rate - m2.refresh_rate)
                    report.append(f"  Refresh Rate Difference: {refresh_diff} Hz")
                    
                    if m1.total_pixels and m2.total_pixels and m2.total_pixels > 0:
                        pixel_ratio = m1.total_pixels / m2.total_pixels
                        report.append(f"  Pixel Count Ratio: {pixel_ratio:.2f}x")
                    report.append("")
        
        # Recommendations
        report.append("PROFESSIONAL RECOMMENDATIONS")
        report.append("-" * 80)
        
        high_risk_monitors = [m for m in self.monitors if m.risk_level in [MonitorRiskLevel.HIGH, MonitorRiskLevel.CRITICAL]]
        
        if high_risk_monitors:
            report.append("URGENT - Address the following issues:")
            for monitor in high_risk_monitors:
                for factor in monitor.risk_factors:
                    if "CRITICAL" in factor or "HIGH" in factor:
                        report.append(f"  • {factor}")
        else:
            report.append("No critical issues detected. Current setup is within acceptable parameters.")
        
        report.append("")
        report.append("General Optimization Recommendations:")
        report.append("  • Enable G-Sync/FreeSync if available to reduce frame pacing issues")
        report.append("  • Match refresh rates across monitors if possible")
        report.append("  • Use display scaling to normalize perceived PPI across monitors")
        report.append("  • Consider reducing motion blur reduction features if causing discomfort")
        report.append("  • Verify proper cable connections (DisplayPort recommended for high refresh)")
        report.append("  • Calibrate color profiles for accurate color reproduction")
        
        report.append("")
        report.append("=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def export_json(self, filename: str = "monitor_analysis.json"):
        """Export analysis data to JSON"""
        import datetime
        data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "monitor_count": len(self.monitors),
            "monitors": [asdict(m) for m in self.monitors]
        }
        
        # Convert enums to strings
        for monitor in data["monitors"]:
            if monitor.get("risk_level"):
                monitor["risk_level"] = monitor["risk_level"].value
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filename

def main():
    """Main execution function"""
    print("Initializing Professional Monitor Analysis System v2.0...")
    print("=" * 80)
    
    analyzer = ProfessionalMonitorAnalyzer()
    
    # Enumerate monitors
    print("Detecting connected monitors...")
    monitors = analyzer.enumerate_monitors()
    
    if not monitors:
        print("ERROR: No monitors detected!")
        return
    
    print(f"Successfully detected {len(monitors)} monitor(s)")
    print()
    
    # Estimate physical dimensions
    print("Calculating physical characteristics...")
    analyzer.estimate_physical_dimensions()
    print()
    
    # Assess motion sickness risk
    print("Performing motion sickness risk assessment...")
    risk_assessment = analyzer.assess_motion_sickness_risk()
    print()
    
    # Generate and display report
    print("Generating technical report...")
    print()
    report = analyzer.generate_technical_report()
    print(report)
    
    # Export to JSON
    json_file = analyzer.export_json()
    print(f"\nDetailed data exported to: {json_file}")
    
    # Save report to file
    with open("monitor_analysis_report_v2.txt", 'w') as f:
        f.write(report)
    print("Report saved to: monitor_analysis_report_v2.txt")

if __name__ == "__main__":
    main()
