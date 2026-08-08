""" 
Chat con PDFs -- Inicio el proyecto RAG con pdfs para practicar y mejorar habilidades 
"""
import sys
from src.rag.pipeline_rag import RagPipeline
from pathlib import Path
from pypgf import PdfReader
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel


load_dotenv()
console = Console()


class PDFProcessor:
    """
    Lee PDF y devuelve el texto extraido.
    """

    @staticmethod
    def extract_text(pdf_path: str) -> str:
        try:
            reader = PdfReader(str(pdf_path))
            pages_text = []

            for page_number, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()

                if page_text and page_text.strip():
                    pages_text.append(f"[Pagina: {page_number}]\n{page_text}")

            return "\n\n".join(pages_text)

        except Exception as e:
            console.print(f"[ERROR] Error al extraer texto del PDF {pdf_path.name}: {e}")
            return ""

    @staticmethod
    def get_pdfs(folder: Path) -> list[Path]:
        """
        Obtiene todos los archivos PDF en el directorio actual.
        """

        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)

        pdf_files = list(folder.glob("*.pdf"))
        return pdf_files


class IndexRegistry:

    def __init__(self, registry_path: Path):
        self.path = registry_path
        self.registry = dict[str, int] = {}
        self._load()

    def _load(self):
        """
        De archivo a memoria, cargamos el registro de índices de PDFs ya procesados.
        """
        if not self.path.exists():
            return

        with open(self.path, "r", encoding="utf-8") as file:
            for line in file.read().splitlines():
                if not line.strip():
                    continue

                parts = line.rsplit(":", 1) # manualmente separamos el nombre del archivo y el índice --> (manual.pdf:204700)
                if len(parts) == 2:
                    name, size = parts
                    self.registry[name] = int(size)

    def save(self) -> None:
        """
        De Memoria a archivo, guardamos el registro de índices de PDFs procesados.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as file:
            for name, size in self.registry.items():
                file.write(f"{name}:{size}\n") # (manual.pdf:204700)

    def is_indexed(self, pdf_path: Path) -> bool:
        """
        Verifica si el PDF ya ha sido indexado.
        """
        if pdf_path.name not in self.registry:
            return False

        current_size = pdf_path.stat().st_size        
        return self.registry[pdf_path.name] == current_size

    def mark_indexed(self, pdf_path: Path) -> None:
        """
        Marca el PDF como indexado.
        """
        self.registry[pdf_path.name] = pdf_path.stat().st_size

    @property
    def indexed_name(self) -> list[str]:
        """
        Devuelve una lista de nombres de archivos PDF que han sido indexados.
        """
        return sorted(self.registry.keys())

    @property
    def count(self) -> int:
        """
        Devuelve el número de PDFs indexados.
        """
        return len(self.registry)


class ChatWithPDFs:
    """
    Clase principal para manejar la interacción con PDFs y el pipeline RAG.
    """

    def __init__(self, pdf_folder: str = "data/files/pdfs"):
        self.pdf_folder = Path(pdf_folder)
        self.processor = PDFProcessor()
        self.registry = IndexRegistry(Path("data/pdfs_indexados.txt"))
        self.rag = RagPipeline(
            collection_name="mis_pdfs",
            db_path="./data/chromadb_pdfs"
        )

    def index_news_pdfs(self) -> int:
        """
        Indexa los PDFs en la carpeta especificada y devuelve el número de PDFs indexados.
        """
        pdfs = self.processor.get_pdfs(self.pdf_folder)
        if not pdfs:
            console.print(
                f"\n[INFO] No se encontraron archivos PDF para indexar en {self.pdf_folder}.\n"
                f"[DIM]Por favor, coloca tus archivos PDF en la carpeta y vuelve a ejecutar el script (reindexar).\n" # [dim]
            )
            return 0

        news_pdfs = [pdf for pdf in pdfs if not self.registry.is_indexed(pdf)]

        if not news_pdfs:
            console.print(
                f"\n[INFO] Todos los PDFs han sido indexados.\n"
                f"({len(pdfs)} archivos)"
            )
            return 0

        console.print(f"\n[INFO] Indexando {len(news_pdfs)} nuevos PDFs...\n")

        indexed_count = 0
        for pdf_path in news_pdfs:
            pass