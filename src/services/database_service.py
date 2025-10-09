"""
Database service for storing aircraft utilization data using Prisma
"""
import logging
from typing import Optional, List, Tuple
from prisma import Prisma
from src.models.aircraft_models import AircraftUtilization, ComponentData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for handling database operations"""
    
    def __init__(self):
        self.db = Prisma()
        self._connected = False
    
    async def connect(self):
        """Establish database connection"""
        if not self._connected:
            await self.db.connect()
            self._connected = True
            logger.info("✅ Connected to database")
    
    async def disconnect(self):
        """Close database connection"""
        if self._connected:
            await self.db.disconnect()
            self._connected = False
            logger.info("👋 Disconnected from database")
    
    async def check_existing_record(
        self, 
        registration: str, 
        msn: str, 
        month: str
    ) -> Optional[dict]:
        """
        Check if a record already exists with the given registration, MSN, and month
        
        Args:
            registration: Aircraft registration number
           
            
        Returns:
            Existing record if found, None otherwise
        """
        try:
            await self.connect()
            
            existing = await self.db.aircraftutilization.find_first(
                where={
                    'registration': registration,
                    'msn': msn,
                    'month': month
                },
                include={'components': True}
            )
            
            return existing
            
        except Exception as e:
            logger.error(f"❌ Error checking existing record: {e}")
            raise
    
    async def store_aircraft_data(self, data: AircraftUtilization) -> tuple[str, bool]:
        """
        Store aircraft utilization data in the database
        
        Args:
            data: AircraftUtilization object containing all extracted data
            
        Returns:
            tuple[str, bool]: (record_id, is_new_record)
                - record_id: ID of the record (existing or newly created)
                - is_new_record: True if new record was created, False if already existed
        """
        try:
            await self.connect()
            
            # Check if record already exists BEFORE creating
            existing_record = await self.check_existing_record(
                registration=data.registration or '',
                msn=data.msn or '',
                month=data.month or ''
            )
            
            if existing_record:
                logger.warning(
                    f"⚠️  Record already exists in database!\n"
                    f"   Registration: {data.registration}\n"
                
                )
                return existing_record.id, False  
            
            # Proceed with creating new record
            components_to_create = []
            
            component_mapping = {
                'Airframe': data.components.Airframe,
                'Engine1': data.components.Engine1,
                'Engine2': data.components.Engine2,
                'APU': data.components.APU,
                'LandingGearLeft': data.components.LandingGearLeft,
                'LandingGearRight': data.components.LandingGearRight,
                'LandingGearNose': data.components.LandingGearNose,
            }
            
            # Build component data for nested create
            for component_type, component in component_mapping.items():
                if component and self._has_data(component):
                    components_to_create.append({
                        'component_type': component_type,
                        'TSN': component.TSN,
                        'CSN': component.CSN,
                        'MonthlyUtil_Hrs': component.MonthlyUtil_Hrs,
                        'MonthlyUtil_Cyc': component.MonthlyUtil_Cyc,
                        'SerialNumber': component.SerialNumber,
                        'location': component.location,
                    })
            
            # Create aircraft record with all components in a single transaction
            aircraft_record = await self.db.aircraftutilization.create(
                data={
                    'airline': data.airline,
                    'month': data.month,
                    'msn': data.msn,
                    'registration': data.registration,
                    'aircraft_type': data.aircraft_type,
                    'days_flown': data.days_flown,
                    'components': {
                        'create': components_to_create
                    }
                },
                include={
                    'components': True
                }
            )
            
            logger.info(f"✅ Created NEW aircraft record: {aircraft_record.id}")
            logger.info(f"✅ Stored {len(aircraft_record.components)} components")
            
            return aircraft_record.id, True  # Return new ID with True flag
            
        except Exception as e:
            logger.error(f"❌ Error storing aircraft data: {e}")
            raise
    
    def _has_data(self, component: ComponentData) -> bool:
        """Check if component has any non-None data"""
        return any([
            component.TSN is not None,
            component.CSN is not None,
            component.MonthlyUtil_Hrs is not None,
            component.MonthlyUtil_Cyc is not None,
            component.SerialNumber is not None,
            component.location is not None,
        ])
    
    async def get_aircraft_by_id(self, aircraft_id: str):
        """
        Retrieve aircraft data by ID
        
        Args:
            aircraft_id: Aircraft record ID
            
        Returns:
            Aircraft record with all components
        """
        try:
            await self.connect()
            
            aircraft = await self.db.aircraftutilization.find_unique(
                where={'id': aircraft_id},
                include={'components': True}
            )
            
            return aircraft
            
        except Exception as e:
            logger.error(f"❌ Error retrieving aircraft data: {e}")
            raise
    
    async def get_aircraft_by_registration(
        self, 
        registration: str, 
        month: Optional[str] = None
    ):
        """
        Retrieve aircraft data by registration number
        
        Args:
            registration: Aircraft registration number
            month: Optional month filter
            
        Returns:
            Aircraft record with all components
        """
        try:
            await self.connect()
            
            where_clause = {'registration': registration}
            if month:
                where_clause['month'] = month
            
            aircraft = await self.db.aircraftutilization.find_first(
                where=where_clause,
                include={'components': True},
                order={'created_at': 'desc'}
            )
            
            return aircraft
            
        except Exception as e:
            logger.error(f"❌ Error retrieving aircraft data: {e}")
            raise


# Singleton instance
_db_service = None

def get_db_service() -> DatabaseService:
    """Get or create database service instance"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service