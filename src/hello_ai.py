""" Librerías para interactuar con la API de OpenAI """
from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            # "content": "Explica que es una API en una oracion."
            "content": "Dime Hola en 3 idiomas diferentes."
        }
    ]
)

print(response.choices[0].message.content)


print("\n--Uso de Tokens--")
print(f"Tokens de entrada: {response.usage.prompt_tokens}")
print(f"Tokens de salida: {response.usage.completion_tokens}")
print(f"Tokens usados: {response.usage.total_tokens}")

cost_input = (response.usage.prompt_tokens / 1_000_000) * 0.15
cost_output = (response.usage.completion_tokens / 1_000_000) * 0.60
total_cost = cost_input + cost_output

print(f"\nCosto Estimado: ${total_cost:.6f} USD")
print(f"\nID de la solicitud: {response.id}")
print(f"Modelo utilizado: {response.model}")