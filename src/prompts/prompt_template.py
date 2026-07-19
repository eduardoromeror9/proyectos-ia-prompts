

from rich.markdown import Markdown

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.rule import Rule
from src.helpers.ia_client import call_ai

console = Console()

def create_code_analysis_prompt(
    code: str,
    language: str,
    detail_level: str = "medium"
    ) -> str:
    """
    Crea un prompt para analizar codigo
    """
    levels = {
        "basic": "Identifica solo bugs criticos",
        "medium": "Identifica bugs criticos, sugiere mejoras de rendimiento y legibilidad",
        "expert": "Analisis completo: bugs, seguridad, rendimiento, patrones de diseño"
    }

    return f"""
    Analiza el siguiente codigo {language}.
    Nivel de analisis requerido: {levels.get(detail_level, levels["medium"])}
    Lengiaje: {language}
    Codigo: {code}
    """
def run_prompt_templates():
    console.print(Rule("[bold yellow] Promp templates [/bold yellow]"))

    # Ejemplo 1: Analisis de codigo
    example_code = """
    def calcular_promedio(numeros):
        total = 0
        for n in numeros:
            total = total+n
        return total / len(numeros)
    """
    syntax = Syntax(example_code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="[bold green]Codigo original[/bold green]", border_style="cyan"))
    console.print("\n")
    
    prompt = create_code_analysis_prompt(
        code=example_code,
        language="Python",
        detail_level="expert"
    )
    response = call_ai([{"role": "user", "content": prompt}])

    # Imprimir respuesta
    console.print(
        Panel(
            Markdown(response),
            title="[bold green]Analisis de codigo[/bold green]",
            border_style="green"
        )
    )
    console.print("\n")