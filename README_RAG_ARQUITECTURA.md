# Sistema RAG Híbrido con Text-to-SQL y Búsqueda Semántica

Arquitectura de IA aplicada para consultar datos privados y actualizados de una organización mediante un asistente conversacional que combina consultas SQL, recuperación semántica con embeddings y control de acceso por usuario u organización.

## Descripción

Este proyecto implementa un sistema **RAG híbrido** orientado a producción. Su objetivo es conectar un modelo de lenguaje con dos tipos de fuentes de información:

- **Datos estructurados**: inventario, precios, facturas, transacciones, stock y métricas operacionales.
- **Datos no estructurados**: manuales, FAQs, documentación, descripciones extensas y conocimiento interno.

La solución enruta cada pregunta hacia el mecanismo de recuperación más adecuado: SQL para exactitud tabular, búsqueda semántica para significado contextual, o una estrategia híbrida cuando la respuesta requiere ambas capas.

## Objetivo

Superar las limitaciones de un LLM preentrenado, que no conoce información privada ni datos recientes de la organización. En lugar de responder solo con conocimiento general, el sistema recupera evidencia desde PostgreSQL y documentos indexados antes de generar una respuesta final fundamentada.

## Casos de uso

- Consultar stock, precios o facturas en lenguaje natural.
- Buscar respuestas dentro de manuales internos o documentación técnica.
- Combinar métricas de negocio con contexto documental.
- Implementar asistentes internos por organización con autenticación.
- Exponer una interfaz tipo chat para usuarios no técnicos.

## Arquitectura general

El siguiente diagrama resume el flujo principal del sistema RAG híbrido, desde la consulta del usuario hasta la generación de una respuesta fundamentada.

```text
+-------------------------------------------------------------------+
|                    USUARIO (Chat Interface)                       |
+-------------------------------------------------------------------+
                                |
                                v
+-------------------------------------------------------------------+
|              1. Clasificador de Intención (LLM)                   |
|           Decide: SQL, Semántico o Híbrido                        |
+-------------------------------------------------------------------+
                                |
                +---------------+---------------+
                |               |               |
                v               v               v
+--------------------+ +--------------------+ +--------------------+
| 2a. SQL Engine     | | 2b. Vector Search  | | 2c. Hybrid Merge   |
|    (Text-to-SQL)   | |    (pgvector)      | |   (RRF / Rerank)   |
+--------------------+ +--------------------+ +--------------------+
                \               |               /
                 \              |              /
                  +-------------+-------------+
                                |
                                v
+-------------------------------------------------------------------+
|              3. Generación (LLM con contexto)                     |
|           Temperatura 0, grounding estricto                       |
+-------------------------------------------------------------------+
                                |
                                v
+-------------------------------------------------------------------+
|                    RESPUESTA AL USUARIO                           |
+-------------------------------------------------------------------+
```

## Arquitectura

```text
Usuario
  │
  ▼
Frontend tipo chat
  │
  ▼
API / Orquestador
  │
  ├── Autenticación y autorización
  ├── Clasificador de intención
  ├── Guardrails de seguridad
  └── Router de consultas
          │
          ├── SQL path  ─────► PostgreSQL
          ├── Semantic path ─► PostgreSQL + pgvector
          └── Hybrid path ───► fusión de resultados
                                │
                                ▼
                           LLM Gateway
                                │
                                ▼
                       Respuesta fundamentada
```

### Componentes principales

| Componente | Responsabilidad |
|---|---|
| Frontend | Chat con el usuario, carga de archivos y visualización de respuestas |
| API Backend | Orquestación, validación, recuperación y generación |
| PostgreSQL | Datos estructurados y metadatos |
| pgvector | Almacenamiento y búsqueda de embeddings |
| LLM Gateway | Acceso unificado a modelos y embeddings |
| Auth Layer | Aislamiento por usuario, tenant u organización |

PostgreSQL con pgvector permite combinar búsqueda vectorial, filtros estructurados y búsqueda full-text dentro de la misma base, reduciendo complejidad operativa frente a arquitecturas con múltiples motores separados.

## Decisiones de diseño

### 1. SQL para verdad estructurada

Las preguntas sobre stock, precios, rangos de fechas, agregaciones o estados transaccionales deben resolverse con SQL, porque requieren precisión, filtros explícitos y resultados auditables.

Ejemplos:

- "¿Cuánto stock queda del SKU-123?"
- "¿Qué facturas vencen esta semana?"
- "¿Cuál fue la venta total del mes pasado?"

### 2. Búsqueda semántica para conocimiento descriptivo

