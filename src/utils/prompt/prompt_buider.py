def build_invoice_prompt() -> str:
    """Build the prompt for invoice extraction"""
    return """
Extract the following fields from this invoice and return as VALID JSON ONLY (no markdown, no code blocks):

**Required Fields:**

1. **Vendor Details:**
   - name (company name)
   - address (full address)
   - tax_id (tax identification number)
   - iban (bank account number, use empty string if not available)

2. **Client Details:**
   - name (company name)
   - address (full address)
   - tax_id (tax identification number, use empty string if not available)

3. **Invoice Metadata:**
   - invoice_number (invoice ID/number)
   - invoice_date (format: YYYY-MM-DD)

4. **Totals:**
   - net_worth (subtotal before tax, as number)
   - vat (total VAT/tax amount, as number)
   - grand_total (final total including tax, as number)

5. **Line Items:** (array of products/services)
   - description (item description)
   - quantity (number of units)
   - unit_of_measure (e.g., "each", "box", "kg", "hour")
   - unit_price (price per unit, as number)
   - net_worth (subtotal for this line, as number)
   - vat_percent (VAT percentage as number, e.g., 10)
   - line_total (total including VAT for this line, as number)

**CRITICAL RULES:**
- Return ONLY the JSON object, no explanations
- Do NOT wrap in markdown code blocks
- All monetary values MUST be numbers, not strings
- Use null for missing optional fields
- Date format must be YYYY-MM-DD

**Expected JSON Structure:**
{
  "vendor": {
    "name": "",
    "address": "",
    "tax_id": "",
    "iban": ""
  },
  "client": {
    "name": "",
    "address": "",
    "tax_id": ""
  },
  "invoice_number": "",
  "invoice_date": "",
  "totals": {
    "net_worth": 0,
    "vat": 0,
    "grand_total": 0
  },
  "line_items": [
    {
      "description": "",
      "quantity": 0,
      "unit_of_measure": "",
      "unit_price": 0,
      "net_worth": 0,
      "vat_percent": 0,
      "line_total": 0
    }
  ]
}
"""