# Extractor de noticias en JSON y español
import json
import os
from dotenv import load_dotenv # pyright: ignore[reportMissingImports]
from src.helpers.ia_client import call_ai
from src.services.news_service import NewsService

load_dotenv()

def run_news_extractor():
    print("Extractor de noticias")
    print("="*50)

    # news = """
    # Apple anunció hoy que Tim Cook presentará el nuevo iPhone 17 Pro
    # el próximo 15 de septiembre de 2025 en Cupertino, California.
    # El dispositivo costará desde $1,199 USD y contará con chip A19.
    # """

    news_service = NewsService(os.getenv("NEWS_APIKEY"))
    news = news_service.get_latest_tech_news()

    # if news.startswith("Error al consultar NewsAPI") or news == "No hay noticias disponibles por el momento.":
    #     print(news)
    #     return

    response_extractor = call_ai([
        {
            "role": "system",
            "content": """Eres un extractor de información de noticias. Tu tarea es traducir la noticia al Español y devolver SOLO JSON válido.
            Reglas estrictas:
                1) Traduce completamente el texto de 'top_news' al español.
                2) Traduce 'keywords' al español, manteniendo solo marcas, productos o nombres propios si son esenciales.
                3) 'company', 'person', 'product' y 'place' deben contener nombres propios si existen; no los conviertas a español si son marcas o entidades reconocibles.
                4) 'datetime' debe estar en formato ISO YYYY-MM-DD.
                5) 'price' debe ser un número o null, nunca 0.
                6) Si una propiedad no existe, usa null.
            Estructura exacta:
            {
                "company": string,
                "person": string,
                "product": string,
                "top_news": string,
                "keywords": string,
                "datetime": string (formato ISO: YYYY-MM-DD),
                "place": string,
                "price": number or null
            }"""
        }, {"role": "user", "content": news}
    ], 0.1, "json_object")

    extract_entities = json.loads(response_extractor)
    for key, value in extract_entities.items():
        print(f"{key}: {value}")