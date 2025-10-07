def build_aircraft_prompt() -> str:
    """Build the prompt for aircraft utilization data extraction"""
    return """
Extract aircraft utilization data from this monthly aircraft utilization report and return structured data.

**AIRCRAFT HEADER INFORMATION:**
- airline: Airline name (e.g., "TOC AIRLINES")
- month: Month and year of report (e.g., "Aug 2025")
- msn: Manufacturer Serial Number
- registration: Aircraft registration number (e.g., "A-7575")
- aircraft_type: Aircraft type (e.g., "737-800")
- days_flown: Number of days flown during the month (if available)

**COMPONENT DATA - Extract for each component:**

1. **Airframe:**
   - TSN: Aircraft Total Time Since New (hours)
   - CSN: Aircraft Total Cycles Since New
   - MonthlyUtil_Hrs: Hours flown during the month
   - MonthlyUtil_Cyc: Cycles/Landings during the month
   - SerialNumber: MSN or Aircraft Serial Number
   - location: Aircraft Registration

2. **Engine1 (Position NO.1):**
   - TSN: Total Time Since New of engine
   - CSN: Total Cycles Since New of engine
   - MonthlyUtil_Hrs: Hours flown during month
   - MonthlyUtil_Cyc: Cycles during month
   - SerialNumber: S/N of Engine Installed
   - location: Present Location of Original Engine

3. **Engine2 (Position NO.2):**
   - TSN: Total Time Since New of engine
   - CSN: Total Cycles Since New of engine
   - MonthlyUtil_Hrs: Hours flown during month
   - MonthlyUtil_Cyc: Cycles during month
   - SerialNumber: S/N of Engine Installed
   - location: Present Location of Original Engine

4. **APU (Auxiliary Power Unit):**
   - TSN: Total Time Since New of APU
   - CSN: Total Cycles Since New of APU
   - MonthlyUtil_Hrs: Hours flown during month
   - MonthlyUtil_Cyc: Cycles during month
   - SerialNumber: S/N of APU Installed
   - location: Present Location of APU

5. **LandingGearLeft (Main Landing Gear 1):**
   - TSN: Total Time Since New
   - CSN: Total Cycles Since New
   - MonthlyUtil_Hrs: Total Hours Flown During Month
   - MonthlyUtil_Cyc: Total Cycles Made During Month
   - SerialNumber: S/N of Landing Gear Installed
   - location: null (or installation position if mentioned)

6. **LandingGearRight (Main Landing Gear 2):**
   - TSN: Total Time Since New
   - CSN: Total Cycles Since New
   - MonthlyUtil_Hrs: Total Hours Flown During Month
   - MonthlyUtil_Cyc: Total Cycles Made During Month
   - SerialNumber: S/N of Landing Gear Installed
   - location: null (or installation position if mentioned)

7. **LandingGearNose (Nose Landing Gear):**
   - TSN: Total Time Since New
   - CSN: Total Cycles Since New
   - MonthlyUtil_Hrs: Total Hours Flown During Month
   - MonthlyUtil_Cyc: Total Cycles Made During Month
   - SerialNumber: S/N of Landing Gear Installed
   - location: null (or installation position if mentioned)

**CRITICAL EXTRACTION RULES:**
1. All numeric values (TSN, CSN, hours, cycles) MUST be numbers, not strings
2. Use null for missing optional fields
3. TSN values are in HOURS (floating point numbers)
4. CSN values are CYCLES (integers)
5. Serial numbers are STRINGS (may contain letters and numbers)
6. If "Total Time Since New" is shown as "16,300" or "16300", extract as 16300.0
7. If a component's data is not found in the document, set all its fields to null

**DATA LOCATION HINTS:**
- Look for tables with columns for different positions (NO.1, NO.2, APU)
- Engine data typically has rows like "S/N of Engine Installed", "Total Time Since New", etc.
- Landing gear data typically has columns for "Main Landing Gear 1", "Main Landing Gear 2", "Nose Landing Gear"
- Aircraft totals are usually at the top of the document

**EXPECTED OUTPUT STRUCTURE:**
{
  "airline": "TOC AIRLINES",
  "month": "Aug 2025",
  "msn": "9999",
  "registration": "A-7575",
  "aircraft_type": "737-800",
  "days_flown": null,
  "components": {
    "Airframe": {
      "TSN": 16300.0,
      "CSN": 8200,
      "MonthlyUtil_Hrs": 197.25,
      "MonthlyUtil_Cyc": 230,
      "SerialNumber": "9999",
      "location": "A-7575"
    },
    "Engine1": { ... },
    "Engine2": { ... },
    "APU": { ... },
    "LandingGearLeft": { ... },
    "LandingGearRight": { ... },
    "LandingGearNose": { ... }
  }
}

Extract all available data from the document provided below.
"""