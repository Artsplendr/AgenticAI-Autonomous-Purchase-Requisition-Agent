"""PO generator utility returning a structured preview payload."""


def generate_po_preview(state: dict) -> dict:
    quote = state.get('best_quote') or {}
    parsed = state.get('parsed_requisition') or {}
    item = (parsed.get('items') or [{}])[0]
    qty = int(item.get('quantity', 1))
    unit_price = float(quote.get('unit_price_eur', 0.0))
    return {
        'supplier': quote.get('name', 'unknown'),
        'item': item.get('name', 'item'),
        'quantity': qty,
        'unit_price_eur': unit_price,
        'total_eur': round(qty * unit_price, 2),
    }
