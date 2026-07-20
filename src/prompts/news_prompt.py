# Extractor de noticias en JSON y español
import json
from src.helpers.ia_client import call_ai

def run_json_mode():
    print("Extractor de noticias")
    print("="*50)

    news = """
    Apple anunció hoy que Tim Cook presentará el nuevo iPhone 17 Pro
    el próximo 15 de septiembre de 2025 en Cupertino, California.
    El dispositivo costará desde $1,199 USD y contará con chip A19.
    """
    
    response_extractor = call_ai([
        {
            "role": "system",
            "content": """Eres un extractor de información de noticias. Si la noticia está en otro idioma traduce al Español.
                Extrae entidades y devuelve SOLO JSON válido con esta estructura:
                {
                    "empresa": string,
                    "persona": string,
                    "producto": string,
                    "noticia_destacada": string,
                    "palabras_clave": string,
                    "fecha": string (formato ISO: YYYY-MM-DD),
                    "lugar": string,
                    "precio_usd": number or null
                }"""
        },
        {"role": "user", "content": news}
    ], 0.1, "json_object")