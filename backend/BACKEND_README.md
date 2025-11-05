# 🔧 Backend - Agente Koper

Backend do sistema de chatbot RAG para Koper ERP.

## 📁 Estrutura

```
backend/
├── api/                    # FastAPI Routes
│   ├── health.py          # Health checks
│   ├── chat.py            # Endpoints de chat
│   └── documents.py       # Gestão de documentos
│
├── agent/                 # LangGraph Agent (FASE 4)
│   ├── graph.py          # Definição do grafo
│   ├── nodes.py          # Nós do agente
│   ├── router.py         # Lógica de roteamento
│   └── state.py          # Estado do agente
│
├── rag/                   # Sistema RAG
│   ├── embeddings.py     # Geração de embeddings
│   ├── retriever.py      # Busca no vector store (FASE 3)
│   ├── document_processor.py  # Processamento (FASE 3)
│   └── vector_store.py   # Cliente Qdrant
│
├── llm/                   # LLM Integration
│   ├── ollama_client.py  # Cliente Ollama
│   └── prompts.py        # Templates de prompts
│
├── models/                # Pydantic Models
│   ├── chat.py           # Modelos de chat
│   └── document.py       # Modelos de documentos
│
├── utils/                 # Utilities
│   └── logger.py         # Configuração de logs
│
├── config.py             # Configurações
├── main.py               # Entry point FastAPI
├── Dockerfile            # Docker image
└── requirements.txt      # Dependências Python
```

## 🚀 Desenvolvimento Local

### Instalar dependências

```bash
cd backend
pip install -r requirements.txt
```

### Rodar aplicação

```bash
# Com reload (desenvolvimento)
python main.py

# Ou com uvicorn diretamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Acessar documentação

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testar Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

### Chat

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "O que é o Koper ERP?",
    "conversation_id": "test-123"
  }'
```

### Upload Documento

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@/path/to/document.pdf"
```

## 🔧 Configuração

Variáveis de ambiente principais (ver `.env`):

```bash
# Ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# RAG
CHUNK_SIZE=1000
TOP_K_RESULTS=5
```

## 📝 Logs

Logs são exibidos no console e (em produção) salvos em:
- `/app/logs/app.log` - Todos os logs
- `/app/logs/errors.log` - Apenas erros

Nível de log configurável via `LOG_LEVEL` (DEBUG, INFO, WARNING, ERROR).

## 🤖 Próximas Fases

- **FASE 3**: Implementar processamento de documentos e RAG completo
- **FASE 4**: Implementar agente LangGraph com todos os nós
- **FASE 5+**: Frontend Next.js

## 🐛 Debug

Ver logs em tempo real:

```bash
# Docker
docker logs -f agente_koper_backend

# Local
tail -f /app/logs/app.log
```

## 📚 Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [LangChain Docs](https://python.langchain.com/)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [Ollama Docs](https://ollama.ai/docs)

