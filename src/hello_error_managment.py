from openai import OpenAI, AuthenticationError, APIConnectionError, APIError, RateLimitError
from dotenv import load_dotenv
import os

load_dotenv()

def call_ai(question: str) -> str:
    """
    Llama a la API de OpenAI para obtener una respuesta a la pregunta proporcionada.
    Args:
        question (str): La pregunta que se desea enviar a la API.
    Returns:
        str: La respuesta generada por la API.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ],
            max_tokens=500, # Limita la respuesta a 500 tokens
            temperature=0.7, # Controla la creatividad de la respuesta --> #0=Determinista, #1=Creativo #2=Más creativo
        )
        return response.choices[0].message.content

    except AuthenticationError:
        return "Error de autenticación: Verifica tu clave de API."
        raise SystemExit(1)
    except APIConnectionError:
        return "Error de conexión: No se pudo conectar a la API."
        raise
    except RateLimitError:
        return "Error de límite de tasa: Has excedido el número de solicitudes permitidas."
        raise
    except APIError as e:
        return f"Error de la API: {e}"
        raise
    except Exception as e:
        return f"Ocurrió un error inesperado: {e}"
        raise
    
if __name__ == "__main__":
    response = call_ai("Cual es la capital de La Guaira?")
    print(f"Respuesta de la API: {response}")