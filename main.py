import os
import json
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI

from funciones.explicar_ratio_diario import explicar_ratio_diario

# ————— Configuración de logging —————
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)
logger = logging.getLogger("bootdirectoras")

# Carga de la clave
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    logger.error("OPENAI_API_KEY no está configurado en el entorno")
    raise RuntimeError("OPENAI_API_KEY no está configurado.")

client = OpenAI(api_key=API_KEY)

function_schema = [
    {
        "name": "explicar_ratio_diario",
        "description": "...",
        "parameters": {
            "type": "object",
            "properties": {
                "codsalon": {"type": "string"},
                "fecha":    {"type": "string"}
            },
            "required": ["codsalon", "fecha"]
        }
    }
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/kpis/30dias")
async def obtener_kpis_30dias(codsalon: str):
    try:
        df = cargar_hoja("KPIs_30Dias")
        df_salon = df[df["cod_salon"] == codsalon]

        if df_salon.empty:
            raise HTTPException(status_code=404, detail=f"No hay datos para el salón {codsalon}")

        registros = df_salon.to_dict(orient="records")
        return JSONResponse(content={"datos": registros})

    except Exception as e:
        logger.exception("❌ Error al obtener KPIs desde Google Sheets")
        raise HTTPException(status_code=500, detail=f"Error al obtener KPIs: {e}")

@app.post("/chat")
async def chat_handler(request: Request):
    data = await request.json()
    logger.debug(f"➡️  /chat payload recibido: {data!r}")

    mensaje_usuario = data.get("mensaje")
    codsalon        = data.get("codsalon")
    fecha           = data.get("fecha")

    if not mensaje_usuario or not codsalon or not fecha:
        logger.warning("Faltan campos en la petición")
        raise HTTPException(
            400,
            "Faltan campos en la petición. Envíame 'mensaje', 'codsalon' y 'fecha'."
        )

    # Construir prompt forzado
    prompt_user = f"[codsalon={codsalon}]\n[fecha={fecha}]\n{mensaje_usuario}"
    logger.debug(f"📝 prompt_user:\n{prompt_user}")

    system_prompt = (
        "Actúa como Mont Dirección...\n"
        "Si el usuario pregunta por un KPI en día concreto, invoca explicar_ratio_diario..."
    )

    logger.debug("🔄 Llamando a OpenAI.chat.completions.create (primera pasada)")
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": prompt_user}
        ],
        functions=function_schema,
        function_call="auto"
    )
    logger.debug(f"✅ Respuesta OpenAI primera pasada: {res.choices[0].message!r}")

    msg = res.choices[0].message

    if msg.function_call:
        nombre = msg.function_call.name
        args   = json.loads(msg.function_call.arguments)
        logger.info(f"🔧 Modelo invocó función {nombre} con args {args}")

        try:
            resultado_fn = globals()[nombre](**args)
            logger.debug(f"✅ Resultado función {nombre}: {resultado_fn!r}")
        except Exception as e:
            logger.exception("❌ Error al ejecutar la función")
            resultado_fn = f"⚠️ Error interno al ejecutar la función: {e}"

        logger.debug("🔄 Llamando a OpenAI.chat.completions.create (segunda pasada)")
        follow = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system",   "content": system_prompt},
                {"role": "user",     "content": prompt_user},
                {"role": "function", "name": nombre, "content": resultado_fn}
            ]
        )
        respuesta = follow.choices[0].message.content
        logger.debug(f"✅ Respuesta final GPT con función: {respuesta!r}")
        return {"respuesta": respuesta}

    # Fallback: invocar directamente
    logger.warning("⚠️ GPT no invocó la función, uso fallback directo")
    resultado_directo = explicar_ratio_diario(codsalon, fecha)
    respuesta = f"¡Hola! Soy Mont Dirección.\n\n{resultado_directo}"
    logger.debug(f"✅ Respuesta fallback directo: {respuesta!r}")
    return {"respuesta": respuesta}

