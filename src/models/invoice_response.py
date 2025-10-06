from dataclasses import dataclass
from typing import List,Optional


@dataclass
class Vendor:
    name:str
    address:str
    tax_id:Optional[str]=None
    iban:Optional[str]=None

@dataclass
class Client:
    name:str
    address:str
    tax_id:Optional[str]=None

@dataclass
class Totals:
    new_worth:float
    vat:float
    grand_total:float

@dataclass
class LineItem:
    description:str
    quantity:int
    unit_of_measure:str
    unit_price:float
    net_worth:float
    vat_percent:float
    line_total:float

@dataclass
class InvoiceResponse:
    vendor:Vendor
    client:Client
    invoice_number:str
    invoice_date:str
    totals:Totals
    line_items:list[LineItem]