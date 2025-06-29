from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, operations
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # "http://seu-frontend.com",  # Descomente em produção, se necessário
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(operations.router)
