from pydantic import BaseModel


class Item(BaseModel):
    name: str
    quantity: int
    unit: str = 'unit'
    estimated_unit_price_eur: float | None = None


class ParsedRequisition(BaseModel):
    items: list[Item]
    department: str = 'unknown'
    urgency: str = 'normal'
    notes: str | None = None
