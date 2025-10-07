from pydantic import BaseModel
from typing import Optional

class EngineData(BaseModel):
    position: str 
    serial_number_installed: str 
    serial_number_original: str 
    present_location: str 
    total_time_since_new: float
    total_cycles_since_new: int
    hours_flown_during_month: float 
    cycles_during_month: int 

class LandingGearData(BaseModel):
    gear_type: str 
    serial_number: str 
    total_time_since_new: float 
    total_cycles_since_new: int
    total_hours_flown_during_month: float 
    total_cycles_made_during_month: int 

class AircraftUtilization(BaseModel):
    msn: str 
    registration: str 
    aircraft_type: str 
    month: str 
    aircraft_total_time_since_new: float 
    aircraft_total_cycles_since_new: int 
    hours_flown_during_month: float 
    cycles_landings_during_month: int
    days_flown: Optional[int] 
    engines: list[EngineData]
    landing_gears: list[LandingGearData]