"""Demo for ChromaDB vector database."""
import os
from pathlib import Path

import chromadb  # type: ignore
from chromadb.utils import embedding_functions  # type: ignore
from dotenv import load_dotenv  # type: ignore

load_dotenv()

# Directorio raíz de datos del proyecto (independiente del CWD).
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
CHROMA_DIR = DATA_DIR / "chromadb"

# Tamaño máximo de chunk (en caracteres) y solapamiento entre chunks.
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def create_chroma_client(persist: bool = True):
    """Create a ChromaDB client"""
    if persist:
        return chromadb.PersistentClient(path=str(CHROMA_DIR))
    else:
        return chromadb.EphemeralClient()


def create_collection(client, name: str):
    """Create a collection in ChromaDB"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY no está definida en el entorno.")

    openai_em = embedding_functions.OpenAIEmbeddingFunction(
        api_key=api_key,
        model_name="text-embedding-3-small"
    )

    collection = client.get_or_create_collection(
        name=name,
        embedding_function=openai_em,
        metadata={
            "hnsw:space": "cosine",
            "description": "Base de conocimientos para el asistente de IA.",
        }
    )

    return collection


def _split_sections(text: str) -> list[tuple[str, str]]:
    """Divide un documento en secciones usando los encabezados '##'."""
    sections: list[tuple[str, str]] = []
    current_heading = ""
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_lines:
                sections.append((current_heading, "\n".join(current_lines).strip()))
            current_heading = line[3:].strip()
            current_lines = []
        elif line.startswith("# "):
            # Título del documento: no es contenido indexable.
            continue
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_heading, "\n".join(current_lines).strip()))

    return [(heading, content) for heading, content in sections if content]


def _chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Divide un texto en chunks de tamaño máximo con solapamiento."""
    if len(text) <= size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def load_documents(directory: Path = DOCUMENTS_DIR) -> list[dict]:
    """Carga los documentos fuente desde archivos Markdown y los fragmenta.

    Cada sección ('##') de cada archivo se convierte en uno o más chunks,
    cada uno con su metadata (fuente y sección).
    """
    files = sorted(directory.glob("*.md"))
    if not files:
        raise FileNotFoundError(f"No se encontraron archivos .md en {directory}")

    documents: list[dict] = []
    for file in files:
        text = file.read_text(encoding="utf-8")
        for section_heading, section_text in _split_sections(text):
            for i, chunk in enumerate(_chunk_text(section_text), start=1):
                documents.append({
                    "id": f"{file.stem}_{len(documents) + 1:03d}",
                    "texto": chunk,
                    "metadata": {
                        "fuente": file.name,
                        "seccion": section_heading,
                    },
                })
    return documents


def add_documents(collection, documents: list[dict]) -> None:
    """Add documents to the collection"""
    collection.add(
        ids=[doc["id"] for doc in documents],
        documents=[doc["texto"] for doc in documents],
        metadatas=[doc["metadata"] for doc in documents]
    )

    print(f"OK {len(documents)} documentos agregados a ChromaDB.")


def search_similar(collection, question: str, n_results: int = 3) -> list[dict]:
    """Search for similar documents in the collection"""

    results = collection.query(
        query_texts=[question],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    if not results.get("documents") or not results["documents"][0]:
        return []

    formatted_docs = []
    for i in range(len(results["documents"][0])):
        formatted_docs.append({
            "texto": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "similitud": max(0.0, min(1.0, round(1 - results["distances"][0][i], 3))),
        })

    return formatted_docs


if __name__ == "__main__":
    print("=" * 50)
    print("ChromaDB")
    print("=" * 50)

    # Crear cliente
    client = create_chroma_client(persist=True)
    collection = create_collection(client, name="base_conocimiento_empresas")

    # Ingestar documentos desde data/documents/
    if collection.count() == 0:
        print(f"\nCargando documentos desde {DOCUMENTS_DIR}...")
        documents = load_documents(DOCUMENTS_DIR)
        add_documents(collection, documents)
    else:
        print(f"\nLa colección ya tiene documentos, no se agregaron nuevos. Total documentos: {collection.count()}")

    # Buscar respuestas similares a una pregunta
    test_questions = [
        # "¿Cómo reinicio el servidor web?",
        # "¿Dónde están las credenciales de la base de datos?",
        # "¿Cómo hago deploy a producción?",
        # "¿Qué pasa si hago demasiadas llamadas a la API?",
        "Mi web app dejó de responder",
        "Olvidé dónde guardamos los passwords",
        "Quiero publicar mi código en vivo",
    ]

    print("\n")
    print("=" * 50)
    print("Búsqueda semantica.")

    for question in test_questions:
        print(f"\nPregunta: {question}")
        results = search_similar(collection, question, n_results=2)
        for i, doc in enumerate(results, 1):
            print(
                f"\n#{i} Similitud: {doc['similitud']}:"
                f"\nFuente: {doc['metadata']['fuente']}"
                f"\nSección: {doc['metadata']['seccion']}"
            )

            print(f"Texto: {doc['texto'][:120]}...")  # print first 120 characters of the text