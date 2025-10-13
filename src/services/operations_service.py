from typing import List, Dict, Any
from prisma import Prisma
from prisma.models import Lessee, Asset, Component
from src.models.operation_models import (
    ComponentData,
    SaveOperationsRequest,
    SaveOperationsResponse,
    AssetData,
    LesseeData
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OperationsService:
    """
    Service for handling operations data business logic
    """
    
    def __init__(self):
        self.db = Prisma(auto_register=True)
        self._connected = False
    
    async def connect(self):
        """Connect to database"""
        if not self._connected:
            await self.db.connect()
            self._connected = True
            logger.info("✅ Database connected")
    
    async def disconnect(self):
        """Disconnect from database"""
        if self._connected:
            await self.db.disconnect()
            self._connected = False
            logger.info("👋 Database disconnected")
    
    async def check_month_exists(self, month: str) -> bool:
        """
        Check if data already exists for the given month
        """
        try:
            # Ensure connection
            if not self._connected:
                await self.connect()
            
            result = await self.db.lessee.find_first(
                where={"month": month}
            )
            return result is not None
        except Exception as e:
            logger.error(f"Error checking month existence: {e}")
            raise
    
    async def save_operations_data(
        self,
        lessees: List[LesseeData],
        month: str,
        file_name: str
    ) -> Dict[str, Any]:
        """
        Save operations data to database
        """
        saved_lessees = 0
        saved_assets = 0
        saved_components = 0
        errors = []
        
        try:
            # Ensure connection
            if not self._connected:
                await self.connect()
            
            for lessee_data in lessees:
                try:
                    logger.info(f"💾 Saving lessee: {lessee_data.lesseeName}")
                    
                    # Create Lessee
                    lessee = await self.db.lessee.create(
                        data={
                            "name": lessee_data.lesseeName,
                            "month": month,
                            "fileName": file_name,
                        }
                    )
                    saved_lessees += 1
                    logger.info(f"✅ Created lessee: {lessee_data.lesseeName} (ID: {lessee.id})")
                    
                    # Create Assets
                    for asset_data in lessee_data.assets:
                        try:
                            asset = await self.db.asset.create(
                                data={
                                    "name": asset_data.name,
                                    "serialNumber": asset_data.serialNumber,
                                    "registrationNumber": asset_data.registrationNumber,
                                    "validation_status": asset_data.validation_status,
                                    "report_status": asset_data.report_status,
                                    "obligation_status": asset_data.obligation_status,
                                    "month": month,
                                    "lesseeId": lessee.id
                                }
                            )
                            saved_assets += 1
                            logger.info(f"✅ Created asset: {asset_data.serialNumber}")
                            
                            # Create Components
                            for component_data in asset_data.components:
                                try:
                                    component = await self.db.component.create(
                                        data={
                                            "type": component_data.type,
                                            "serialNumber": component_data.serialNumber,
                                            "lastUtilizationDate": component_data.lastUtilizationDate,
                                            "flightHours": component_data.flightHours,
                                            "flightCycles": component_data.flightCycles,
                                            "apuHours": component_data.apuHours,
                                            "apuCycles": component_data.apuCycles,
                                            "tsnAtPeriod": component_data.tsnAtPeriod,
                                            "csnAtPeriod": component_data.csnAtPeriod,
                                            "tsnAtPeriodEnd": component_data.tsnAtPeriodEnd,
                                            "csnAtPeriodEnd": component_data.csnAtPeriodEnd,
                                            "lastTsnCsnUpdate": component_data.lastTsnCsnUpdate,
                                            "lastTsnUtilization": component_data.lastTsnUtilization,
                                            "lastCsnUtilization": component_data.lastCsnUtilization,
                                            "attachmentStatus": component_data.attachmentStatus,
                                            "engineThrust": component_data.engineThrust,
                                            "status": component_data.status,
                                            "utilReportStatus": component_data.utilReportStatus,
                                            "asset_status": component_data.asset_status,
                                            "derate": component_data.derate,
                                            "month": month,
                                            "assetId": asset.id
                                        }
                                    )
                                    saved_components += 1
                                    
                                except Exception as e:
                                    error_msg = f"Error saving component {component_data.serialNumber}: {str(e)}"
                                    logger.error(error_msg)
                                    errors.append(error_msg)
                            
                        except Exception as e:
                            error_msg = f"Error saving asset {asset_data.serialNumber}: {str(e)}"
                            logger.error(error_msg)
                            errors.append(error_msg)
                    
                except Exception as e:
                    error_msg = f"Error saving lessee {lessee_data.lesseeName}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
        except Exception as e:
            error_msg = f"Database error: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
        
        return {
            "saved_lessees": saved_lessees,
            "saved_assets": saved_assets,
            "saved_components": saved_components,
            "errors": errors
        }
    
    async def get_operations_by_month(self, month: str) -> List[Dict[str, Any]]:
        """
        Retrieve operations data for a specific month
        """
        try:
            # Ensure connection
            if not self._connected:
                await self.connect()
            
            lessees = await self.db.lessee.find_many(
                where={"month": month},
                include={
                    "assets": {
                        "include": {
                            "components": True
                        }
                    }
                }
            )
            
            return [self._format_lessee(lessee) for lessee in lessees]
        
        except Exception as e:
            logger.error(f"Error fetching operations by month: {e}")
            raise
    
    async def get_all_operations(self) -> List[Dict[str, Any]]:
        """
        Retrieve all operations data
        """
        try:
            # Ensure connection
            if not self._connected:
                await self.connect()
            
            lessees = await self.db.lessee.find_many(
                include={
                    "assets": {
                        "include": {
                            "components": True
                        }
                    }
                }
            )
            
            return [self._format_lessee(lessee) for lessee in lessees]
        
        except Exception as e:
            logger.error(f"Error fetching all operations: {e}")
            raise
    
    async def delete_operations_by_month(self, month: str) -> bool:
        """
        Delete operations data for a specific month
        """
        try:
            # Ensure connection
            if not self._connected:
                await self.connect()
            
            result = await self.db.lessee.delete_many(
                where={"month": month}
            )
            return result > 0
        
        except Exception as e:
            logger.error(f"Error deleting operations by month: {e}")
            raise
    
    def _format_lessee(self, lessee) -> Dict[str, Any]:
        """
        Format lessee data for response
        """
        return {
            "id": lessee.id,
            "name": lessee.name,
            "month": lessee.month,
            "file_name": lessee.fileName,
            "created_at": lessee.createdAt.isoformat() if lessee.createdAt else None,
            "updated_at": lessee.updatedAt.isoformat() if lessee.updatedAt else None,
            "assets": [self._format_asset(asset) for asset in (lessee.assets or [])]
        }
    
    def _format_asset(self, asset) -> Dict[str, Any]:
        """
        Format asset data for response
        """
        return {
            "id": asset.id,
            "name": asset.name,
            "serial_number": asset.serialNumber,
            "registration_number": asset.registrationNumber,
            "validation_status": asset.validation_status,
            "report_status": asset.report_status,
            "obligation_status": asset.obligation_status,
            "month": asset.month,
            "created_at": asset.createdAt.isoformat() if asset.createdAt else None,
            "components": [self._format_component(comp) for comp in (asset.components or [])]
        }
    
    def _format_component(self, component) -> Dict[str, Any]:
        """
        Format component data for response
        """
        return {
            "id": component.id,
            "type": component.type,
            "serial_number": component.serialNumber,
            "last_utilization_date": component.lastUtilizationDate,
            "flight_hours": component.flightHours,
            "flight_cycles": component.flightCycles,
            "apu_hours": component.apuHours,
            "apu_cycles": component.apuCycles,
            "tsn_at_period": component.tsnAtPeriod,
            "csn_at_period": component.csnAtPeriod,
            "tsn_at_period_end": component.tsnAtPeriodEnd,
            "csn_at_period_end": component.csnAtPeriodEnd,
            "util_report_status": component.utilReportStatus,
            "attachment_status": component.attachmentStatus,
            "status": component.status,
            "asset_status": component.asset_status,
            "derate": component.derate,
            "month": component.month,
            "created_at": component.createdAt.isoformat() if component.createdAt else None
        }


# Singleton instance
_operations_service = None

def get_operations_service() -> OperationsService:
    """Get or create operations service instance"""
    global _operations_service
    if _operations_service is None:
        _operations_service = OperationsService()
    return _operations_service