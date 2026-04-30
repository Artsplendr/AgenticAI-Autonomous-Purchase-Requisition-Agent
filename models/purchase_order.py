from pydantic import BaseModel


class POLineItem(BaseModel):
    item: str
    quantity: int
    unit_price_eur: float


class PurchaseOrder(BaseModel):
    po_number: str
    supplier: str
    status: str
    total_eur: float
    line_items: list[POLineItem]
    justification: str | None = None
    approval_memo: str | None = None
