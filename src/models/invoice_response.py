from pydantic import BaseModel
from typing import List, Optional

class Vendor(BaseModel):
    name: str
    address: str
    tax_id: Optional[str] = None
    iban: Optional[str] = None

class Client(BaseModel):
    name: str
    address: str
    tax_id: Optional[str] = None

class Totals(BaseModel):
    new_worth: float
    vat: float
    grand_total: float

class LineItem(BaseModel):
    description: str
    quantity: int
    unit_of_measure: str
    unit_price: float
    net_worth: float
    vat_percent: float
    line_total: float

class InvoiceResponse(BaseModel):
    vendor: Vendor
    client: Client
    invoice_number: str
    invoice_date: str
    totals: Totals
    line_items: List[LineItem]
