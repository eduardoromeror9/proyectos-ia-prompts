from http import client
import os
import math
# pyrefly: ignore [missing-import]
from openai import OpenAI
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()
# noinspection redeclaration
client = OpenAI()


# noinspection unresolved-references
def get_embedding(text: str) -> list[float]:
    """Convierte texto a vector de 1536 dimensiones"""
    response = client.embeddings.create(
        model= "text-embedding-3-small",
        input= text,
    )
    return response.data[0].embedding

def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    """
    Calcula la similitud del coseno entre dos vectores.
    
    """
    dot_product = sum(a * b for a,b in zip(vector_a, vector_b))
    magnitude_a = math.sqrt(sum(a ** 2 for a in vector_a))
    magnitude_b = math.sqrt(sum(b ** 2 for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0  
    
    return dot_product / (magnitude_a * magnitude_b)




if __name__ == "__main__":
    print("="*40)
    print("         Búsqueda por vector")
    print("="*40)

    embeddin_vector = get_embedding("Elefante")
    embeddin_vector_b = get_embedding("Pelota")

    similarity = cosine_similarity(embeddin_vector, embeddin_vector_b)
    print(f"Similitud: {similarity:} ")