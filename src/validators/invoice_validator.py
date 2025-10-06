from src.models.invoice_response import InvoiceResponse
def validate_invoice(data: InvoiceResponse) -> bool:
    vendor_name = getattr(data.vendor, "name", None) if not isinstance(data.vendor, dict) else data.vendor.get("name")
    client_name = getattr(data.client, "name", None) if not isinstance(data.client, dict) else data.client.get("name")
    grand_total = getattr(data.totals, "grand_total", None) if not isinstance(data.totals, dict) else data.totals.get("grand_total")
    
    if not vendor_name:
        print("Validation warning missing vendor name")
        return False
    if not client_name:
        print("Validation warning missing client name")
        return False
    if not data.invoice_number:
        print("Validation missing invoice number")
        return False
    if grand_total is None or grand_total <= 0:
        print("Validation missing or invalid grand total")
        return False
    if not data.line_items:
        print("Validation warning no line item found")
        return False
    
    return True
