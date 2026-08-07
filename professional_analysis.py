#!/usr/bin/env python3
"""
Professional Monitor Analysis System - Final Version
Processes monitor data and performs comprehensive analysis
"""

import json
import math
import ctypes
import ctypes.wintypes
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum
import datetime

class MonitorRiskLevel(Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class MonitorSpecs:
    """Comprehensive monitor specifications"""
    device_name: str
    primary: bool
    resolution_width: int
    resolution_height: int
    position_x: int
    position_y: int
    working_area_width: int
    working_area_height: int
    refresh_rate: int = 60  # Default, will be updated
    color_depth: int = 32  # Default
    diagonal_inches: Optional[float] = None
    ppi: Optional[float] = None
    pixel_pitch_mm: Optional[float] = None
    total_pixels: Optional[int] = None
    aspect_ratio: Optional[str] = None
    risk_level: Optional[MonitorRiskLevel] = None
    risk_factors: List[str] = None
    graphics_card: str = ""

class ProfessionalMonitorAnalyzer:
    """Advanced monitor analysis with motion sickness risk assessment"""
    
    def __init__(self):
        self.monitors: List[MonitorSpecs] = []
        self.user32 = ctypes.windll.user32
        
    def load_monitor_data(self, json_file: str = "monitor_data.json"):
        """Load monitor data from PowerShell export"""
        with open(json_file, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        
        for screen_data in data['Screens']:
            # Calculate total pixels
            total_pixels = screen_data['BoundsWidth'] * screen_data['BoundsHeight']
            
            # Calculate aspect ratio
            aspect_ratio = self._calculate_aspect_ratio(screen_data['BoundsWidth'], screen_data['BoundsHeight'])
            
            specs = MonitorSpecs(
                device_name=screen_data['DeviceName'],
                primary=screen_data['Primary'],
                resolution_width=screen_data['BoundsWidth'],
                resolution_height=screen_data['BoundsHeight'],
                position_x=screen_data['BoundsX'],
                position_y=screen_data['BoundsY'],
                working_area_width=screen_data['WorkingAreaWidth'],
                working_area_height=screen_data['WorkingAreaHeight'],
                total_pixels=total_pixels,
                aspect_ratio=aspect_ratio,
                risk_factors=[]
            )
            
            self.monitors.append(specs)
        
        # Add graphics card info if available
        if data.get('PNPDisplays'):
            for display in data['PNPDisplays']:
                if 'Radeon' in display.get('FriendlyName', '') or 'NVIDIA' in display.get('FriendlyName', '') or 'Intel' in display.get('FriendlyName', ''):
                    for monitor in self.monitors:
                        monitor.graphics_card = display['FriendlyName']
                        break
        
        return self.monitors
    
    def get_refresh_rates(self):
        """Get refresh rates using Windows API"""
        for monitor in self.monitors:
            device_name = monitor.device_name
            
            # Try to get current display settings
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
            
            devmode = DEVMODE()
            devmode.dmSize = ctypes.sizeof(devmode)
            
            # Try to get current settings
            try:
                if self.user32.EnumDisplaySettingsW(device_name, -1, ctypes.byref(devmode)):
                    if devmode.dmDisplayFrequency > 0:
                        monitor.refresh_rate = devmode.dmDisplayFrequency
                    if devmode.dmBitsPerPel > 0:
                        monitor.color_depth = devmode.dmBitsPerPel
            except:
                pass
            
            # If still 0, try iterating through modes
            if monitor.refresh_rate == 0:
                for mode_num in range(0, 20):
                    devmode = DEVMODE()
                    devmode.dmSize = ctypes.sizeof(devmode)
                    
                    try:
                        if self.user32.EnumDisplaySettingsW(device_name, mode_num, ctypes.byref(devmode)):
                            if devmode.dmPelsWidth == monitor.resolution_width and devmode.dmPelsHeight == monitor.resolution_height:
                                if devmode.dmDisplayFrequency > monitor.refresh_rate:
                                    monitor.refresh_rate = devmode.dmDisplayFrequency
                                if devmode.dmBitsPerPel > 0:
                                    monitor.color_depth = devmode.dmBitsPerPel
                    except:
                        pass
            
            # Fallback to common refresh rates if still 0
            if monitor.refresh_rate == 0:
                monitor.refresh_rate = 60  # Most common default
    
    def _calculate_aspect_ratio(self, width: int, height: int) -> str:
        """Calculate simplified aspect ratio"""
        gcd = math.gcd(width, height)
        return f"{width//gcd}:{height//gcd}"
    
    def estimate_physical_dimensions(self):
        """Estimate physical dimensions and calculate PPI"""
        for monitor in self.monitors:
            # Estimate based on resolution and aspect ratio
            if monitor.resolution_width == 1920 and monitor.resolution_height == 1080:
                monitor.diagonal_inches = 24.0  # Standard 1080p monitor
            elif monitor.resolution_width == 2560 and monitor.resolution_height == 1440:
                monitor.diagonal_inches = 27.0  # Standard 1440p monitor
            elif monitor.resolution_width == 3840 and monitor.resolution_height == 2160:
                monitor.diagonal_inches = 32.0  # Standard 4K monitor
            elif monitor.resolution_width == 1440 and monitor.resolution_height == 900:
                monitor.diagonal_inches = 19.0  # Common laptop size
            elif monitor.resolution_width == 1366 and monitor.resolution_height == 768:
                monitor.diagonal_inches = 15.6  # Standard laptop
            else:
                # Calculate based on pixel density assumption
                # Assume ~100 PPI as baseline
                diagonal_pixels = math.sqrt(monitor.resolution_width**2 + monitor.resolution_height**2)
                monitor.diagonal_inches = diagonal_pixels / 100.0
            
            # Calculate PPI
            if monitor.diagonal_inches:
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
                        risk_factors.append(f"MODERATE: Refresh rate mismatch with other monitor ({monitor.refresh_rate}Hz vs {other.refresh_rate}Hz)")
                        if risk_level == MonitorRiskLevel.LOW:
                            risk_level = MonitorRiskLevel.MODERATE
            
            # Factor 4: Color depth
            if monitor.color_depth < 24:
                risk_factors.append(f"MODERATE: Low color depth ({monitor.color_depth}-bit) - may cause visual fatigue")
                if risk_level == MonitorRiskLevel.LOW:
                    risk_level = MonitorRiskLevel.MODERATE
            
            # Factor 5: Aspect ratio considerations
            if monitor.aspect_ratio == "16:10":
                risk_factors.append("MODERATE: 16:10 aspect ratio - less common, may cause scaling issues")
                if risk_level == MonitorRiskLevel.LOW:
                    risk_level = MonitorRiskLevel.MODERATE
            
            # Factor 6: Position offset (monitors at different heights)
            if len(self.monitors) > 1:
                other_monitors = [m for m in self.monitors if m != monitor]
                for other in other_monitors:
                    if abs(monitor.position_y - other.position_y) > 100:
                        risk_factors.append(f"MODERATE: Vertical position mismatch ({abs(monitor.position_y - other.position_y)}px difference) - can cause neck strain")
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
        report.append("PROFESSIONAL MONITOR ANALYSIS REPORT - FINAL")
        report.append("Advanced Display Characterization & Motion Sickness Risk Assessment")
        report.append(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")
        
        # System overview
        report.append("SYSTEM OVERVIEW")
        report.append("-" * 80)
        report.append(f"Total Monitors Detected: {len(self.monitors)}")
        if len(self.monitors) > 0:
            total_width = sum(m.resolution_width for m in self.monitors)
            max_height = max(m.resolution_height for m in self.monitors)
            report.append(f"Combined Desktop Resolution: {total_width}x{max_height}")
            report.append(f"Total Pixels Across All Displays: {sum(m.total_pixels for m in self.monitors):,}")
            report.append(f"Graphics Adapter: {self.monitors[0].graphics_card if self.monitors[0].graphics_card else 'Not detected'}")
        report.append("")
        
        # Individual monitor analysis
        for idx, monitor in enumerate(self.monitors, 1):
            report.append(f"MONITOR {idx} - {'PRIMARY DISPLAY' if monitor.primary else 'SECONDARY DISPLAY'}")
            report.append("-" * 80)
            report.append(f"Device Name: {monitor.device_name}")
            report.append("")
            report.append("DISPLAY SPECIFICATIONS:")
            report.append(f"  Resolution: {monitor.resolution_width} x {monitor.resolution_height}")
            report.append(f"  Aspect Ratio: {monitor.aspect_ratio}")
            report.append(f"  Total Pixels: {monitor.total_pixels:,}")
            report.append(f"  Refresh Rate: {monitor.refresh_rate} Hz")
            report.append(f"  Color Depth: {monitor.color_depth}-bit")
            report.append(f"  Desktop Position: ({monitor.position_x}, {monitor.position_y})")
            report.append(f"  Working Area: {monitor.working_area_width} x {monitor.working_area_height}")
            report.append("")
            
            if monitor.diagonal_inches:
                report.append("PHYSICAL CHARACTERISTICS:")
                report.append(f"  Estimated Diagonal Size: {monitor.diagonal_inches}\"")
                report.append(f"  Pixel Density (PPI): {monitor.ppi:.2f} PPI")
                report.append(f"  Pixel Pitch: {monitor.pixel_pitch_mm:.3f} mm")
                report.append("")
            
            report.append("MOTION SICKNESS RISK ASSESSMENT:")
            report.append(f"  Overall Risk Level: {monitor.risk_level.value}")
            
            if monitor.risk_factors:
                report.append("  Detected Risk Factors:")
                for factor in monitor.risk_factors:
                    report.append(f"    • {factor}")
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
                        significance = "SIGNIFICANT" if ppi_diff > 30 else "MINIMAL"
                        report.append(f"  PPI Difference: {ppi_diff:.2f} PPI ({significance})")
                    
                    refresh_diff = abs(m1.refresh_rate - m2.refresh_rate)
                    report.append(f"  Refresh Rate Difference: {refresh_diff} Hz")
                    
                    if m1.total_pixels and m2.total_pixels and m2.total_pixels > 0:
                        pixel_ratio = m1.total_pixels / m2.total_pixels
                        report.append(f"  Pixel Count Ratio: {pixel_ratio:.2f}x")
                    
                    height_diff = abs(m1.position_y - m2.position_y)
                    report.append(f"  Vertical Position Difference: {height_diff} pixels")
                    report.append("")
        
        # Motion sickness analysis
        report.append("MOTION SICKNESS ANALYSIS")
        report.append("-" * 80)
        report.append("Potential causes of motion sickness in multi-monitor setups:")
        report.append("  • PPI mismatch causing different perceived image scales")
        report.append("  • Refresh rate differences causing motion inconsistency")
        report.append("  • Vertical misalignment requiring frequent head movement")
        report.append("  • Frame pacing issues between displays")
        report.append("  • Color/brightness calibration differences")
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
            report.append("")
        
        report.append("OPTIMIZATION RECOMMENDATIONS:")
        report.append("  • Enable AMD FreeSync (Radeon RX 580 supports this) to reduce frame tearing")
        report.append("  • Match refresh rates across both monitors if possible")
        report.append("  • Use Windows display scaling to normalize perceived UI size across monitors")
        report.append("  • Align monitors vertically to reduce neck strain")
        report.append("  • Calibrate color profiles to match brightness and color temperature")
        report.append("  • Reduce motion blur reduction features if causing discomfort")
        report.append("  • Ensure DisplayPort/HDMI cables are properly connected for high refresh rates")
        report.append("  • Consider using a single monitor setup temporarily to isolate the issue")
        report.append("  • Check for VR headset (Meta Virtual Monitor) interference with display settings")
        report.append("")
        
        report.append("TECHNICAL NOTES:")
        report.append("  • Radeon RX 580 supports FreeSync for smoother motion")
        report.append("  • 1440x900 resolution suggests older or secondary display")
        report.append("  • PPI differences between monitors can cause motion discomfort")
        report.append("  • Virtual monitor presence may affect display timing")
        
        report.append("")
        report.append("=" * 80)
        report.append("END OF PROFESSIONAL ANALYSIS REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)

def main():
    """Main execution function"""
    print("Professional Monitor Analysis System - Final Version")
    print("=" * 80)
    
    analyzer = ProfessionalMonitorAnalyzer()
    
    # Load monitor data
    print("Loading monitor data...")
    monitors = analyzer.load_monitor_data()
    print(f"Loaded {len(monitors)} monitor(s)")
    print()
    
    # Get refresh rates
    print("Detecting refresh rates...")
    analyzer.get_refresh_rates()
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
    print("Generating comprehensive technical report...")
    print()
    report = analyzer.generate_technical_report()
    print(report)
    
    # Save report to file
    with open("professional_analysis_report.txt", 'w', encoding='utf-8') as f:
        f.write(report)
    print("\nReport saved to: professional_analysis_report.txt")

if __name__ == "__main__":
    main()
