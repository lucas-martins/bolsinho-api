from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    
    # Relacionamento com operações (opcional)
    operations = relationship("Operation", back_populates="user")


class Operation(Base):
    __tablename__ = "operations"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)

    date = Column(
        DateTime(timezone=True),
        nullable=False,  # Remove server_default para que o usuário informe a data
    )

    value = Column(Numeric(12, 2), nullable=False)
    type = Column(String(1), nullable=False)

    # Foreign key para usuário
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relacionamento para acessar o usuário da operação
    user = relationship("User", back_populates="operations")

    __table_args__ = (
        CheckConstraint("type IN ('E', 'S')", name="ck_operation_type_e_or_s"),
    )
