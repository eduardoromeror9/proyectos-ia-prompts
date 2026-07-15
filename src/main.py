
from rich.console import Console
from rich.panel import Panel
# from rich.rule import Rule

from src.prompts.zero_few_shot import run_zero_few_shot
from src.prompts.cot_prompts import run_chain_of_thought

console = Console()

def main():
    """
    Función principal que ejecuta el programa.
    """
    console.print(Panel.fit("[bold cyan] Tecnicas de de prompts [/bold cyan]\n"))

    # run_zero_few_shot()
    run_chain_of_thought()
    console.print("\n[bold green] Ejecucion terminada!\n")

if __name__ == "__main__":
    main()