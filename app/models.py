from sqlalchemy import CheckConstraint, Column, DateTime, Integer, Numeric, String, func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)

class Operation(Base):
    __tablename__ = "operations"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)

    # Data de criação (imutável)
    date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Data de alteração (nula na criação, atualizada em cada UPDATE)
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),   # dispara só em UPDATE via ORM
        nullable=True,        # permite NULL no INSERT
    )

    value = Column(Numeric(12, 2), nullable=False)

    # “E” (entrada) ou “S” (saída)
    type = Column(String(1), nullable=False)

    __table_args__ = (
        CheckConstraint("type IN ('E', 'S')", name="ck_operation_type_e_or_s"),
    )