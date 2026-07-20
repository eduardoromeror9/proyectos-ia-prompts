"""
JSON Mode
"""

import json
from src.helpers.ia_client import call_ai

def run_json_mode():
    # print("Texto libre")
    # print("="*40)

    # response_text = call_ai([{"role": "user", "content": "Dame la informacion sobre Python: año de creacion, creador, usos principales."}])

    # print(f"\nRespuesta del modelo: {response_text}")

    print(f"\nJson mode:\n")
    print("="*40)

    response_json = call_ai([
        {
            "role": "system",
            "content": " Devuelvelo SIEMPRE en formato JSON valido"
        },
        {
            "role": "user",
            "content": """ Dame la informacion sobre Python en este formato exacto:
            {
                "Lenguaje": "nombre",
                "Año de creacion": "numero",
                "Creador": "nombre",
                "Usos principales": ["uso1", "uso2", "uso3"]
            }
            """
        }
    ], 0.1, "json_object")
    json_data = json.loads(response_json)
    print("JSON: ", json_data)
    print(f"Año de creacion: {json_data['Año de creacion']}")
    print(f"Creador: {json_data['Creador']}")
