"""
Proyecto: CLI Chatbot
"""
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configuracion
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """Eres un asistente técnico experto en Python e IA.
Eres directo, usas ejemplos de código cuando es relevante,
y respondes en el mismo idioma que el usuario.
Si no sabes algo, lo dices honestamente."""

# Costos de la API en USD
COSTO_INPUT_POR_MILLON = 0.15
COSTO_OUTPUT_POR_MILLON = 0.60

class Chatbot:
    """ Clase para manejar la interacción con la API de OpenAI """
    def __init__(self, system_prompt: str = SYSTEM_PROMPT):
        self.client = OpenAI()
        self.model = MODEL

        self.history: list[dict] = [
            { "role": "system", "content": system_prompt }
        ]
        self.total_tokens = 0
        self.total_cost = 0.0

    def chat(self, user_message: str) -> str:
        """ Envía un mensaje del usuario a la API de OpenAI y devuelve la respuesta. (Mantiene el historial de la conversación) """

        self.history.append({ "role": "user", "content": user_message })

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            max_tokens=1000,
            temperature=0.7,
        )
        response_message = response.choices[0].message.content

        self.history.append({ "role": "assistant", "content": response_message })
        self._update_cost(response.usage)
        return response_message
    
    def _update_cost(self, usage) -> None:
        """ Actualiza el costo total basado en el uso de tokens """
        input_cost = (usage.prompt_tokens / 1_000_000) * COSTO_INPUT_POR_MILLON
        output_cost = (usage.completion_tokens / 1_000_000) * COSTO_OUTPUT_POR_MILLON

        self.total_tokens += usage.total_tokens
        self.total_cost += input_cost + output_cost

    def show_stats(self) -> None:
        """ Muestra estadísticas de uso y costo """
        print(f"\n{'-'*40}")
        print("Sessión finalizada. Estadísticas de uso:")
        print(f"Tokens totales usados: {self.total_tokens}")
        print(f"Costo total estimado: ${self.total_cost:.4f} USD")
        print(f"Turnos: {len(self.history) // 2}")
        print(f"\n{'-'*40}")

def main():
    """Función principal"""
    print("╔══════════════════════════════════════╗")
    print("║      Python IA Aplicada - Chatbot    ║")
    print("║  Escribe 'quit' o Ctrl+C para salir  ║")
    print("╚══════════════════════════════════════╝\n")

    bot = Chatbot()

    try:
        while True:
            try:
                user_input = input("Tú: ").strip()
            except EOFError:
                print("\nSaliendo del chatbot...")
                break
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit", "salir", "q", "bye"]:
                print("Saliendo del chatbot...")
                break
            if user_input.lower() == "/stats":
                bot.show_stats()
                continue
            if user_input.lower() == "/reset":
                bot.history = [bot.history[0]]  # Reinicia el historial manteniendo el prompt del sistema
                print("Historial de conversación reiniciado.\n")
                continue

            print("Bot: ", end="", flush=True)
            try:
                response = bot.chat(user_input)
                print(response)
                print(f"\n--Uso de Tokens-- {bot.total_tokens} tokens, Costo estimado: ${bot.total_cost:.4f} USD\n")
            except Exception as e:
                print(f"\nOcurrió un error al procesar tu solicitud: {e}")
                continue
    
    except KeyboardInterrupt:
        print("\nSaliendo del chatbot...")
    finally:
        bot.show_stats()
        print("Gracias por usar el chatbot. ¡Hasta luego!")


if __name__ == "__main__":
    main()