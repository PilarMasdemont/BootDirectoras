from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import setup_environment, openai_client
from routes import chat, kpis

app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_environment()

# Registrar rutas
app.include_router(chat.router)
app.include_router(kpis.router)