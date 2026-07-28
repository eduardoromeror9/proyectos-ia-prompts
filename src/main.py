
from rich.console import Console
from rich.panel import Panel
# from rich.rule import Rule

# from src.prompts.json_mode import run_json_mode
# from src.prompts.news_extractor import run_news_extractor
# from src.prompts.zero_few_shot import run_zero_few_shot
# from src.prompts.cot_prompts import run_chain_of_thought
# from src.prompts.prompt_template import run_prompt_templates
from src.prompts.function_calling import run_chat_with_tools

console = Console()

def main():
    """
    Función principal que ejecuta el programa.
    """
    console.print(Panel.fit("[bold cyan] Tecnicas de de prompts [/bold cyan]\n"))

    # run_zero_few_shot()
    # run_chain_of_thought()
    # run_prompt_templates()
    # run_json_mode()
    # run_news_extractor()
    run_chat_with_tools(input("De que ciudad quieres saber el clima?: "))
    # run_chat_with_tools("¿Cuál es el clima en La Guaira?")
    # run_chat_with_tools("¿Cuál es el clima en Madrid?")
    # run_chat_with_tools("¿Cuál es el clima en London?")
    # run_chat_with_tools("¿Cuál es el clima en Santiago?")
    # run_chat_with_tools("¿Cuál es el clima en Buenos Aires?")


    console.print("\n[bold green] Ejecucion terminada!\n")

if __name__ == "__main__":
    main()