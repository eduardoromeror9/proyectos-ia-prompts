from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.rule import Rule

from src.helpers.ia_client import call_ai

console = Console()

def run_chain_of_thought():
    console.print(Rule("[bold yellow] Chain of Thought"))

    problem = """
    Una empresa tiene 3 servidores. Cada servidor maneja 1.200 request/hora.
    Tiene picos de 4.500 request/hora los lunes.
    Cuantos servidores adicionales necesitan para los picos?
"""

    console.print(Panel(problem.strip(), title="Problema", border_style="blue"))

    whithout_cot = call_ai([{"role": "user", "content": f"Responde solo con un numero: {problem}"}])

    whit_cot = call_ai([{"role": "user", "content": f"""
    {problem}
    Piensa paso a paso:
    1. Calcula la capacidad actual.
    2. Calcula el deficit del pico.
    3. Determina cuantos servidores adicionales se necesitan.
    4. Da la resuesta final.
    """}])

    console.print(Panel(f"[bold] Sin CoT [/bold] {whithout_cot}", border_style="red"))
    console.print(Panel(Markdown(whit_cot),title="Con Chain of Thought", border_style="green"))