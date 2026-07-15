from rich.console import Console
from rich.table import Table
from rich.rule import Rule

from src.helpers.ia_client import call_ai

console = Console()

def run_zero_few_shot():
    """
    Función que ejecuta el prompt de Zero/Few Shot.
    """
    console.print(Rule("[bold yellow] Tecnica Zero-Shot y Few-Shot [/bold yellow]"))
    zero_shot = call_ai([
        {"role": "user", "content": "Clasifica este email como URGENTE o NORMAL. " 
        "'El servidor de producción está caído, los clientes no pueden acceder'"},
    ])

    few_shot = call_ai(
        [
            {"role": "system", "content": "Clasifica emails. Responde solo con: URGENTE o NORMAL, Sin explicacion"},
            {"role": "user", "content": "Tengo una reunion manana a las 15:00"},
            {"role": "assistant", "content": "NORMAL"},
            {"role": "user", "content": "La base de datos se corrompio en produccion"},
            {"role": "assistant", "content": "URGENTE"},
            {"role": "user", "content": "Puedes revisar mi PR en lo que puedas?"},
            {"role": "assistant", "content": "NORMAL"},
            {"role": "user", "content": "El servidor de produccion esta caido, los clientes no pueden acceder"},
        ]
    )


    table = Table(title="COMPARACION DE RESPUESTAS")
    table.add_column("Tecnica", justify="center", style="cyan", no_wrap=True)
    table.add_column("Resultado", justify="center", style="magenta")

    table.add_row("Zero Shot", zero_shot)
    table.add_row("Few Shot", few_shot)
    console.print(table)