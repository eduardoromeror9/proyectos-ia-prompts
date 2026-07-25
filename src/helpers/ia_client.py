"""Helper para crear y ejecutar el cliente de OpenAI."""

from openai import OpenAI, omit
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def call_ai(messages: list, temperature: float = 0.1, response_format: str = "text") -> str:
    """
    Funcion que ejecuta el cliente.
    Args:
        messages (list): Lista de mensajes para enviar al modelo.
        temperature (float): Nivel de creatividad del modelo.
    Returns:
        str: Respuesta del modelo.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
        response_format={"type": response_format}
    )
    return response.choices[0].message.content

def call_ai_tools(messages: list, temperature: float = 0.1, response_format: str = "text", tools: list = omit, tool_choice: str = omit) -> str:
    """
    Funcion que ejecuta el cliente con herramientas.
    Args:
        messages (list): Lista de mensajes para enviar al modelo.
        temperature (float): Nivel de creatividad del modelo.
        response_format (str): Formato de respuesta.
        tools (list): Lista de herramientas disponibles.
        tool_choice (str): Elección de herramientas.
    Returns:
        str: Respuesta del modelo.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
        response_format={"type": response_format},
        tools=tools,
        tool_choice=tool_choice
    )
    return response.choices[0].message