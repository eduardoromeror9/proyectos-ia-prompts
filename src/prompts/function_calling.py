import json
from src.helpers.ia_client import call_ai_tools
from src.services.weather_service import WeatherService

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Obtener clima actual de una ciudad. Usar cuando el usuario pregunte por el tiempo o clima",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Nombre de la ciudad, ej: 'La Guaira' o 'Madrid' "
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Unidad de temperatura (celsius o fahrenheit)"
                    }
                },
                "required": ["city"] # Este campo es obligatorio, el user debe mencionar la ciudad para obtener el clima.
            }
        }
    }
]

def get_weather(city: str, unit: str = "celsius") -> dict:
    """Obtener clima"""

    # simulated_data = {
    #     "Madrid": {"temperature": 18, "wind_speed": 10.2},
    #     "Mexico City": {"temperature": 22, "wind_speed": 1.0},
    #     "La Guaira": {"temperature": 12, "wind_speed": 2.0},
    # }

    # city_lower = city.lower()
    # weather_data = simulated_data.get(
    #     city_lower,
    #     {"temperature": 20, "wind_speed": 1.0}
    # )
    weather_service = WeatherService()
    weather = weather_service.get_current_weather_by_city(city)
    # print(weather["temperature"])


    temp = weather["temperature"]
    if unit == "fahrenheit":
        temp = (temp * 9/5) + 32
    return {
        "city": city,
        "temperature": f"{temp}°{"C" if unit == "celsius" else "F"}",
        "windspeed": f"{weather.get('windspeed', 0)} km/h"
    }

def execute_tool(name: str, arguments: dict) -> str:
    """Mapea el nombre de la funcion real"""

    available_functions = {
        "get_weather": get_weather,
    }
    if name not in available_functions:
        return json.dumps({"error": f"Función '{name}' no encontrada."})

    result = available_functions[name](**arguments)
    return json.dumps(result, ensure_ascii=False)

def run_chat_with_tools(user_message: str) -> str:
    messages = [
        {"role": "system", "content": "Eres un asistente util con acceso a herramientas."},
        {"role": "user", "content": user_message}        
    ]
    print(f"\nUsuario: {user_message}")

    message_ia = call_ai_tools(messages, 0.1, "text", TOOLS, "auto")

    if message_ia.tool_calls:
        print(f"\nIA Decide usar herramientas")
        messages.append(message_ia)

        for tool_call in message_ia.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print(f"\nIA llama a la herramienta: {function_name} con argumentos: {arguments}")

            result = execute_tool(function_name, arguments)

            print(f"\nResultado de la herramienta: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

        final_response = call_ai_tools(messages, 0.1, "text", TOOLS)
    else:
        final_response = message_ia
    print(f"\nIA Responde: {final_response.content}")
    return final_response.content