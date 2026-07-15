"""
Roles for prompts.
"""
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


def show_roles():
    """
    Muestra el comportamiento de los roles.
    """
    # Rol user

    print("="*50)
    print("Rol User -- Sin rol system")
    print("="*50)

    response_1 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "¿Cuanto es 2 + 2?"}
        ]
    )
    print(f"Respuesta 1: {response_1.choices[0].message.content}\n")

    # Rol system

    print("="*50)
    print("Rol System")
    print("="*50)

    response_2 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", 
            "content": "Eres un matematico gruñon que responde preguntas simples con desden pero con precisión absoluta, siempre inclyes un comentario sobre lo basico que es la pregunta."},
            {"role": "user", "content": "¿Cuanto es 2 + 2?"}
        ]
    )
    print(f"Respuesta 2: {response_2.choices[0].message.content}\n")

    # Rol assistant

    print("="*50)
    print("Rol Assistant")
    print("="*50)

    response_3 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un clasificador de sentimientos."
             "Respondes con un solo con: positivo, negativo o neutral."},
            {"role": "user", "content": "Me encanta el helado"},
            {"role": "assistant", "content": "positivo"},
            {"role": "user", "content": "MEl clima es templado"},
            {"role": "assistant", "content": "Neutral"},
            {"role": "user", "content": "Odio los lunes"},
            {"role": "assistant", "content": "negativo"},
            {"role": "user", "content": "Odio los martes"},
        ]
    )
    print(f"Sentimientos: {response_3.choices[0].message.content}\n")

if __name__ == "__main__":
    show_roles()