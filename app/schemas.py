from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator

class UserCreate(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class OperationBase(BaseModel):
    description: str = Field(..., example="Pagamento serviço X")
    value: float = Field(..., gt=0, example=150.75)
    type: str = Field(..., min_length=1, max_length=1, example="E")

    # garante só "E" ou "S"
    @validator("type")
    def type_must_be_e_or_s(cls, v):
        if v not in ("E", "S"):
            raise ValueError("type deve ser 'E' (entrada) ou 'S' (saída)")
        return v

class OperationCreate(OperationBase):
    """Usado no POST (criação)."""
    pass


class OperationUpdate(BaseModel):
    """Todos opcionais para PUT/PATCH."""
    description: Optional[str]
    value: Optional[float]
    type: Optional[str]

    @validator("type")
    def type_must_be_e_or_s(cls, v):
        if v and v not in ("E", "S"):
            raise ValueError("type deve ser 'E' ou 'S'")
        return v


class OperationOut(OperationBase):
    id: int
    date: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True