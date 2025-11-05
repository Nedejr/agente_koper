# ============================================
# Agente Koper - Backend Dockerfile
# Python 3.11 + FastAPI + LangChain + LangGraph
# ============================================

FROM python:3.11-slim

# Metadata
LABEL maintainer="Koper Team"
LABEL description="Agente Koper Backend - RAG Chatbot"

# Previne arquivos .pyc e habilita unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    PYTHONPATH=/app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação para /app/backend
COPY . ./backend

# Cria diretórios necessários
RUN mkdir -p /app/documents /app/logs

# Volta para o diretório raiz
WORKDIR /app

# Expõe porta do FastAPI
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando padrão (pode ser sobrescrito no docker-compose)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