Las preguntas abiertas, explicativas o basadas en intención se resuelven mejor con embeddings y similarity search, especialmente cuando el conocimiento vive en manuales, artículos internos o FAQs.

Ejemplos:

- "¿Cómo se configura la autenticación?"
- "Recomiéndame algo para dolor de espalda"
- "¿Qué política aplica para devoluciones complejas?"

### 3. Ruta híbrida para preguntas reales de negocio

Muchas preguntas empresariales mezclan datos estructurados con contexto narrativo. En esos casos, el sistema debe ejecutar múltiples recuperaciones y luego sintetizar una respuesta.

Ejemplos:

- "¿Por qué bajó el stock de este producto y qué dicen los reportes internos?"
- "¿Cuál es la tasa de retención actual y qué causas aparecen en soporte?"

## Stack tecnológico sugerido

- **Backend**: FastAPI o funciones serverless.
- **Base de datos**: PostgreSQL.
- **Vector store**: pgvector sobre PostgreSQL.
- **Model Gateway**: OpenRouter para chat, embeddings y rerank cuando aplique.
- **Autenticación**: JWT o auth del proveedor BaaS.
- **Ingesta**: loaders para Markdown, PDF y texto plano.
- **Embeddings**: un único modelo consistente para indexación y consulta.
- **Editor**: Cursor o VS Code.
- **Infraestructura**: despliegue en nube con variables de entorno y observabilidad.

## Flujo end-to-end

### Paso 1. Ingesta documental

Los documentos se extraen, limpian y transforman en texto. Luego se fragmentan en chunks con overlap para preservar contexto entre segmentos cercanos antes de generar embeddings.

### Paso 2. Generación de embeddings

Cada chunk se convierte en un vector numérico usando un modelo de embeddings. Ese vector captura similitud semántica y se almacena en PostgreSQL con metadatos como `source`, `org_id`, `user_id` o `document_type`.

### Paso 3. Clasificación de intención

Cuando llega una pregunta, el orquestador decide si debe usar:

- `sql`
- `semantic`
- `hybrid`

Este paso evita usar vector search para preguntas que deberían resolverse con exactitud tabular y evita usar SQL para preguntas vagas o explicativas.

### Paso 4. Recuperación

Según la intención:

- **SQL path**: genera o selecciona una consulta SQL segura.
- **Semantic path**: calcula el embedding de la pregunta y busca similitud por vector.
- **Hybrid path**: recupera desde ambas capas y fusiona evidencia.

### Paso 5. Reranking y selección final

Cuando se recuperan múltiples documentos, conviene rerankear para dejar solo los fragmentos más útiles en el prompt final. OpenRouter documenta un flujo RAG con embeddings y rerank para mejorar la calidad del grounding.

### Paso 6. Generación con grounding

El LLM recibe únicamente el contexto recuperado y responde con temperatura baja o cero, priorizando precisión y consistencia. La respuesta final debe fundamentarse en la evidencia recuperada y declarar falta de información cuando el contexto no sea suficiente.

## Estructura de proyecto sugerida

```text
rag-hibrido/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   └── dependencies/
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── db/
│   │   ├── models.py
│   │   ├── session.py
│   │   └── migrations/
│   ├── services/
│   │   ├── ingest/
│   │   ├── embeddings/
│   │   ├── retrieval/
│   │   ├── text_to_sql/
│   │   ├── llm/
│   │   └── auth/
│   ├── schemas/
│   └── main.py
├── scripts/
│   ├── ingest_documents.py
│   └── rebuild_embeddings.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── evals/
├── .env.example
├── requirements.txt
└── README.md
```

