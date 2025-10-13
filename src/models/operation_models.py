from pydantic import BaseModel
from typing import Optional,List

class ComponentData(BaseModel):
    type: str
    serialNumber: str
    lastUtilizationDate: str
    flightHours: str
    flightCycles: str
    apuHours: str
    apuCycles: str
    tsnAtPeriod: str
    csnAtPeriod: str
    tsnAtPeriodEnd: str
    csnAtPeriodEnd: str
    lastTsnCsnUpdate: str
    lastTsnUtilization: str
    lastCsnUtilization: str
    attachmentStatus: str
    engineThrust: str
    status: str
    utilReportStatus: str
    asset_status: str
    derate: str


class AssetData(BaseModel):
    name: str
    serialNumber: str
    registrationNumber: str
    validation_status: str
    report_status: str
    obligation_status: str
    components: list[ComponentData]


class LesseeData(BaseModel):
    lesseeName: str
    assets: List[AssetData]


class SaveOperationsRequest(BaseModel):
    lessees: List[LesseeData]
    month: str
    fileName: str


class SaveOperationsResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    errors: Optional[List[str]] = None