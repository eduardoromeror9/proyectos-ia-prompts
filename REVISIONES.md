# Revisión técnica del proyecto

> Documento vivo de las revisiones del código `src/` y `data/`, las mejoras implementadas y las pendientes.
> Última actualización: 2026-08-03

## 1. Contexto y alcance

El proyecto es un repositorio de aprendizaje/demos de "Python IA Aplicada" (técnicas de prompting, function calling, RAG con ChromaDB y un chatbot CLI). Se revisó, prioritariamente, `src/` y `data/` para detectar mejoras de robustez, mantenibilidad y arquitectura.

Existe una brecha importante entre el `README.md` (arquitectura RAG híbrida con PostgreSQL/pgvector/FastAPI) y el código real (demos). Se recomienda, cuando se tome rumbo, separar `demos/` de `app/` o reescribir el README.

## 2. Hallazgos iniciales

| # | Severidad | Problema |
|---|-----------|----------|
| 1 | Crítico | `weather["temperature"]` → `KeyError` si la ciudad no existe (`function_calling.py`) |
| 2 | Alto | Los artefactos de ChromaDB se comitearían con `git add .` (sin ignorar) |
| 3 | Alto | Errores de red/API sin manejar ni timeout en los `*_service.py` |
| 4 | Alto | Modelo hardcodeado en 6+ lugares, ignorando `OPENAI_MODEL` del `.env` |
| 5 | Alto | `data/` no quedaba claro qué debía versionarse y qué no |
| 6 | Medio | `raise` inalcanzables (código muerto) en `hello_error_managment.py` |
| 7 | Medio | `json.loads(response_extractor)` sin manejo si la API devuelve JSON inválido |
| 8 | Medio | Cliente OpenAI duplicado en 6 archivos en vez de centralizarse en `ia_client.py` |
| 9 | Medio | Historial del chatbot crece sin límite (ventana de contexto) |
| 10 | Medio | `count_approximate_tokens` cuenta caracteres, no tokens (`contex_problem.py`) |
| 11 | Media/Baja | `embeddings_demo.py` genera embeddings de a uno (debería ser batch) y tiene un import erróneo (`from http import client`) |
| 12 | Baja | Sin tests, sin CI, sin `pyproject.toml`; `requirements.txt` es un `pip freeze` completo |

## 3. Mejoras implementadas

### 3.1 Ingesta del conocimiento desde `data/documents/` (RAG)

`chromadb_demo.py` tenía 6 documentos hardcodeados en `KNOWLEDGE_BASE`. Ahora el conocimiento vive en archivos fuente `data/documents/*.md` y se ingiere con `load_documents()`:

- `_split_sections()` divide cada archivo por encabezados `##` (omite el título `#`).
- `_chunk_text()` fragmenta secciones largas en chunks de `CHUNK_SIZE` (800) con `CHUNK_OVERLAP` (100).
- Cada chunk lleva metadata `fuente` y `seccion`.
- `DATA_DIR` se deriva de `__file__` (independiente del CWD).

### 3.2 Espacio de métrica coseno (búsqueda semántica correcta)

La colección se creaba con la distancia por defecto de ChromaDB (`l2`), pero el código interpretaba `1 - distance` como similitud coseno. Ahora:

- `metadata={"hnsw:space": "cosine", "description": ...}` al crear la colección.
- Similitud clampeada a `[0, 1]` en `search_similar`.

> Nota: si existía una colección previa con `l2`, debe recrearse (borrar `data/chromadb/`) porque la metadata no se actualiza en una colección existente.

### 3.3 Reintento con backoff exponencial en el cliente OpenAI

`ia_client.py` fallaba ante errores transitorios (`429`, `5xx/503`, timeouts, red). Se agregó una política de reintento con `tenacity`:

- Hasta 5 intentos con backoff exponencial (`2s → 4s → 8s → 16s → 60s`).
- `reraise=True` relanza el error original si se agotan los intentos.
- No reintenta errores permanentes (`AuthenticationError`, `BadRequestError`).

### 3.4 Git y datos

- `.gitignore` ignora `data/chromadb/` y `data/private/`, pero **versiona** `data/documents/*.md` (el conocimiento del RAG).
- Se eliminó una línea `EOF` suelta al final del archivo.

## 4. Mejoras pendientes (priorizadas)

1. **Corregir `KeyError` en `function_calling.py`** (validar `weather` antes de `weather["temperature"]`).
2. **Centralizar la configuración** en un `config.py` (pydantic-settings): `OPENAI_MODEL`, `MAX_TOKENS`, timeouts; dejar de hardcodear el modelo.
3. **Centralizar el tráfico LLM** en `ia_client.py` (eliminar los 6 clientes duplicados) con logging y type hints `str | None`.
4. **Agregar timeouts y verificación de `status_code`** en `weather_service.py` y `news_service.py`.
5. **Quitar el código muerto** (`raise` inalcanzables) en `hello_error_managment.py`.
6. **Limitar el historial** del chatbot (`chatbot_cli.py`) para no exceder la ventana de contexto.
7. **Batch de embeddings** en `embeddings_demo.py` y uso de `numpy`.
8. **Validar entrada** en `add_documents` (esquema/IDs únicos).
9. **Chunker por tokens** (p. ej. `tiktoken`) en vez de caracteres cuando los documentos crezcan.
10. **Empaquetar**: `pyproject.toml` con deps directas (separando dev), primeros tests y CI.

## 5. Notas de operación

- Ejecutar la demo RAG:
  ```bash
  .venv/bin/python src/rag/chromadb_demo.py
  ```
- Si la base cambia de esquema (metadata/espacio), borrar `data/chromadb/` para recrearla.
- **Dependencias agregadas** relevantes para las mejoras: `tenacity`, `chromadb`, `pydantic-settings`.