# Solução para Erro "readonly database" no ChromaDB

## Problema

```
Erro ao processar documentos: Query error: Database error: error returned from database: (code: 1032) attempt to write a readonly database
```

## Causas Comuns

1. **Permissões incorretas** no diretório `db/`
2. **Banco de dados corrompido** devido a interrupção durante escrita
3. **Problemas no Docker** com volumes montados
4. **Conflito entre múltiplas instâncias** acessando o mesmo banco

## Soluções Implementadas

### 1. Melhorias Automáticas no Código

O código foi atualizado com as seguintes melhorias:

- ✅ **Verificação automática de permissões** ao carregar o banco
- ✅ **Detecção e remoção** de bancos corrompidos
- ✅ **Recriação automática** do banco em caso de erro
- ✅ **Validação** após criação/adição de documentos
- ✅ **Tratamento robusto de erros** com mensagens claras

### 2. Script de Diagnóstico

Use o script `fix_db_permissions.py` para diagnosticar e corrigir problemas:

```bash
# Execute o script
python fix_db_permissions.py
```

O script oferece as seguintes opções:

1. **Verificar permissões** - Mostra informações detalhadas sobre o diretório
2. **Corrigir permissões** - Ajusta automaticamente as permissões
3. **Testar banco** - Valida se o banco está funcionando
4. **Remover e recriar** - Remove completamente o banco (⚠️ perde dados!)

### 3. Soluções Rápidas

#### Opção A: Remover o banco manualmente (perde dados)

```bash
rm -rf db/
```

Depois, reinicie a aplicação e faça upload dos documentos novamente.

#### Opção B: Corrigir permissões manualmente

```bash
# Ajusta permissões do diretório e arquivos
chmod -R u+rwX db/
chmod -R go+rX db/
```

#### Opção C: No Docker

Se estiver usando Docker, recrie o container:

```bash
# Para e remove o container
docker-compose down

# Remove o volume (opcional, perde dados)
docker volume rm agente_koper_db_data

# Recria o container
docker-compose up -d
```

## Prevenção

### Boas Práticas

1. **Não interrompa a aplicação** durante processamento de documentos
2. **Use apenas uma instância** da aplicação por vez
3. **Faça backups** do diretório `db/` regularmente
4. **No Docker**, use volumes nomeados ao invés de bind mounts

### Backup Regular

Crie backups do banco de dados:

```bash
# Backup manual
tar -czf db_backup_$(date +%Y%m%d_%H%M%S).tar.gz db/

# Ou copie o diretório
cp -r db/ db_backup/
```

## Verificação de Funcionamento

Após aplicar as correções, teste a aplicação:

1. Inicie a aplicação
2. Faça upload de um documento de teste
3. Verifique se não há erros no console
4. Tente fazer uma pergunta sobre o documento

## Logs e Monitoramento

O código agora exibe mensagens claras sobre o status do banco:

- ✅ **"Vector store válido com X documentos"** - Banco funcionando
- ⚠️ **"Banco de dados corrompido"** - Banco será recriado
- 🔄 **"Removendo banco corrompido"** - Limpeza automática
- ❌ **"Erro ao criar vector store"** - Problema crítico

## Suporte Adicional

Se o problema persistir após todas as tentativas:

1. Verifique os logs completos da aplicação
2. Confirme que a variável `PERSIST_DIR` está corretamente configurada
3. Verifique se há espaço em disco suficiente
4. Confirme que não há múltiplas instâncias rodando simultaneamente
5. No Docker, verifique o mapeamento de volumes no `docker-compose.yml`

## Observações Técnicas

### ChromaDB e SQLite

O ChromaDB usa SQLite internamente. O erro "readonly database" geralmente indica:

- Arquivo `.sqlite3` com permissões inadequadas
- Arquivo de lock (`.sqlite3-wal` ou `.sqlite3-shm`) travado
- Problema no sistema de arquivos (especialmente em ambientes virtualizados)

### Estrutura do Banco

O diretório `db/` contém:

```
db/
├── chroma.sqlite3          # Banco de dados principal
├── chroma.sqlite3-wal      # Write-Ahead Log
├── chroma.sqlite3-shm      # Shared Memory
└── [uuid]/                 # Dados das embeddings
```

Todos esses arquivos precisam ter permissões de leitura/escrita.
