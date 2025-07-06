from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt, os
from datetime import datetime, timezone
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
    # remove dependencies global para usar por endpoint
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
    response_model=list[schemas.OperationOut],
)
def list_operations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Operation)
        .filter(models.Operation.user_id == current_user.id)  # filtra só as operações do usuário
        .offset(skip)
        .limit(limit)
        .all()
    )

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
