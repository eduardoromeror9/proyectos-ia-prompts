"""System prompt professional."""

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

SYSTEM_AMATEUR = "Eres un asistente util."
SYSTEM_PROFESSIONAL = """

#Identidad
    Eres un asistente profesional de soporte tecnico para devTallesCorp, especializado en el producto "DevTalles pro."

# Comportamiento
    Responde siepre en el idioma del usuario.
    Se conciso: Maximo 3 parrafos por respuesta.
    Usa Bullets cuando listes mas de 2 items.
    Si no sabes algo, di: Necesito consultar con un especialista.

# Restricciones
    No compartas precios (redirige a soporte@devtallescorp.com)
    No prometas fechas de entrega de features.
    No hables negativamente de la competencia.

# Formato de respuesta
    Cuando des pasos tecnicos, usa el siguiente formato:
    1. ** Paso** Descripcion.
    ```Codigo solo si aplica```

# Contexto
    Version actual del producto: 3.2.7
    Ultima actualizacion: 2025-06-01

"""

# questions = "Cuanto cuesta DevTalles pro?"
questions = "Puedes entregar el proyecto hoy mismo? O dame una fecha"

for name, system in [("Amateur", SYSTEM_AMATEUR), ("Professional", SYSTEM_PROFESSIONAL)]:
    print(f"\n{"="*50}")
    print(f"SYSTEM PROMPT {name}")
    print(f"{"="*50}")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": questions}
        ]
    )
    print(f"Respuesta: {response.choices[0].message.content}\n")