import os
from dotenv import load_dotenv
from openai import OpenAI

def setup_environment():
    load_dotenv()
    print("🗂 Directorio actual:", os.getcwd())
    print("📄 Archivos disponibles:", os.listdir())
    print("📁 Contenido funciones/:", os.listdir("./funciones"))

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))