from pydantic import BaseModel, Field

class OrderBase(BaseModel):
    product: str = Field(max_length=255, strip_whitespace=True)
    quantity: int

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    user_id: int
    status: str

    class Config:
        from_attributes = True