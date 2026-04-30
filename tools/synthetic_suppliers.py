"""Synthetic supplier generation based on request category."""

from __future__ import annotations

from models.supplier import Quote


def generate_synthetic_quotes(item_name: str, quantity: int) -> list[Quote]:
    category = item_name.lower().strip()
    catalog = _catalog_for_category(category)
    if not catalog:
        return []

    qty_discount = min(0.08, max(0.0, (quantity - 1) * 0.0015))
    quotes: list[Quote] = []
    for entry in catalog:
        adjusted_price = round(entry["unit_price_eur"] * (1 - qty_discount), 2)
        quotes.append(
            Quote(
                supplier_id=entry["supplier_id"],
                supplier_name=entry["supplier_name"],
                unit_price_eur=adjusted_price,
                delivery_days=entry["delivery_days"],
                reliability=entry["reliability"],
                categories=[category],
            )
        )
    return quotes


def _catalog_for_category(category: str) -> list[dict]:
    catalogs = {
        "laptop": [
            {
                "supplier_id": "lenovo-eu",
                "supplier_name": "Lenovo EU",
                "unit_price_eur": 880.0,
                "delivery_days": 7,
                "reliability": 0.87,
            },
            {
                "supplier_id": "dell-eu",
                "supplier_name": "Dell EU",
                "unit_price_eur": 920.0,
                "delivery_days": 5,
                "reliability": 0.90,
            },
            {
                "supplier_id": "hp-enterprise-eu",
                "supplier_name": "HP Enterprise EU",
                "unit_price_eur": 950.0,
                "delivery_days": 4,
                "reliability": 0.86,
            },
        ],
        "desk": [
            {
                "supplier_id": "flexispot-eu",
                "supplier_name": "FlexiSpot EU",
                "unit_price_eur": 410.0,
                "delivery_days": 6,
                "reliability": 0.82,
            },
            {
                "supplier_id": "steelcase-eu",
                "supplier_name": "Steelcase EU",
                "unit_price_eur": 465.0,
                "delivery_days": 8,
                "reliability": 0.89,
            },
        ],
        "usb-c cable": [
            {
                "supplier_id": "cablehub-eu",
                "supplier_name": "CableHub EU",
                "unit_price_eur": 7.9,
                "delivery_days": 3,
                "reliability": 0.79,
            },
            {
                "supplier_id": "anker-business",
                "supplier_name": "Anker Business",
                "unit_price_eur": 8.4,
                "delivery_days": 4,
                "reliability": 0.88,
            },
        ],
    }
    return catalogs.get(category, [])
