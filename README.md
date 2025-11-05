# 🤖 Agente Koper - Chatbot RAG com LangGraph

Sistema inteligente de atendimento usando **Retrieval-Augmented Generation (RAG)** para responder dúvidas sobre o **Koper ERP**. Construído com **LangChain**, **LangGraph**, **Streamlit**, e **OpenRouter** com múltiplos modelos gratuitos.

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCKER COMPOSE                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │  Streamlit   │   │   FastAPI    │   │   Qdrant     │    │
│  │  Frontend    │──▶│   Backend    │──▶│ Vector Store │    │
│  │  (Port 8501) │   │  (Port 8000) │   │  (Port 6333) │    │
│  └──────────────┘   └──────┬───────┘   └──────────────┘    │
│                             │                                 │
│                             ▼                                 │
│                     ┌──────────────┐                         │
│                     │  OpenRouter  │                         │
│                     │  Cloud API   │                         │
│                     │ (6 modelos)  │                         │
│                     └──────────────┘                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1️⃣ Clone o repositório

```bash
git clone https://github.com/Nedejr/agente_koper.git
cd agente_koper
```

### 2️⃣ Configure as variáveis de ambiente

```bash
cp .env.example .env
```

**IMPORTANTE**: Edite o arquivo `.env` e adicione sua chave da OpenRouter:

