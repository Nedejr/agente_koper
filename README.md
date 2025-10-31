# 🤖 Agente Koper - Chat RAG com PDFs

Sistema de Retrieval-Augmented Generation (RAG) para fazer perguntas sobre documentos PDF usando LangChain e OpenAI.

## ️ Estrutura do Projeto

```
agente_koper/
├── backend/                    # Lógica de negócio
│   ├── config.py              # Configurações centralizadas
│   ├── processing.py          # Processamento de PDFs
│   ├── vector_store.py        # Gerenciamento do ChromaDB
│   └── qa.py                  # Sistema de perguntas e respostas
├── frontend/                   
│   └── streamlit_app.py       # Interface Streamlit
├── backend_api/               # (Opcional) Backend FastAPI
│   └── app.py                 # API REST
├── db/                        # ChromaDB (criado automaticamente)
├── .env                       # Variáveis de ambiente (você cria)
├── .env.example              # Template
└── requirements.txt          # Dependências
```

## 🚀 Instalação e Execução

### 1. Clone o repositório

```bash
git clone <seu-repositorio>
cd agente_koper
```

### 2. Crie e ative o ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure a chave OpenAI

Crie o arquivo `.env` na raiz do projeto:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione sua chave:

```env
OPENAI_API_KEY=sk-sua-chave-aqui
```

### 5. Execute a aplicação

```bash
streamlit run frontend/streamlit_app.py
```

Acesse: **http://localhost:8501**

## 💻 Como Usar

1. **Upload PDF**: Clique em "Browse files" na sidebar e selecione seus PDFs
2. **Processar**: Clique em "🚀 Processar Documentos"
3. **Perguntar**: Digite suas perguntas no chat
4. **Configurar**: Escolha o modelo (GPT-3.5/4o) e ajuste a temperatura

## � Variáveis de Ambiente (.env)

```env
# Obrigatório
OPENAI_API_KEY=sk-sua-chave-aqui

# Opcional
PERSIST_DIR=db              # Diretório do ChromaDB
CHUNK_SIZE=1000            # Tamanho dos chunks
CHUNK_OVERLAP=400          # Overlap entre chunks
TEMPERATURE=0.7            # Criatividade (0-1)
```

## 🎯 Funcionalidades

- ✅ Upload de múltiplos PDFs
- ✅ Processamento e chunking inteligente
- ✅ Busca semântica com ChromaDB
- ✅ Chat com histórico de conversa
- ✅ Múltiplos modelos OpenAI
- ✅ Interface intuitiva

## � Tecnologias Utilizadas

- **Python 3.11+**
- **LangChain** - Framework RAG
- **OpenAI** - Modelos de linguagem
- **ChromaDB** - Banco de dados vetorial
- **Streamlit** - Interface web
- **PyPDF** - Processamento de PDFs

## 📄 Licença

MIT License