## Modelo de datos mínimo

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}'::jsonb,
    org_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE inventory (
    id BIGSERIAL PRIMARY KEY,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    stock INTEGER NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    org_id UUID NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Seguridad

La capa de seguridad no debe depender solo del prompt. Un sistema Text-to-SQL productivo necesita defensa en profundidad.

### Guardrails recomendados

- Permitir únicamente consultas `SELECT`.
- Usar un rol de base de datos **solo lectura**.
- Aplicar allowlist de esquemas y tablas.
- Forzar `LIMIT` máximo en respuestas tabulares.
- Configurar timeout de consulta.
- Parametrizar filtros cuando corresponda.
- Registrar auditoría de consultas generadas.
- Validar aislamiento por `org_id` o `user_id` en cada consulta.

### Riesgos a mitigar

- SQL injection inducido por prompt.
- Exfiltración de datos entre tenants.
- Uso del LLM sin grounding suficiente.
- Respuestas basadas en chunks irrelevantes.
- Mezcla de modelos de embeddings entre indexación y consulta, lo que degrada la similitud semántica.

## Buenas prácticas de recuperación

### Chunking

Un tamaño inicial razonable es 200 a 500 tokens con overlap moderado, aunque el valor óptimo depende del tipo de documento y de su estructura. Los documentos técnicos suelen beneficiarse de chunks alineados con secciones o encabezados más que de un corte estrictamente fijo.

### Estrategia híbrida de búsqueda

Antes de introducir un reranker complejo, una estrategia práctica es combinar:

- full-text search
- filtros SQL
- búsqueda vectorial con pgvector

Este enfoque mejora consultas cortas, nombres propios, IDs o términos exactos que a veces no se resuelven bien con embeddings solamente.

### Política de respuesta

El sistema debe tener una política explícita de "no sé" cuando no encuentre suficiente evidencia. Temperatura 0 ayuda a la consistencia, pero no sustituye un diseño correcto de recuperación ni un buen control de relevancia.

## Instalación local

### Requisitos

- Python 3.12+
- PostgreSQL 15+
- pgvector
- `.venv`
- Variables de entorno para base de datos y gateway LLM

### Setup rápido

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Variables de entorno esperadas

```env
DATABASE_URL=postgresql://user:password@localhost:5432/rag
OPENROUTER_API_KEY=your_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
APP_ENV=development
JWT_SECRET=change_me
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=openai/gpt-4o-mini
```

## Pipeline de ejecución

```text
1. Cargar documentos
2. Limpiar y fragmentar
3. Generar embeddings
4. Indexar en PostgreSQL + pgvector
5. Recibir pregunta del usuario
6. Autenticar usuario
7. Clasificar intención
8. Recuperar contexto (SQL / semantic / hybrid)
9. Rerankear si aplica
10. Construir prompt final
11. Generar respuesta fundamentada
12. Registrar métricas, latencia y trazas
```

## Evaluación

Un sistema RAG no debe validarse solo con demos visuales. Debe medirse con conjuntos de preguntas reales del negocio.

### Métricas sugeridas

- **Routing accuracy**: porcentaje de preguntas enviadas a la ruta correcta.
- **Retrieval relevance**: relevancia de los chunks o filas recuperadas.
- **Answer groundedness**: grado en que la respuesta está soportada por evidencia.
- **Latency**: tiempo total de respuesta por tipo de consulta.
- **Tenant isolation**: pruebas negativas para confirmar que un usuario no accede a datos de otro tenant.
- **SQL safety pass rate**: porcentaje de consultas aprobadas por validación sin riesgo.

## Roadmap

### Fase 1

- Ingesta básica de Markdown y PDF.
- Embeddings y búsqueda vectorial en pgvector.
- Text-to-SQL con reglas simples.
- Chat autenticado por organización.

### Fase 2

- Router con clasificación `sql / semantic / hybrid`.
- Reranking.
- Observabilidad y tracing.
- Evals automáticas.

### Fase 3

- Cache de respuestas y embeddings.
- Enrutado por complejidad hacia distintos modelos.
- Memoria conversacional por sesión.
- Citado de fuentes en la respuesta final.

## Errores comunes

| Error | Impacto | Corrección |
|---|---|---|
| Usar embeddings para preguntas tabulares | Respuestas imprecisas | Enrutar a SQL |
| Usar SQL para consultas semánticas | Mala experiencia en lenguaje natural | Enrutar a vector search |
| No filtrar por tenant | Riesgo crítico de seguridad | Aplicar `org_id` en todas las capas |
| Sin rol read-only | Riesgo de modificación de datos | Crear usuario de solo lectura |
| Chunking fijo sin criterio documental | Baja relevancia | Ajustar chunking por tipo de contenido |
| Sin evaluación | Falsa sensación de calidad | Crear dataset de preguntas reales |

## Principios de producción

- La recuperación manda; el LLM sintetiza.
- SQL resuelve exactitud, vector search resuelve significado.
- La seguridad se implementa en código, base de datos y prompts.
- Multi-tenant implica filtrado estricto por identidad y organización.
- La calidad del sistema depende más del retrieval que del modelo más caro.

## Próximos pasos sugeridos

1. Implementar el esquema base en PostgreSQL.
2. Cargar 20 a 50 documentos reales.
3. Crear 30 preguntas de negocio representativas.
4. Medir cuántas deben ir a SQL, cuántas a semántica y cuántas a híbrido.
5. Construir una primera API con FastAPI.
6. Añadir evaluaciones antes de pasar a producción.

## Fuentes usadas para el diseño

- SQL for RAG (pgvector + full-text + filtros estructurados).
- OpenRouter cookbook para RAG con embeddings y rerank.
