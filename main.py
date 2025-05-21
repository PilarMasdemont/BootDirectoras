import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI
from funciones.explicar_ratio_diario import explicar_ratio_diario
from sheets import cargar_hoja
from typing import Optional

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY no está configurado.")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# —————————————————————————————————————————————————————————————————————————————————————————
# Endpoint de depuración: devuelve TODO el contenido de la hoja KPIs_30Dias (o filtrado por salón)
# —————————————————————————————————————————————————————————————————————————————————————————
@app.get("/kpis/30dias")
async def kpis_30dias(codsalon: Optional[str] = None):
    """
    Devuelve los registros de la pestaña KPIs_30Dias.
    Si se pasa codsalon, filtra solo ese salón.
    """
    # cargar_hoja internally hace pd.read_csv desde tu Google Sheets export URL
    df = cargar_hoja("KPIs_30Dias")
    # Asegúrate de que codsalon sea string en el DataFrame
    df["codsalon"] = df["codsalon"].astype(str)

    if codsalon:
        df = df[df["codsalon"] == str(codsalon)]

    # Serializamos a JSON
    return df.to_dict(orient="records")


# —————————————————————————————————————————————————————————————————————————————————————————
# Chat handler (igual que antes, pero ya lee fecha del body y fuerza inyección de tags)
# —————————————————————————————————————————————————————————————————————————————————————————
client = OpenAI(api_key=API_KEY)
function_schema = [
    {
        "name": "explicar_ratio_diario",
        "description": "Explica por qué el Ratio General fue alto, medio o bajo en un día concreto...",
        "parameters": {
            "type": "object",
            "properties": {
                "codsalon": {"type": "string"},
                "fecha":    {"type": "string", "description": "YYYY-MM-DD"}
            },
            "required": ["codsalon", "fecha"]
        }
    }
]

@app.post("/chat")
async def chat_handler(request: Request):
    data = await request.json()
    mensaje_usuario = data.get("mensaje")
    codsalon        = data.get("codsalon")
    fecha           = data.get("fecha")

    if not mensaje_usuario or not codsalon or not fecha:
        raise HTTPException(400, "Debes enviar 'mensaje', 'codsalon' y 'fecha' en el body.")

    system_prompt = (
        "Actúa como Mont Dirección. "
        "Contesta siempre con un saludo, y presentándote: Soy Mont Dirección.\n\n"
        "Cuando la directora pregunte por un KPI de un día concreto, debes invocar "
        "la función explicar_ratio_diario con los parámetros codsalon y fecha en formato YYYY-MM-DD, "
        "esperar su respuesta, y luego generar tú el texto explicativo en español claro y directo."
    )

    # Inyectamos tags para ayudar al modelo
    injected = f"[codsalon={codsalon}]\n[fecha={fecha}]\n{mensaje_usuario}"

    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": injected}
        ],
        functions=function_schema,
        function_call="auto"
    )

    msg = res.choices[0].message
    # Si no lo llama GPT, lo hacemos nosotros
    if not msg.function_call or msg.function_call.name != "explicar_ratio_diario":
        resultado = explicar_ratio_diario(codsalon, fecha)
        return {"respuesta": f"¡Hola! Soy Mont Dirección.\n\n{resultado}"}

    # Si GPT genera correctamente la llamada:
    args = json.loads(msg.function_call.arguments)
    resultado = explicar_ratio_diario(**args)
    follow = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": injected},
            {"role": "function", "name": "explicar_ratio_diario", "content": resultado}
        ]
    )
    return {"respuesta": follow.choices[0].message.content}
