from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure aqui as origens permitidas (ajuste conforme o endereço do seu frontend)
origins = [
    "http://localhost:5173",  # Vue com Vite (dev)
    "http://127.0.0.1:5173",
    # "http://seu-frontend.com",  # Descomente em produção, se necessário
]

# Adiciona o middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # ou use ["*"] para todos (não recomendado em prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
