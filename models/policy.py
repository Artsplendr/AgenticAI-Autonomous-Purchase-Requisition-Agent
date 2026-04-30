from pydantic import BaseModel


class PolicyRule(BaseModel):
    id: str
    text: str


class PolicyCheck(BaseModel):
    compliant: bool
    rules: list[str]
    hard_block: bool = False
    missing_fields: list[str] = []
