from pydantic import BaseModel


class Supplier(BaseModel):
    id: str
    name: str
    categories: list[str]
    min_order_qty: int = 1
    unit_price_eur: float
    delivery_days: int
    reliability: float


class Quote(BaseModel):
    supplier_id: str
    supplier_name: str
    unit_price_eur: float
    delivery_days: int
    reliability: float
    categories: list[str] = []
    score: float | None = None
