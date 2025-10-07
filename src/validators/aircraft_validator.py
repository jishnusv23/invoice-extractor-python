from src.models.aircraft_models import AircraftUtilization,ComponentData
from typing import Optional,List, Tuple


def validate_aircraft_utilization(data: AircraftUtilization) -> tuple[bool, list[str]]:
    """
    Validate essential aircraft utilization data
    
    Args:
        data: AircraftUtilization object to validate
        
    Returns:
        Tuple of (is_valid, list of warning messages)
    """
    warnings = []
    
  
    if not data.msn:
        warnings.append("Missing MSN (Manufacturer Serial Number)")
    
    if not data.registration:
        warnings.append("Missing aircraft registration")
    
    if not data.month:
        warnings.append("Missing month")
    
   
    components = data.components
    
    if not components.Engine1.SerialNumber:
        warnings.append("Missing Engine 1 Serial Number")
    
    if not components.Engine2.SerialNumber:
        warnings.append("Missing Engine 2 Serial Number")
    
    if not components.APU.SerialNumber:
        warnings.append("Missing APU Serial Number")
    
  
    has_airframe_data = (
        components.Airframe.TSN is not None or 
        components.Airframe.CSN is not None
    )
    
    has_engine_data = (
        components.Engine1.TSN is not None or 
        components.Engine2.TSN is not None
    )
    
    if not has_airframe_data and not has_engine_data:
        warnings.append("No utilization data found for aircraft or engines")
    

    is_valid = len(warnings) == 0
    
    return is_valid, warnings


def print_validation_results(is_valid: bool, warnings: List[str]) -> None:
    """
    Print validation results
    
    Args:
        is_valid: Whether validation passed
        warnings: List of warning messages
    """
    if is_valid:
        print("✅ Validation passed - All critical data present")
    else:
        print("⚠️ Validation warnings:")
        print("=" * 60)
        for i, warning in enumerate(warnings, 1):
            print(f"{i}. {warning}")
        print("=" * 60)