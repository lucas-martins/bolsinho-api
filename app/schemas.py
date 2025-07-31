from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date, datetime
from typing import Optional, List


# Usuário
class UserCreate(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


# Operação
class OperationBase(BaseModel):
    description: str = Field(..., example="Pagamento serviço X")
    value: float = Field(..., gt=0, example=150.75)
    type: str = Field(..., min_length=1, max_length=1, example="E")

    @validator("type")
    def type_must_be_e_or_s(cls, v):
        if v not in ("E", "S"):
            raise ValueError("type deve ser 'E' (entrada) ou 'S' (saída)")
        return v


class OperationCreate(OperationBase):
    # Agora o usuário DEVE informar a data
    date: date   # ou date, se quiser só Y‑M‑D

    # se você quiser garantir que a data não seja futura, por ex.:
    # @validator("date")
    # def no_future(cls, v):
    #     if v > datetime.utcnow():
    #         raise ValueError("Data não pode estar no futuro")
    #     return v


class OperationUpdate(BaseModel):
    description: Optional[str]
    value: Optional[float]
    type: Optional[str]
    date: Optional[date]  # permitir editar a data

    @validator("type")
    def type_must_be_e_or_s(cls, v):
        if v and v not in ("E", "S"):
            raise ValueError("type deve ser 'E' ou 'S'")
        return v


class OperationOut(OperationBase):
    id: int
    date: datetime            # data informada
    user_id: int              # dono da operação

    class Config:
        orm_mode = True

class OperationListResponse(BaseModel):
    balance: float
    operations: List[OperationOut]

    class Config:
        orm_mode = True
