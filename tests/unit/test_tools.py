from tools.po_generator import generate_po_preview


def test_po_preview_total_calculation():
    preview = generate_po_preview({
        'parsed_requisition': {'items': [{'name': 'laptop', 'quantity': 2}]},
        'best_quote': {'name': 'Dell EU', 'unit_price_eur': 900},
    })
    assert preview['total_eur'] == 1800
