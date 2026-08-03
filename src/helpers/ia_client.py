"""Helper para crear y ejecutar el cliente de OpenAI."""

from openai import OpenAI, omit, RateLimitError, APIConnectionError, APIStatusError, APITimeoutError
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()
client = OpenAI()

# Excepciones transitorias que merecen reintento (429, 5xx, timeouts, red).
RETRYABLE_ERRORS = (RateLimitError, APIStatusError, APIConnectionError, APITimeoutError)

def _retry_policy():
    """Política de reintento: hasta 5 intentos con backoff exponencial (2s -> 60s)."""
    return retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type(RETRYABLE_ERRORS),
        reraise=True,
    )


@_retry_policy()
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

@_retry_policy()
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