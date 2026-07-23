# Extractor de noticias en JSON y español
import json
from src.helpers.ia_client import call_ai

def run_news_extractor():
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
                "company": string,
                "person": string,
                "product": string,
                "top_news": string,
                "keywords": string,
                "datetime": string (formato ISO: YYYY-MM-DD),
                "place": string,
                "price": number or null # Null porque si no hay precio, devolver null NO 0
            }"""
        },{"role": "user", "content": news}
    ], 0.1, "json_object")
    
    extract_entities = json.loads(response_extractor)
    for key, value in extract_entities.items():
        print(f"{key}: {value}")