# 🚀 Guia Rápido - Agente Koper

## ⚡ Start em 3 Passos

```bash
# 1. Clone e entre no diretório
git clone https://github.com/Nedejr/agente_koper.git
cd agente_koper

# 2. Configure (opcional - valores padrão já funcionam)
cp .env.example .env

# 3. Inicie tudo
docker-compose up -d
```

## 📊 Status dos Serviços

Verifique se tudo está rodando:

```bash
docker-compose ps
```

Você deve ver:
- ✅ `agente_koper_qdrant` - healthy
- ✅ `agente_koper_ollama` - healthy
- ✅ `agente_koper_backend` - healthy (pode demorar ~40s)
- ✅ `agente_koper_frontend` - healthy (pode demorar ~60s)
- ✅ `agente_koper_ollama_init` - exited (0) ← Normal!

## ⏱️ Primeira Execução

**Atenção**: Na primeira vez, o sistema precisa baixar o modelo Llama3 (~4.7GB).

Acompanhe o progresso:

```bash
docker logs -f agente_koper_ollama_init
```

Aguarde até ver:
```
✅ Modelo Llama3 instalado com sucesso!
🎉 Sistema pronto para uso!
```

**Tempo estimado**: 5-15 minutos (depende da conexão)

## 🌐 Acessar a Aplicação

Após tudo inicializado:

| Serviço | URL | Descrição |
|---------|-----|-----------|
| 🖥️ **Frontend** | http://localhost:3000 | Interface do chat |
| 📝 **Admin** | http://localhost:3000/admin | Upload de docs |
| 🔌 **API Docs** | http://localhost:8000/docs | Swagger UI |
| 🗄️ **Qdrant** | http://localhost:6333/dashboard | Vector DB |

## 📤 Adicionar Documentos

### Opção 1: Via Interface (Recomendado)

1. Acesse: http://localhost:3000/admin
2. Clique em "Upload Documents"
3. Selecione arquivos (PDF, TXT, MD)
4. Aguarde processamento
5. Teste no chat!

### Opção 2: Via API

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@/caminho/do/arquivo.pdf"
```

## 💬 Testar o Chat

### Via Interface

1. Acesse: http://localhost:3000
2. Digite: "O que é o Koper ERP?"
3. Veja a resposta do agente!

### Via API

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "O que é o Koper ERP?",
    "conversation_id": "test-123"
  }'
```

## 🔍 Verificar Saúde

```bash
# Backend
curl http://localhost:8000/health

# Qdrant
curl http://localhost:6333/healthz

# Ollama
curl http://localhost:11434/api/version
```

## 🛑 Parar Tudo

```bash
# Parar serviços (mantém dados)
docker-compose down

# Parar e limpar TUDO (incluindo dados)
docker-compose down -v
```

## 🐛 Problemas Comuns

### "Cannot connect to backend"

```bash
# Verificar se backend está rodando
docker logs agente_koper_backend

# Reiniciar backend
docker-compose restart backend
```

### "Ollama model not found"

```bash
# Baixar modelo manualmente
docker exec -it agente_koper_ollama ollama pull llama3
```

### "Permission denied" no Qdrant

```bash
# Ajustar permissões
chmod -R 777 ./data/qdrant
docker-compose restart qdrant
```

### Container ficando lento

O Llama3 usa muita RAM/CPU. Alternativas:

```bash
# 1. Usar modelo menor (edite .env):
OLLAMA_MODEL=llama3:8b-instruct-q4_0

# 2. Aumentar recursos do Docker:
# Docker Desktop → Settings → Resources → Aumentar RAM para 8GB+
```

## 📚 Próximos Passos

Agora que está rodando:

1. ✅ Adicione documentos do Koper ERP
2. ✅ Teste diferentes perguntas
3. ✅ Ajuste configurações no `.env`
4. ✅ Explore a API em http://localhost:8000/docs
5. ✅ Leia o README.md completo

## 💡 Dicas Rápidas

**Logs em tempo real**:
```bash
docker-compose logs -f
```

**Rebuild após mudanças**:
```bash
docker-compose up -d --build
```

**Shell no backend**:
```bash
docker exec -it agente_koper_backend bash
```

**Testar Ollama diretamente**:
```bash
docker exec -it agente_koper_ollama ollama run llama3
```

## 🎯 Comandos Essenciais

```bash
# Ver status
docker-compose ps

# Ver logs
docker-compose logs -f [serviço]

# Reiniciar serviço
docker-compose restart [serviço]

# Parar tudo
docker-compose down

# Iniciar tudo
docker-compose up -d

# Rebuild
docker-compose up -d --build

# Limpar volumes
docker-compose down -v
```

---

**Pronto! 🎉 Seu Agente Koper está rodando!**

Para mais detalhes, veja o [README.md](README.md) completo.

