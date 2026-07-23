from datetime import datetime, timedelta, timezone
import requests # pyright: ignore[reportMissingModuleSource]


class NewsService:
    """News Service class para hacer fetch con la api de newsapi.org"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/top-headlines"

    def get_latest_tech_news(self) -> str:
        """Trae las ultimas noticias de tecnologia"""
        from_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")

        params = {
            "category": "technology",
            # "q": "apple",
            "from": from_date,
            "sortBy": "popularity",
            "apiKey": self.api_key,
        }
        response = requests.get(self.base_url, params=params)
        data = response.json()

        if response.status_code != 200:
            error_message = data.get("message", "No hay noticias disponibles por el momento.")
            return f"Error al consultar NewsAPI: {error_message}"

        if not data.get("articles"):
            return "No hay noticias disponibles por el momento."

        article = data["articles"][0]

        return f"""
        {article.get('title', '')}.
        {article.get('description', '')}.
        {article.get('content', '')}.
        """