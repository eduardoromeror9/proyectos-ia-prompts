import os
import uuid
from typing import Optional
# pyrefly: ignore [missing-import]
import chromadb
# pyrefly: ignore [missing-import]
from chromadb.utils import embedding_functions
# pyrefly: ignore [missing-import]
from openai import OpenAI
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()


class RAGPipeline:
    """Pipeline RAG completo."""

    def __init__(
        self,
        collection_name: str,
        db_path: str = "./data/chromadb",
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
    ):
        """Inicializa el pipeline RAG con ChromaDB.

        Args:
            collection_name: Nombre de la colección vectorial.
            db_path: Ruta donde ChromaDB persiste sus datos.
            model: Modelo de chat usado para generar respuestas.
            temperature: Control de creatividad de la respuesta (0 = preciso).
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY no está definida en el entorno.")

        self.model = model
        self.temperature = temperature
        self.openai_client = OpenAI()

        self.chroma_client = chromadb.PersistentClient(path=db_path)

        self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name="text-embedding-3-small",
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

        print(
            f"\n✅ Pipeline RAG inicializado, Colección: {collection_name}"
            f"Documentos: {self.collection.count()}"
        )

    def index_texts(self, texts: list[str], metadatas: Optional[list[dict]] = None) -> None:
        """Indexa textos y metadatos en ChromaDB."""
        if not texts:
            return

        # Crear IDs únicos para cada texto
        ids = [f"doc_{uuid.uuid4().hex[:8]}" for _ in texts]
        if metadatas is None:
            metadatas = [{"fuente": "manual"} for _ in texts]

        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
        )

        print(f"✅ Se indexaron {len(texts)} documentos. Total en DB: {self.collection.count()}")

    def index_chunks(
        self,
        long_text: str,
        chunk_size: int = 500,
        overlap: int = 50,
        base_metadata: Optional[dict] = None,
    ) -> int:
        """Divide un texto largo en chunks (en tokens) y los indexa.

        Args:
            long_text: Texto completo a fragmentar.
            chunk_size: Tamaño de cada chunk en tokens (se convierten a
                caracteres estimando ~4 chars/token).
            overlap: Solapamiento entre chunks, también en tokens.
            base_metadata: Metadata base que se copiará a cada chunk.

        Returns:
            Número de chunks indexados.
        """
        if overlap >= chunk_size:
            raise ValueError("'overlap' debe ser menor que 'chunk_size'.")

        chunk_chars_size = chunk_size * 4
        chunks: list[str] = []
        start = 0

        while start < len(long_text):
            end = start + chunk_chars_size
            chunk = long_text[start:end]

            if chunk.strip():
                chunks.append(chunk)

            if end >= len(long_text):
                break

            start = end - (overlap * 4)

        metadatas = []
        for i, _ in enumerate(chunks):
            meta = (base_metadata or {}).copy()
            meta["fuente"] = meta.get("fuente", "manual")
            meta["chunk_numero"] = i
            meta["chunk_total"] = len(chunks)
            metadatas.append(meta)

        self.index_texts(chunks, metadatas)

        return len(chunks)

    def retrieve_context(self, question: str, n_fragments: int = 3, min_similarity: float = 0.3) -> list[dict]:
        """Realiza la búsqueda semántica de documentos relevantes.

        Args:
            question: Pregunta del usuario.
            n_fragments: Máximo de fragmentos a recuperar.
            min_similarity: Similitud mínima (coseno) para aceptar un fragmento.

        Returns:
            Lista de fragmentos con 'texto', 'metadata' y 'similitud'.
        """
        total_documents = self.collection.count()
        if total_documents == 0:
            return []

        results = self.collection.query(
            query_texts=[question],
            n_results=min(n_fragments, total_documents),
            include=["documents", "metadatas", "distances"],
        )

        fragments = []
        retrieved_documents = results["documents"][0]

        for i in range(len(retrieved_documents)):
            similarity = round(max(0.0, min(1.0, 1 - results["distances"][0][i])), 3)

            if similarity >= min_similarity:
                fragments.append({
                    "texto": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similitud": similarity,
                })

        return fragments

    def answer(self, question: str, n_fragments: int = 3, verbose: bool = False) -> dict:
        """Busca contexto y genera una respuesta con IA."""
        # Recuperar contexto relevante
        fragments = self.retrieve_context(question, n_fragments)

        if not fragments:
            return {
                "respuesta": "No encontre informacion relevante en la base de conocimiento.",
                "fragmentos_usados": [],
                "tiene_contexto": False,
            }

        if verbose:
            print(f"\n Fragmentos recuperados para: {question}")
            for fragment in fragments:
                print(f"- Similitud: {fragment['similitud']}")
                print(f"   Texto: {fragment['texto'][:80]}...")

        # Construir contexto
        context_text = "\n\n--\n\n".join(
            f"[Fuente: {fragment['metadata'].get('fuente', 'desconocida')}]\n{fragment['texto']}"
            for fragment in fragments
        )

        # Generar la respuesta con el LLM usando el contexto
        system_prompt = (
            "Eres un asistente experto que responde preguntas basándote ÚNICAMENTE en el contexto proporcionado.\n"
            "Reglas:\n"
            "- Si la respuesta está en el contexto, respóndela directamente y con precisión.\n"
            "- Si el contexto no contiene suficiente información, dilo honestamente.\n"
            "- Cita la fuente cuando sea relevante.\n"
            "- No inventes información que no esté en el contexto.\n"
            "- Responde en el mismo idioma de la pregunta."
        )

        user_prompt = (
            "Contexto disponible:\n"
            f"{context_text}\n"
            f"Pregunta: {question}"
        )

        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
            )
        except Exception as exc:
            raise RuntimeError(f"Error al generar la respuesta con el LLM: {exc}") from exc

        return {
            "respuesta": response.choices[0].message.content,
            "fragmentos_usados": fragments,
            "tokens_usados": response.usage.total_tokens,
            "tiene_contexto": True,
        }


if __name__ == "__main__":

    DOCUMENTS = [
        {
            "texto": "Python fue creado por Guido van Rossum y lanzado en 1991. "
                "Es un lenguaje de programación de alto nivel, interpretado y de propósito general.",
            "metadata": {"fuente": "python_history.txt", "tema": "historia"}
        },
        {
            "texto": "Las listas en Python son colecciones ordenadas y mutables. "
                "Se crean con corchetes: mi_lista = [1, 2, 3]. "
                "Puedes agregar elementos con .append() y eliminar con .remove().",
            "metadata": {"fuente": "python_basics.txt", "tema": "estructuras_datos"}
        },
        {
            "texto": "Los decoradores en Python son funciones que modifican el comportamiento "
                "de otras funciones. Se usan con la sintaxis @nombre_decorador. "
                "Son muy comunes en frameworks como FastAPI y Django.",
            "metadata": {"fuente": "python_advanced.txt", "tema": "avanzado"}
        },
        {
            "texto": "Para manejar errores en Python se usa try/except. "
                "Ejemplo: try: resultado = 10/0 except ZeroDivisionError: print('División por cero'). "
                "También existe finally para código que siempre se ejecuta.",
            "metadata": {"fuente": "python_basics.txt", "tema": "manejo_errores"}
        },
        {
            "texto": "Los virtual environments (entornos virtuales) en Python aislan "
                "las dependencias de cada proyecto. Se crean con: python -m venv .venv "
                "y se activan con: source .venv/bin/activate en Linux/Mac.",
            "metadata": {"fuente": "python_setup.txt", "tema": "configuracion"}
        },
    ]

    print("=" * 60)
    print("RAG Pipeline - Ejemplo")
    print("=" * 60)

    # Iniciar pipeline
    rag = RAGPipeline("python_knowledge_base")

    if rag.collection.count() == 0:
        print("\n Indexando base de conocimientos...")
        texts = [doc["texto"] for doc in DOCUMENTS]
        metas = [doc["metadata"] for doc in DOCUMENTS]
        rag.index_texts(texts, metas)
        print("\n ✅ Base de conocimientos indexada.")

    # Preguntas de prueba
    questions = [
        "Quien creó Python?",
        "Como manejo excepciones en Python?",
        "Para que sirven los decoradores?",
        "Como instalo Django?",
        "Como se crean los entornos virtuales en Python?"
    ]

    print("\n")
    print("=" * 60)
    print("Consultando la base de conocimientos...")
    print("=" * 60)

    for question in questions:
        print(f"\nPregunta: {question}")
        # Consultar el RAG
        result = rag.answer(question, n_fragments=2, verbose=True)

        print("Respuesta:\n")
        print(result["respuesta"])
        print("*** Metricas ***")
        print(f"Tokens utilizados: {result.get('tokens_usados', 'N/A')}")
        print(f"Fragmentos utilizados: {len(result['fragmentos_usados'])}")
        print(f"Tiene contexto: {result['tiene_contexto']}")