1. Acesse [https://openrouter.ai/keys](https://openrouter.ai/keys)
2. Crie uma conta (gratuita)
3. Gere uma API key
4. Adicione no `.env`: `OPENROUTER_API_KEY=sua_chave_aqui`

### 3️⃣ Inicie todos os serviços com Docker

```bash
docker-compose up -d
```

**Nota**: Na primeira execução, o Ollama irá baixar o modelo Llama3 (~4.7GB). Isso pode levar alguns minutos dependendo da sua conexão.

### 4️⃣ Acompanhe o download do modelo

```bash
docker logs -f agente_koper_ollama_init
```

Aguarde até ver: ✅ **"Modelo Llama3 instalado com sucesso!"**

### 5️⃣ Acesse a aplicação

- 🖥️ **Frontend (Streamlit)**: http://localhost:8501
- 🔌 **Backend API**: http://localhost:8000/docs
- 🗄️ **Qdrant Dashboard**: http://localhost:6333/dashboard

---

## 📁 Estrutura do Projeto

```
agente_koper/
├── docker-compose.yml          # Orquestração de serviços
├── .env.example               # Template de variáveis
├── .dockerignore              # Otimização de builds
│
├── frontend/                  # Streamlit Application
│   ├── streamlit_app.py      # Direct integration
│   └── streamlit_app_api_client.py  # API client mode
│
├── backend/                   # FastAPI Backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py               # Entry point
│   ├── config.py             # Configurações
│   ├── api/                  # Routes
│   ├── agent/                # LangGraph Agent
│   │   ├── graph.py          # Definição do grafo
│   │   ├── nodes.py          # Nós do agente
│   │   ├── router.py         # Lógica de roteamento
│   │   └── state.py          # Estado do agente
│   ├── rag/                  # Sistema RAG
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   ├── document_processor.py
│   │   └── vector_store.py
│   └── llm/                  # Interface com LLMs
│       ├── ollama_client.py
│       └── prompts.py
│
├── data/                      # Volumes (criado automaticamente)
│   ├── documents/            # Documentos do Koper ERP
│   ├── qdrant/               # Vector store data
│   └── ollama/               # Modelos LLM
│
└── tests/                     # Testes
    ├── unit/
    └── integration/
```

---

## 🤖 Como Funciona o Agente

O agente usa **LangGraph** para criar um fluxo inteligente de decisões:

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  CLASSIFIER     │  ← É sobre Koper ERP?
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
   Sim       Não
    │         │
    │         ▼
    │  ┌─────────────────┐
    │  │  OFF_TOPIC      │
    │  │  "Não é meu     │
    │  │   propósito"    │
    │  └─────────────────┘
    │
    ▼
┌─────────────────┐
│  RAG_SEARCH     │  ← Busca no Qdrant
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  EVALUATOR      │  ← Avalia qualidade
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
  Alta     Baixa
 Confiança  Confiança
    │         │
    │         ▼
    │  ┌─────────────────┐
    │  │  HUMAN_HANDOFF  │
    │  │  "Fale com      │
    │  │   atendente"    │
    │  └─────────────────┘
    │
    ▼
┌─────────────────┐
│ GENERATE_ANSWER │  ← Resposta baseada no RAG
└─────────────────┘
```

### Comportamentos do Agente:

1. ✅ **Pergunta sobre Koper + Informação disponível** → Responde com base no RAG
2. ❌ **Pergunta sobre Koper + Sem informação** → Direciona para humano
3. 🚫 **Pergunta fora do escopo** → Informa limitação educadamente

---

## 🛠️ Comandos Úteis

### Gerenciar serviços

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs de todos os serviços
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f backend
docker-compose logs -f frontend

# Parar todos os serviços
docker-compose down

# Parar e remover volumes (limpa dados)
docker-compose down -v

# Rebuild dos containers
docker-compose up -d --build

# Restart de um serviço específico
docker-compose restart backend
```

### Acessar containers

```bash
# Acessar backend
docker exec -it agente_koper_backend bash

# Acessar frontend
docker exec -it agente_koper_frontend bash
```

### Verificar saúde dos serviços

```bash
# Status de todos os containers
docker-compose ps

# Health check do backend
curl http://localhost:8000/health

# Health check do Qdrant
curl http://localhost:6333/healthz
```

---

## 📊 Tecnologias Utilizadas

### Frontend
- **Streamlit** - Python web framework
- **Requests** - HTTP client

### Backend
- **FastAPI** - Web framework
- **LangChain** - RAG framework
- **LangGraph** - Agent orchestration
- **Pydantic** - Data validation

### AI/ML
- **OpenRouter** - Cloud LLM API
- **6 Modelos Gratuitos** - Meta Llama, Google Gemma, Mistral, Qwen, Microsoft Phi-3, Nous Hermes
- **Sentence-Transformers** - Embeddings
- **Qdrant** - Vector database

### DevOps
- **Docker & Docker Compose** - Containerization
- **Python 3.11+** - Backend runtime
- **Node.js 20+** - Frontend runtime

---

## ⚙️ Variáveis de Ambiente

Principais variáveis configuráveis no `.env`:

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `OLLAMA_MODEL` | Modelo LLM a usar | `llama3` |
| `QDRANT_COLLECTION_NAME` | Nome da collection | `koper_knowledge` |
| `CHUNK_SIZE` | Tamanho dos chunks | `1000` |
| `TOP_K_RESULTS` | Documentos retornados | `5` |
| `MIN_SIMILARITY_SCORE` | Score mínimo | `0.7` |
| `CLASSIFIER_THRESHOLD` | Threshold do classificador | `0.6` |
| `LOG_LEVEL` | Nível de log | `INFO` |

Veja `.env.example` para todas as variáveis disponíveis.

---

## 📚 Como Adicionar Documentos

### Via Interface Web (Admin Panel)

1. Acesse: http://localhost:3000/admin
2. Faça upload dos documentos (PDF, TXT, MD)
3. Aguarde processamento
4. Documentos estarão disponíveis para busca

### Via API (cURL)

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@/path/to/manual_koper.pdf"
```

### Via Volume Docker

Coloque documentos em `./data/documents/` e use o endpoint de processamento:

```bash
curl -X POST http://localhost:8000/api/documents/process-all
```

---

## 🧪 Testando o Sistema

### 1. Testar o Ollama

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Hello, how are you?",
  "stream": false
}'
```

### 2. Testar o Backend

```bash
# Health check
curl http://localhost:8000/health

# Chat simples
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "O que é o Koper ERP?",
    "conversation_id": "test-123"
  }'
```

### 3. Testar o Qdrant

```bash
# Ver collections
curl http://localhost:6333/collections

# Ver collection específica
curl http://localhost:6333/collections/koper_knowledge
```

---

## 🐛 Troubleshooting

### Ollama não baixa o modelo

```bash
# Verificar logs
docker logs agente_koper_ollama_init

# Baixar manualmente
docker exec -it agente_koper_ollama ollama pull llama3
```

### Backend não inicia

```bash
# Verificar logs
docker logs agente_koper_backend

# Verificar se Qdrant e Ollama estão rodando
docker-compose ps
```

### Frontend não conecta ao backend

1. Verifique `NEXT_PUBLIC_API_URL` no `.env`
2. Para acesso externo, use: `http://IP_DO_SERVIDOR:8000`

### Qdrant sem permissão

```bash
# Ajustar permissões
chmod -R 777 ./data/qdrant
```

### Container muito lento

O Llama3 é pesado. Considere:
- Usar modelo menor: `llama3:8b-instruct-q4_0`
- Adicionar mais RAM ao Docker
- Usar GPU (descomentar no docker-compose.yml)

---

## 🚀 Próximos Passos

- [ ] Implementar autenticação JWT
- [ ] Adicionar suporte a mais formatos (DOCX, XLSX)
- [ ] Implementar cache de respostas
- [ ] Dashboard de analytics
- [ ] Deploy em produção (Kubernetes)
- [ ] CI/CD pipeline
- [ ] Testes E2E

---

## 📄 Licença

MIT License

---

## 👥 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: nova feature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

---

## 📞 Suporte

Para dúvidas ou problemas:
- 📧 Email: suporte@koper.com.br
- 🐛 Issues: [GitHub Issues](https://github.com/Nedejr/agente_koper/issues)

---

**Desenvolvido com ❤️ para Koper ERP**
