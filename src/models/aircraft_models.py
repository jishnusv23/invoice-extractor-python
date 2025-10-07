
from pydantic import BaseModel, Field
from typing import Optional



class ComponentData(BaseModel):
    """Individual component data with utilization metrics"""
    TSN: Optional[float] = Field(default=None, description="Component Time Since New (hours)")
    CSN: Optional[int] = Field(default=None, description="Component Cycles Since New")
    MonthlyUtil_Hrs: Optional[float] = Field(default=None, description="Component Monthly Utilization in Hours")
    MonthlyUtil_Cyc: Optional[int] = Field(default=None, description="Component Monthly Utilization in Cycles")
    SerialNumber: Optional[str] = Field(default=None, description="Component Serial Number")
    location: Optional[str] = Field(default=None, description="Component location information (e.g., #1, #2, MSN, tail number)")

class ExtractedComponentData(BaseModel):
    """Extracted component data with utilization metrics"""
    Airframe: Optional[ComponentData] = Field(
        default_factory=ComponentData,
        description="Airframe component with utilization metrics, TSN/CSN values, and status information"
    )
    Engine1: Optional[ComponentData] = Field(
        default_factory=ComponentData,
        description="Engine 1 component with serial report, utilization metrics, TSN/CSN values, and status information"
    )
    Engine2: Optional[ComponentData] = Field(
        default_factory=ComponentData,
        description="Engine 2 component with serial report, utilization metrics, TSN/CSN values, and status information"
    )
    APU: Optional[ComponentData] = Field(
        default_factory=ComponentData,
        description="Auxiliary Power Unit component with utilization metrics, TSN/CSN values, and status information"
    )
    LandingGearLeft: Optional[ComponentData] = Field(
        default_factory=ComponentData,
        description="Left Landing Gear component with serial report, utilization metrics, TSN/CSN values, and status information"
    )
    LandingGearRight: Optional[ComponentData] = Field(
        default_factory=ComponentData,
        description="Right Landing Gear component with serial report, utilization metrics, TSN/CSN values, and status information"
    )
    LandingGearNose: Optional[ComponentData] = Field(
        default_factory=ComponentData,
        description="Nose Landing Gear component with serial report, utilization metrics, TSN/CSN values, and status information"
    )



class AircraftUtilization(BaseModel):
    """Complete aircraft monthly utilization report"""
    airline: Optional[str] = Field(default=None, description="Airline name (e.g., TOC AIRLINES)")
    month: Optional[str] = Field(default=None, description="Month of the report (e.g., Aug 2025)")
    msn: Optional[str] = Field(default=None, description="Manufacturer Serial Number")
    registration: Optional[str] = Field(default=None, description="Aircraft registration number")
    aircraft_type: Optional[str] = Field(default=None, description="Aircraft type (e.g., 737-800)")
    days_flown: Optional[int] = Field(default=None, description="Days flown during the month")
    components: ExtractedComponentData = Field(
        default_factory=ExtractedComponentData,
        description="All aircraft components with their utilization data"
    )
