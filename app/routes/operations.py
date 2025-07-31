from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import jwt, os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

from ..database import SessionLocal
from .. import models, schemas

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = creds.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        exp: int | None = payload.get("exp")
        if username is None or exp is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        if datetime.now(timezone.utc).timestamp() > exp:
            raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Não autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user

router = APIRouter(
    prefix="/operations",
    tags=["operations"],
)

# CREATE
@router.post(
    "",
    response_model=schemas.OperationOut,
    status_code=status.HTTP_201_CREATED,
)
def create_operation(
    op_in: schemas.OperationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),  # usuário logado
):
    op = models.Operation(**op_in.dict(), user_id=current_user.id)  # associa usuário
    db.add(op)
    db.commit()
    db.refresh(op)
    return op

# READ (lista só do usuário)
@router.get(
    "",
    response_model=schemas.OperationListResponse
)
def list_operations(
    skip: int = 0,
    limit: int = 100,
    month_year: str = Query(None, alias="month_year"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Operation).filter(models.Operation.user_id == current_user.id)

    if month_year:
        try:
            start_date = datetime.strptime(month_year, "%m/%Y")
            if start_date.month == 12:
                next_month = start_date.replace(year=start_date.year + 1, month=1)
            else:
                next_month = start_date.replace(month=start_date.month + 1)
            end_date = next_month - timedelta(seconds=1)

            query = query.filter(models.Operation.date >= start_date, models.Operation.date <= end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use mm/aaaa.")

    operations = (
        query.order_by(models.Operation.date.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    balance = sum(op.value for op in operations if op.type == "E") - \
            sum(op.value for op in operations if op.type == "S")

    return {
        "balance": float(balance),
        "operations": operations
    }

# UPDATE (só se for do usuário)
@router.put(
    "/{operation_id}",
    response_model=schemas.OperationOut,
)
def update_operation(
    operation_id: int,
    op_in: schemas.OperationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    op = db.query(models.Operation).get(operation_id)
    if not op or op.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Operação não encontrada")

    for field, value in op_in.dict(exclude_unset=True).items():
        setattr(op, field, value)

    db.commit()
    db.refresh(op)
    return op

# DELETE (só se for do usuário)
@router.delete(
    "/{operation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_operation(
    operation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    op = db.query(models.Operation).get(operation_id)
    if not op or op.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Operação não encontrada")

    db.delete(op)
    db.commit()
    return None
