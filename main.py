import sys
import os


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import setup_environment, openai_client
from routes.chat_router import router as chat_router
from routes.kpis import router as kpis_router

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
app.include_router(chat_router, prefix="/chat")
app.include_router(kpis_router, prefix="/kpis")
